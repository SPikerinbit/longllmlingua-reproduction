"""Stage-three main experiment: pilot/main matrix, coverage, statistics and figures.

The stage-three matrix merges the stage-one baselines (original prompt, BM25 2x/4x)
and the stage-two compressors (LLMLingua / LongLLMLingua 2x/4x) into one run, so
every method is answered and scored by the same code path:

* resumable append-only ``results.jsonl`` keyed by ``slot_id``;
* failures are recorded as rows (never as success) and retried on the next run;
* the 7B compressor is loaded lazily: a resume that only needs cached compressions,
  or a run that only uses original/BM25, never touches the model;
* ``coverage.json`` / ``failures.jsonl`` are rebuilt from the saved rows;
* ``stats`` does paired bootstrap over questions (all five positions kept together);
* ``figures`` rebuilds the main table, position curves and quality-vs-ratio plot.

Entry point: ``python -m reproduction.stage3 <plan|run|summarize|stats|figures|casebook>``.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import time
from collections import defaultdict
from pathlib import Path

from . import common, evaluation

KINDS = ("original", "bm25", "llmlingua", "longllmlingua")
COMPRESSED_KINDS = ("llmlingua", "longllmlingua")
PINNED_LLMLINGUA = "5a4c78ae18ab17a98cf997e8259354e546081d64"
COMPRESSED_FIELDS = ("rank_method", "condition_in_question", "reorder_context")


# --------------------------------------------------------------------------- config

def method_spec(config, name):
    """Return a validated method spec; original has an implicit ratio of 1."""
    try:
        spec = dict(config["methods"][name])
    except KeyError:
        raise ValueError(f"Unknown stage-three method: {name}") from None
    kind = spec.get("kind")
    if kind not in KINDS:
        raise ValueError(f"methods.{name}.kind must be one of {KINDS}")
    if kind == "original":
        spec["ratio"] = 1.0
    else:
        try:
            ratio = float(spec["ratio"])
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"methods.{name}.ratio must be numeric") from None
        if ratio <= 1:
            raise ValueError(f"methods.{name}.ratio must be greater than 1")
        spec["ratio"] = ratio
    if kind == "bm25" and name not in ("bm25_2x", "bm25_4x"):
        raise ValueError("Stage-three BM25 methods must be named bm25_2x / bm25_4x")
    return spec


def load_stage3_config(path=None):
    config = common.read_json(path or common.ROOT / "configs/stage3.json")
    if config.get("stage") != 3:
        raise ValueError("Stage-three config must declare stage=3")
    if config.get("provider") != "deepseek" or config.get("base_url") != "https://api.deepseek.com":
        raise ValueError("Stage three keeps the verified DeepSeek endpoint")
    for key in ("model", "expected_model_version", "api_key_env"):
        if not isinstance(config.get(key), str) or not config[key]:
            raise ValueError(f"Config field {key} must be a non-empty string")
    if config.get("thinking") != {"type": "disabled"}:
        raise ValueError("Thinking must stay disabled for comparability")
    if config.get("temperature") != 0:
        raise ValueError("temperature must stay 0")
    for key in ("max_tokens", "timeout_seconds", "max_attempts", "retry_delay_seconds",
                "max_requests_per_run", "max_context_tokens"):
        if not isinstance(config.get(key), int) or config[key] <= 0:
            raise ValueError(f"Config field {key} must be a positive integer")
    if config.get("split") not in ("smoke", "pilot", "main"):
        raise ValueError("split must be smoke, pilot or main")
    positions = config.get("positions")
    if not isinstance(positions, list) or not positions:
        raise ValueError("positions must be a non-empty list")
    if len(set(positions)) != len(positions) or not set(positions) <= set(common.POSITIONS):
        raise ValueError(f"positions must be unique and drawn from {common.POSITIONS}")
    upstream = config.get("upstream", {})
    if upstream.get("llmlingua") != PINNED_LLMLINGUA:
        raise ValueError("Stage three is pinned to llmlingua commit " + PINNED_LLMLINGUA)

    stage_methods = config.get("methods")
    if not isinstance(stage_methods, dict) or not stage_methods:
        raise ValueError("methods must be a non-empty object")
    kinds = set()
    for name in stage_methods:
        spec = method_spec(config, name)
        kinds.add(spec["kind"])
        if spec["kind"] == "bm25" and not isinstance(config.get("bm25"), dict):
            raise ValueError("bm25 block is required when a BM25 method is configured")
        if spec["kind"] in COMPRESSED_KINDS:
            for key in COMPRESSED_FIELDS:
                if not isinstance(spec.get(key), str) or not spec[key]:
                    raise ValueError(f"methods.{name}.{key} must be a non-empty string")
            for key in ("condition_compare", "use_context_level_filter", "restrict", "recovery"):
                if not isinstance(spec.get(key), bool):
                    raise ValueError(f"methods.{name}.{key} must be a boolean")
            if not isinstance(spec.get("dynamic_context_compression_ratio"), (int, float)):
                raise ValueError(f"methods.{name}.dynamic_context_compression_ratio must be numeric")
    if "original" not in kinds:
        raise ValueError("The original-prompt baseline is mandatory")
    if any(kind in COMPRESSED_KINDS for kind in kinds):
        compressor = config.get("compressor", {})
        for key in ("model_path", "device", "torch_dtype", "attn_implementation",
                    "context_budget", "budget_mode"):
            if not isinstance(compressor.get(key), str) or not compressor[key]:
                raise ValueError(f"compressor.{key} must be a non-empty string")
        if compressor["budget_mode"] not in ("hard", "natural"):
            raise ValueError("compressor.budget_mode must be hard or natural")
        for key in ("iterative_size", "max_budget_passes", "seed"):
            if not isinstance(compressor.get(key), int) or compressor[key] <= 0:
                raise ValueError(f"compressor.{key} must be a positive integer")

    baseline = config.get("baseline")
    if baseline not in stage_methods or method_spec(config, baseline)["kind"] != "original":
        raise ValueError("baseline must name the original-prompt method")
    stats = config.get("statistics", {})
    if not isinstance(stats.get("bootstrap_samples"), int) or stats["bootstrap_samples"] < 1:
        raise ValueError("statistics.bootstrap_samples must be a positive integer")
    if not isinstance(stats.get("seed"), int):
        raise ValueError("statistics.seed must be an integer")
    if not 0 < float(stats.get("confidence", 0)) < 1:
        raise ValueError("statistics.confidence must be in (0, 1)")
    return config


def slot_id(question_id, position, method):
    return f"{question_id}:{position}:{method}"


def expected_slot_ids(meta):
    config = meta["config"]
    return [slot_id(qid, position, method)
            for qid in meta["question_ids"]
            for position in config["positions"]
            for method in config["methods"]]


# --------------------------------------------------------------------------- plan

def plan(config):
    """Offline budget: token counts and slot counts, no model load, no API call."""
    from . import data, methods, runner

    counter = methods.TokenCounter()
    runner.verify_resources(config)
    samples = list(data.iter_samples(config))
    specs = {name: method_spec(config, name) for name in config["methods"]}
    totals = {name: {"slots": 0, "origin_tokens": 0, "target_tokens": 0} for name in specs}
    max_prompt = 0
    for _qid, _position, row in samples:
        sample = data.visible_sample(row)
        origin = counter.count(methods.prompt(sample["question"], sample["documents"]))
        for name, spec in specs.items():
            target = origin if spec["kind"] == "original" else origin // int(spec["ratio"])
            totals[name]["slots"] += 1
            totals[name]["origin_tokens"] += origin
            totals[name]["target_tokens"] += target
            max_prompt = max(max_prompt, target)
    budget = [{"method": name, "kind": specs[name]["kind"], "ratio": specs[name]["ratio"],
               **totals[name]} for name in specs]
    total_slots = sum(item["slots"] for item in budget)
    total_input = sum(item["target_tokens"] for item in budget)
    compressor = config.get("compressor", {})
    report = {
        "stage": 3,
        "split": config["split"],
        "questions": len(samples) // max(len(config["positions"]), 1),
        "positions": config["positions"],
        "methods": list(config["methods"]),
        "slots": total_slots,
        "estimated_api_calls": total_slots,
        "estimated_input_text_tokens": total_input,
        "estimated_output_token_cap": total_slots * config["max_tokens"],
        "max_prompt_tokens": max_prompt,
        "budget": budget,
        "compressor_model": compressor.get("model_name"),
        "compressor_model_path": compressor.get("model_path"),
        "compressor_present": bool(compressor.get("model_path"))
        and Path(compressor["model_path"]).exists(),
        "note": ("Offline estimate only: compressed prompts are budgeted as origin // ratio, "
                 "real API usage and cache hits are recorded per slot."),
    }
    (common.ROOT / "reports").mkdir(exist_ok=True)
    common.atomic_json(common.ROOT / f"reports/{config['split']}-stage3-plan.json", report)
    return report


# --------------------------------------------------------------------------- run

def _build_slot(config, method, sample, counter, compressor, stage2_module):
    """Return the stage-three prompt payload for one method/sample."""
    from . import methods

    spec = method_spec(config, method)
    kind = spec["kind"]
    started = time.perf_counter()
    if kind == "original":
        built = methods.build_prompt(sample, "original", config, counter)
        built.update(budget_satisfied=True, trace=None, ranking=[],
                     truncated_doc_ids=[], compression_seconds=time.perf_counter() - started,
                     compression_cache_hit=False, compression_cache_key=None)
    elif kind == "bm25":
        built = methods.build_prompt(sample, method, config, counter)
        built.update(budget_satisfied=True, trace=None,
                     compression_seconds=time.perf_counter() - started,
                     compression_cache_hit=False, compression_cache_key=None)
    else:
        if compressor is None:
            raise ValueError("Compressor must be loaded before compressing a sample")
        built, hit, cache_key = stage2_module._compress_cached(
            compressor, config, method, sample, counter)
        built.update(compression_cache_hit=hit, compression_cache_key=cache_key)
    built["kind"] = kind
    built["compression_seconds"] = built.get("compression_seconds", 0.0)
    built.setdefault("ranking", [])
    built.setdefault("truncated_doc_ids", [])
    built.setdefault("selected_doc_ids", [])
    return built, spec


def run(config, limit=None):
    from . import api, compression, data, methods, recovery, runner
    from . import stage2 as stage2_module

    key = api.get_key(config)
    runner.verify_resources(config)
    if limit is not None and limit <= 0:
        raise ValueError("--limit must be positive")
    manifest = common.read_json(common.ROOT / f"manifests/{config['split']}.json")
    question_ids = manifest["question_ids"]
    config_hash = common.configuration_hash(config)
    implementation_hash = common.implementation_hash()
    run_id = common.digest({"config": config_hash, "implementation": implementation_hash,
                            "question_ids": question_ids})[:20]
    run_dir = common.ROOT / "outputs/stage3" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    lock = run_dir / ".running"
    if lock.exists():
        raise ValueError(f"Run already active: {run_dir}; remove {lock} only if no process runs")
    lock.write_text("running\n", encoding="utf-8")

    meta = {
        "run_id": run_id, "stage": 3, "split": config["split"],
        "question_ids": question_ids, "manifest": manifest,
        "config": config, "config_hash": config_hash,
        "implementation_hash": implementation_hash,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "upstream": config["upstream"], "tokenizer": config["tokenizer"],
    }
    common.atomic_json(run_dir / "run.json", meta)

    results_path = run_dir / "results.jsonl"
    completed = set()
    if results_path.exists():
        for record in load_records(results_path).values():
            if record["status"] == "success":
                completed.add(record["slot_id"])

    counter = methods.TokenCounter()
    client = None
    compressor = None
    compressor_meta = None
    request_budget = min(limit or config["max_requests_per_run"], config["max_requests_per_run"])
    requests = 0
    written = 0
    try:
        for _qid, position, row in data.iter_samples(config):
            sample = data.visible_sample(row)
            for method in config["methods"]:
                sid = slot_id(_qid, position, method)
                if sid in completed:
                    continue
                if requests >= request_budget:
                    break
                spec = method_spec(config, method)
                started = time.perf_counter()
                try:
                    if spec["kind"] in COMPRESSED_KINDS and compressor is None:
                        compressor, compressor_meta = compression.load_compressor(config, counter)
                        meta["compressor"] = compressor_meta
                        common.atomic_json(run_dir / "run.json", meta)
                    built, spec = _build_slot(config, method, sample, counter,
                                              compressor, stage2_module)
                    prompt = built["prompt"]
                    prompt_tokens = counter.count(prompt)
                    if prompt_tokens > config["max_context_tokens"]:
                        raise ValueError(f"prompt tokens {prompt_tokens} exceed "
                                         f"max_context_tokens {config['max_context_tokens']}")
                    payload = api.request_payload(config, prompt)
                    if client is None:
                        client = api.DeepSeekClient(config, key)
                    saved, hit = api.cached_completion(
                        config, payload, client,
                        provenance={"run_id": run_id, "slot_id": sid, "stage": 3,
                                    "method": method})
                    if not hit:
                        requests += 1
                    answer = saved["result"]["answer"]
                    if spec.get("recovery"):
                        original_prompt = methods.prompt(sample["question"], sample["documents"])
                        recovered, recovery_stats = recovery.recover_answer(
                            original_prompt, prompt, answer, counter)
                    else:
                        recovered = answer
                        recovery_stats = {"changed": False, "enabled": False,
                                          "response_tokens": counter.count(answer),
                                          "recovered_tokens": counter.count(answer)}
                    record = {
                        "slot_id": sid, "question_id": _qid, "position": position,
                        "split": config["split"], "stage": 3, "method": method,
                        "kind": spec["kind"], "question": sample["question"],
                        "answers": row["answers"], "status": "success",
                        "prompt": prompt, "prompt_hash": common.digest(prompt),
                        "prompt_tokens": prompt_tokens,
                        "origin_prompt_tokens": built["origin_tokens"],
                        "target_tokens": built["target_tokens"],
                        "target_ratio": built["target_ratio"],
                        "actual_ratio": built["actual_ratio"],
                        "budget_satisfied": built["budget_satisfied"],
                        "selected_doc_ids": built.get("selected_doc_ids", []),
                        "truncated_doc_ids": built.get("truncated_doc_ids", []),
                        "ranking": built.get("ranking", []),
                        "trace": built.get("trace"),
                        "compression_seconds": built.get("compression_seconds", 0.0),
                        "compression_cache_hit": built.get("compression_cache_hit", False),
                        "compression_cache_key": built.get("compression_cache_key"),
                        "method_version": built.get("method_version"),
                        "answer": answer,
                        "answer_before_recovery": answer,
                        "answer_after_recovery": recovered,
                        "recovery_enabled": bool(spec.get("recovery")),
                        "recovery_stats": recovery_stats,
                        "score_before_recovery": evaluation.score(answer, row["answers"]),
                        "score_after_recovery": evaluation.score(recovered, row["answers"]),
                        "score": evaluation.score(recovered if spec.get("recovery") else answer,
                                                  row["answers"]),
                        "cache_key": saved["cache_key"], "cache_hit": hit,
                        "cache_source_provenance": saved.get("provenance"),
                        "usage": saved["result"].get("usage"),
                        "response_model": saved["result"].get("response_model"),
                        "system_fingerprint": saved["result"].get("system_fingerprint"),
                        "response_id": saved["result"].get("response_id"),
                        "finish_reason": saved["result"].get("finish_reason"),
                        "api_seconds": saved["result"].get("api_seconds"),
                        "attempts": saved["result"].get("attempts"),
                        "generation_created_at": saved["result"].get("created_at"),
                        "config_hash": config_hash,
                        "implementation_hash": implementation_hash,
                        "expected_model_version": config["expected_model_version"],
                        "model": config["model"], "endpoint": config["base_url"],
                        "upstream": config["upstream"], "tokenizer": config["tokenizer"],
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    }
                except api.APIError as exc:
                    record = {"slot_id": sid, "question_id": _qid, "position": position,
                              "split": config["split"], "stage": 3, "method": method,
                              "kind": spec["kind"], "question": sample["question"],
                              "status": "failed",
                              "error": f"APIError: {exc}", "fatal": bool(exc.fatal),
                              "api_attempts": exc.attempts, "answers": row["answers"],
                              "answer": None, "score": 0.0,
                              "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
                    if exc.attempts:
                        requests += 1
                except Exception as exc:  # noqa: BLE001 - fail the slot, keep the matrix honest
                    record = {"slot_id": sid, "question_id": _qid, "position": position,
                              "split": config["split"], "stage": 3, "method": method,
                              "kind": spec["kind"], "question": sample["question"],
                              "status": "failed",
                              "error": f"{type(exc).__name__}: {exc}", "fatal": False,
                              "answers": row["answers"], "answer": None, "score": 0.0,
                              "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
                record.setdefault("total_pipeline_seconds", time.perf_counter() - started)
                common.append_jsonl(results_path, record)
                written += 1
                if record["status"] == "success":
                    completed.add(sid)
                print(f"{record['status']}: {sid} requests={requests}/{request_budget}",
                      flush=True)
                if record.get("fatal"):
                    break
                if not record.get("cache_hit"):
                    time.sleep(config["request_interval_seconds"])
            else:
                continue
            break
    finally:
        if client is not None:
            client.close()
        lock.unlink(missing_ok=True)

    records = load_records(results_path)
    common.atomic_json(run_dir / "coverage.json", coverage_from_records(meta, records))
    _write_failures(run_dir, records)
    report = summarize(run_dir)
    print(f"Results: {run_dir}; new_rows={written}; complete={report['complete']}", flush=True)
    return run_dir, written


# --------------------------------------------------------------------------- records

def load_records(path):
    """Latest record per slot, keeping only compact fields (streams the JSONL)."""
    records = {}
    path = Path(path)
    if not path.exists():
        return records
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = row.get("slot_id")
            if not sid:
                continue
            usage = row.get("usage") or {}
            records[sid] = {
                "slot_id": sid,
                "question_id": row.get("question_id"),
                "position": row.get("position"),
                "method": row.get("method"),
                "status": row.get("status", "unknown"),
                "score": row.get("score"),
                "actual_ratio": row.get("actual_ratio"),
                "budget_satisfied": row.get("budget_satisfied"),
                "prompt_tokens": row.get("prompt_tokens"),
                "origin_prompt_tokens": row.get("origin_prompt_tokens"),
                "usage": usage,
                "cache_hit": row.get("cache_hit"),
                "error": row.get("error"),
            }
    return records


def coverage_from_records(meta, records):
    config = meta["config"]
    expected = expected_slot_ids(meta)
    found = set(records)
    missing = [sid for sid in expected if sid not in found]
    failed = [sid for sid, record in records.items() if record["status"] != "success"]
    cells = []
    for method in config["methods"]:
        for position in config["positions"]:
            ok = sum(1 for sid in expected
                     if records.get(sid, {}).get("status") == "success"
                     and records[sid]["method"] == method
                     and records[sid]["position"] == position)
            cells.append({"method": method, "position": position,
                          "expected": len(meta["question_ids"]), "success": ok})
    return {
        "split": config["split"], "questions": len(meta["question_ids"]),
        "positions": config["positions"], "methods": list(config["methods"]),
        "expected_slots": len(expected),
        "success": sum(1 for record in records.values() if record["status"] == "success"),
        "failed": len(failed), "missing": len(missing),
        "cells": cells,
        "missing_slot_ids": missing,
        "failed_slot_ids": failed,
    }


def _write_failures(run_dir, records):
    lines = []
    for sid, record in records.items():
        if record["status"] == "success":
            continue
        lines.append(json.dumps({"slot_id": sid, "method": record["method"],
                                 "position": record["position"],
                                 "question_id": record["question_id"],
                                 "status": record["status"], "error": record["error"]},
                                ensure_ascii=False))
    (Path(run_dir) / "failures.jsonl").write_text(
        "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


# --------------------------------------------------------------------------- summarise

def summarize_records(meta, records):
    config = meta["config"]
    expected = len(meta["question_ids"])
    groups = []
    for method in config["methods"]:
        for position in config["positions"]:
            rows = [record for record in records.values()
                    if record["method"] == method and record["position"] == position]
            ok = [record for record in rows if record["status"] == "success"]
            ratio = [record["actual_ratio"] for record in ok
                     if isinstance(record["actual_ratio"], (int, float))]
            groups.append({
                "method": method, "position": position, "expected": expected,
                "success": len(ok), "failed": len(rows) - len(ok),
                "missing": expected - len(rows),
                "best_subspan_em": (sum(record["score"] for record in ok) / len(ok)
                                    if ok else None),
                "mean_actual_ratio": (sum(ratio) / len(ratio) if ratio else None),
                "budget_satisfied_rate": (
                    sum(bool(record["budget_satisfied"]) for record in ok) / len(ok)
                    if ok else None),
                "api_input_tokens": sum((record["usage"] or {}).get("prompt_tokens", 0)
                                        for record in ok),
                "api_output_tokens": sum((record["usage"] or {}).get("completion_tokens", 0)
                                         for record in ok),
            })
    methods = []
    for method in config["methods"]:
        cells = [group for group in groups if group["method"] == method]
        scored = [cell["best_subspan_em"] for cell in cells if cell["best_subspan_em"] is not None]
        methods.append({
            "method": method,
            "kind": method_spec(config, method)["kind"],
            "ratio": method_spec(config, method)["ratio"],
            "success": sum(cell["success"] for cell in cells),
            "failed": sum(cell["failed"] for cell in cells),
            "missing": sum(cell["missing"] for cell in cells),
            "expected": expected * len(config["positions"]),
            "mean_em": statistics.mean(scored) if scored else None,
            "mean_actual_ratio": statistics.mean(
                [cell["mean_actual_ratio"] for cell in cells
                 if cell["mean_actual_ratio"] is not None]) if scored else None,
            "budget_satisfied_rate": statistics.mean(
                [cell["budget_satisfied_rate"] for cell in cells
                 if cell["budget_satisfied_rate"] is not None]) if scored else None,
            "api_input_tokens": sum(cell["api_input_tokens"] for cell in cells),
            "api_output_tokens": sum(cell["api_output_tokens"] for cell in cells),
        })
    complete = all(group["success"] == group["expected"] for group in groups)
    return {"complete": complete, "split": config["split"], "expected": expected,
            "positions": config["positions"], "methods": methods, "groups": groups,
            "compressor": meta.get("compressor")}


def summarize(run_dir):
    run_dir = Path(run_dir)
    meta = common.read_json(run_dir / "run.json")
    records = load_records(run_dir / "results.jsonl")
    report = summarize_records(meta, records)
    common.atomic_json(run_dir / "summary.json", report)
    common.atomic_json(run_dir / "coverage.json", coverage_from_records(meta, records))

    methods = [row["method"] for row in report["methods"]]
    by_cell = {(row["method"], row["position"]): row for row in report["groups"]}
    lines = ["# Stage-three main results", "",
             f"Split `{report['split']}`, {report['expected']} questions x "
             f"{len(report['positions'])} positions, complete: **{report['complete']}**.", "",
             "EM is the upstream `best_subspan_em`; ratios are measured full-prompt "
             "tokens; failed/missing are reported before interpreting scores.", "",
             "| Method | " + " | ".join(f"pos {p}" for p in report["positions"]) +
             " | Mean EM | Actual ratio | Budget met | Success |",
             "| --- | " + " | ".join("---:" for _ in report["positions"]) +
             " | ---: | ---: | ---: | ---: |"]
    for method in methods:
        cells = [by_cell[(method, position)] for position in report["positions"]]
        em_cells = " | ".join(
            f"{cell['best_subspan_em']:.2f}" if cell["best_subspan_em"] is not None else "—"
            for cell in cells)
        overall = next(row for row in report["methods"] if row["method"] == method)
        fmt = (lambda value, pattern="{:.2f}": pattern.format(value)
               if value is not None else "—")
        ratio = fmt(overall["mean_actual_ratio"])
        budget = fmt(overall["budget_satisfied_rate"])
        lines.append(f"| {method} | {em_cells} | {fmt(overall['mean_em'])} | "
                     f"{ratio} | {budget} | {overall['success']}/{overall['expected']} |")
    lines += ["", "Coverage and per-slot denominators are in `coverage.json`; failures in "
              "`failures.jsonl`.", ""]
    (run_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return report


# --------------------------------------------------------------------------- statistics

def paired_bootstrap(differences, samples=2000, seed=42, confidence=0.95):
    """Percentile bootstrap over paired per-question differences."""
    values = [float(value) for value in differences if value is not None]
    if not values:
        return {"n": 0, "mean": None, "ci_low": None, "ci_high": None}
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(int(samples)):
        total = 0.0
        for _ in range(n):
            total += values[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    alpha = (1.0 - float(confidence)) / 2.0
    low = means[max(0, int(alpha * samples) - 1)]
    high = means[min(samples - 1, int((1.0 - alpha) * samples))]
    return {"n": n, "mean": statistics.mean(values), "ci_low": low, "ci_high": high}


def paired_comparisons(meta, records):
    config = meta["config"]
    positions = config["positions"]
    baseline = config["baseline"]
    per = defaultdict(list)
    for record in records.values():
        if record["status"] != "success" or record["score"] is None:
            continue
        per[(record["question_id"], record["method"])].append(record["score"])
    complete = {key: sum(scores) / len(scores) for key, scores in per.items()
                if len(scores) == len(positions)}
    stats = config.get("statistics", {})
    comparisons = []
    for method in config["methods"]:
        if method == baseline:
            continue
        common_questions = [qid for qid in meta["question_ids"]
                            if (qid, method) in complete and (qid, baseline) in complete]
        if not common_questions:
            comparisons.append({"method": method, "baseline": baseline, "n_questions": 0,
                                "mean": None, "ci_low": None, "ci_high": None})
            continue
        diffs = [complete[(qid, method)] - complete[(qid, baseline)]
                 for qid in common_questions]
        result = paired_bootstrap(diffs, samples=stats.get("bootstrap_samples", 2000),
                                  seed=stats.get("seed", 42),
                                  confidence=stats.get("confidence", 0.95))
        comparisons.append({
            "method": method, "baseline": baseline,
            "n_questions": result["n"],
            "coverage": result["n"] / len(meta["question_ids"]),
            "baseline_mean": statistics.mean(complete[(qid, baseline)]
                                             for qid in common_questions),
            "method_mean": statistics.mean(complete[(qid, method)]
                                           for qid in common_questions),
            "mean": result["mean"], "ci_low": result["ci_low"], "ci_high": result["ci_high"],
        })
    return comparisons


def stats(run_dir):
    run_dir = Path(run_dir)
    meta = common.read_json(run_dir / "run.json")
    records = load_records(run_dir / "results.jsonl")
    comparisons = paired_comparisons(meta, records)
    report = {"split": meta["config"]["split"],
              "bootstrap": meta["config"].get("statistics"),
              "unit": "question (all positions kept together)",
              "comparisons": comparisons}
    common.atomic_json(run_dir / "stats.json", report)
    lines = ["# Paired comparison vs baseline", "",
             f"Unit: question; bootstrap {report['bootstrap'].get('bootstrap_samples')} "
             f"draws, seed {report['bootstrap'].get('seed')}, "
             f"{report['bootstrap'].get('confidence')} CI.", "",
             "| Method | n questions | Coverage | Baseline EM | Method EM | Δ EM | 95% CI |",
             "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in comparisons:
        if not row["n_questions"]:
            lines.append(f"| {row['method']} | 0 | 0 | — | — | — | — |")
            continue
        lines.append(f"| {row['method']} | {row['n_questions']} | {row['coverage']:.1%} | "
                     f"{row['baseline_mean']:.3f} | {row['method_mean']:.3f} | "
                     f"{row['mean']:+.3f} | [{row['ci_low']:+.3f}, {row['ci_high']:+.3f}] |")
    (run_dir / "stats.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


# --------------------------------------------------------------------------- figures

def figures(run_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    run_dir = Path(run_dir)
    report = common.read_json(run_dir / "summary.json")
    positions = report["positions"]
    methods = [row["method"] for row in report["methods"]]
    by_cell = {(row["method"], row["position"]): row["best_subspan_em"]
               for row in report["groups"]}
    out = run_dir / "figures"
    out.mkdir(exist_ok=True)

    plt.figure(figsize=(7, 4.2))
    for method in methods:
        values = [by_cell.get((method, position)) for position in positions]
        if any(value is None for value in values):
            continue
        plt.plot(positions, values, marker="o", label=method)
    plt.xlabel("answer document position")
    plt.ylabel("EM")
    plt.title(f"Position curve ({report['split']})")
    plt.xticks(positions)
    plt.grid(alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(out / "position_curves.png", dpi=160)
    plt.close()

    plt.figure(figsize=(6, 4.2))
    for row in report["methods"]:
        if row["mean_actual_ratio"] is None or row["mean_em"] is None:
            continue
        plt.scatter(row["mean_actual_ratio"], row["mean_em"], s=40)
        plt.annotate(row["method"], (row["mean_actual_ratio"], row["mean_em"]),
                     fontsize=8, xytext=(4, 4), textcoords="offset points")
    plt.xlabel("actual compression ratio (origin / compressed)")
    plt.ylabel("mean EM")
    plt.title("Quality vs actual compression")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "quality_vs_ratio.png", dpi=160)
    plt.close()

    with (out / "main_table.csv").open("w", encoding="utf-8", newline="") as handle:
        handle.write("method," + ",".join(f"pos_{position}" for position in positions) +
                     ",mean_em,actual_ratio\n")
        for row in report["methods"]:
            cells = [by_cell.get((row["method"], position)) for position in positions]
            cell_text = ",".join("" if value is None else f"{value:.4f}" for value in cells)
            mean_em = "" if row["mean_em"] is None else f"{row['mean_em']:.4f}"
            ratio = "" if row["mean_actual_ratio"] is None else f"{row['mean_actual_ratio']:.4f}"
            handle.write(f"{row['method']},{cell_text},{mean_em},{ratio}\n")
    return out


# --------------------------------------------------------------------------- casebook

def casebook(run_dir, limit=2):
    run_dir = Path(run_dir)
    meta = common.read_json(run_dir / "run.json")
    records = load_records(run_dir / "results.jsonl")
    chosen_ids = []
    for method in meta["config"]["methods"]:
        rows = [record for record in records.values() if record["method"] == method]
        successes = [record for record in rows if record["status"] == "success"]
        failures = [record for record in rows if record["status"] != "success"]
        chosen_ids += [record["slot_id"] for record in successes
                       if record.get("score") == 1.0][:limit]
        chosen_ids += [record["slot_id"] for record in successes
                       if record.get("score") == 0.0][:limit]
        chosen_ids += [record["slot_id"] for record in failures][:limit]
    wanted = set(chosen_ids)
    rows = {}
    with (run_dir / "results.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("slot_id") in wanted:
                rows[row["slot_id"]] = row
    lines = ["# Stage-three cases", "",
             f"Run `{meta['run_id']}`, split `{meta['split']}`.", ""]
    for sid in chosen_ids:
        row = rows.get(sid)
        if not row:
            continue
        lines += [f"## {sid}", "",
                  f"- status: {row['status']}; score: {row.get('score')}; "
                  f"ratio: {row.get('actual_ratio')}",
                  f"- question: {row.get('question')}",
                  f"- answer: {row.get('answer')!r}",
                  f"- gold answers: {row.get('answers')}",
                  f"- error: {row.get('error')}", ""]
    path = run_dir / "casebook.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- CLI

def main():
    parser = argparse.ArgumentParser(description="LongLLMLingua stage-three main experiment")
    parser.add_argument("--config", help="JSON config path (default: configs/stage3.json)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("plan", help="Offline budget and slot counts; no model load, no API calls")
    run_parser = sub.add_parser("run", help="Run/resume the real matrix")
    run_parser.add_argument("--limit", type=int, help="Max new logical API calls this invocation")
    for name, help_text in (("summarize", "Rebuild summary/coverage from saved rows"),
                            ("stats", "Paired bootstrap vs the baseline"),
                            ("figures", "Rebuild figures from summary.json"),
                            ("casebook", "Representative success/failure cases")):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    config = load_stage3_config(args.config)
    if args.command == "plan":
        print(json.dumps(plan(config), ensure_ascii=False, indent=2))
    elif args.command == "run":
        run_dir, written = run(config, args.limit)
        print(f"Results: {run_dir}; new_rows={written}")
    elif args.command == "summarize":
        print(json.dumps(summarize(args.run_dir), ensure_ascii=False, indent=2))
    elif args.command == "stats":
        print(json.dumps(stats(args.run_dir), ensure_ascii=False, indent=2))
    elif args.command == "figures":
        print(figures(args.run_dir))
    elif args.command == "casebook":
        print(casebook(args.run_dir))


if __name__ == "__main__":
    main()
