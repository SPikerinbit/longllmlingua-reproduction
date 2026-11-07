"""Stage-two runner: LLMLingua / LongLLMLingua compression, answer, recovery, scoring.

Mirrors the stage-one conventions (config files, append-only result rows, resumable
runs, API cache, upstream scoring) and adds the compression layer:

* compression is cached separately from the answer cache, so a recovery-only change
  never re-runs the 7B compressor, and a compressor-run change never re-calls the API;
* every slot carries the mechanism trace (document scores, retained documents,
  per-document dynamic ratios, token budget attempts, compressed-text preview);
* recovery runs after the answer, both answers are stored and both are scored;
* the answered prompt is the stage-one template, so 2x/4x mean the same thing for
  every method.

Entry point: ``python -m reproduction.stage2 <plan|run|summarize|casebook>``.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from . import api, common, compression, data, evaluation, methods, recovery, runner

PINNED_LLMLINGUA = "5a4c78ae18ab17a98cf997e8259354e546081d64"


def load_stage2_config(path=None):
    path = Path(path) if path else common.ROOT / "configs/stage2.json"
    config = common.read_json(path)
    if config.get("stage") != 2:
        raise ValueError("Stage-two config must declare stage=2")
    if config.get("provider") != "deepseek" or config.get("base_url") != "https://api.deepseek.com":
        raise ValueError("Stage two keeps the verified DeepSeek endpoint")
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
        raise ValueError("Stage two is pinned to llmlingua commit " + PINNED_LLMLINGUA)
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
    stage_methods = config.get("methods")
    if not isinstance(stage_methods, dict) or not stage_methods:
        raise ValueError("methods must be a non-empty object")
    for name, spec in stage_methods.items():
        compression.method_spec(config, name)
        for key in ("rank_method", "condition_in_question", "reorder_context"):
            if not isinstance(spec.get(key), str) or not spec[key]:
                raise ValueError(f"methods.{name}.{key} must be a non-empty string")
        for key in ("condition_compare", "use_context_level_filter", "restrict", "recovery"):
            if not isinstance(spec.get(key), bool):
                raise ValueError(f"methods.{name}.{key} must be a boolean")
        if not isinstance(spec.get("dynamic_context_compression_ratio"), (int, float)):
            raise ValueError(f"methods.{name}.dynamic_context_compression_ratio must be numeric")
    return config


def _questions(config):
    return [(qid, position, row) for qid, position, row in data.iter_samples(config)]


def _slots(config, questions):
    return [{"slot_id": f"{qid}:{position}:{method}", "question_id": qid,
             "position": position, "split": config["split"], "method": method,
             "answers": row["answers"], "row": row}
            for qid, position, row in questions
            for method in config["methods"]]


def _compression_key(config, method, sample):
    spec = compression.method_spec(config, method)
    compressor = config["compressor"]
    return common.digest({
        "method": method, "spec": spec, "sample": sample,
        "compressor": {key: compressor.get(key) for key in
                       ("model_name", "model_path", "torch_dtype", "attn_implementation",
                        "iterative_size", "context_budget", "budget_mode", "max_budget_passes")},
        "implementation": common.implementation_hash(),
        "upstream_llmlingua": config["upstream"]["llmlingua"],
    })


def _compress_cached(compressor, config, method, sample, counter):
    key = _compression_key(config, method, sample)
    cache_dir = common.ROOT / "cache/compress2"
    slot = cache_dir / f"{key}.json"
    if slot.exists():
        saved = common.read_json(slot)
        return saved["result"], True, key
    result = compression.compress_sample(compressor, config, method, sample, counter)
    cache_dir.mkdir(parents=True, exist_ok=True)
    common.atomic_json(slot, {"method": method, "key": key, "result": result})
    return result, False, key


def _run_dir(config, question_ids):
    digest = common.digest({"config": common.configuration_hash(config),
                            "implementation": common.implementation_hash(),
                            "question_ids": question_ids})
    return common.ROOT / "outputs/stage2" / digest[:20]


def plan(config):
    counter = methods.TokenCounter()
    runner.verify_resources(config)
    questions = _questions(config)
    slots = _slots(config, questions)
    budget = []
    for name, spec in config["methods"].items():
        ratio = float(spec["ratio"])
        row = {"method": name, "ratio": ratio, "slots": 0,
               "origin_tokens": 0, "target_tokens": 0}
        for slot in slots:
            if slot["method"] != name:
                continue
            sample = data.visible_sample(slot["row"])
            origin = counter.count(methods.prompt(sample["question"], sample["documents"]))
            row["slots"] += 1
            row["origin_tokens"] += origin
            row["target_tokens"] += origin // int(ratio)
        budget.append(row)
    compressor = config["compressor"]
    report = {"split": config["split"], "questions": len(questions),
              "slots": len(slots), "logical_call_limit": config["max_requests_per_run"],
              "budget_mode": compressor["budget_mode"],
              "compressor_model": compressor.get("model_name"),
              "compressor_model_path": compressor["model_path"],
              "compressor_present": Path(compressor["model_path"]).exists(),
              "budget": budget}
    (common.ROOT / "reports").mkdir(exist_ok=True)
    common.atomic_json(common.ROOT / f"reports/{config['split']}-stage2-plan.json", report)
    return report


def _error_row(slot, message):
    return {"slot_id": slot["slot_id"], "question_id": slot["question_id"],
            "position": slot["position"], "split": slot["split"],
            "method": slot["method"], "stage": 2, "status": "failed",
            "error": message, "answer": None, "answer_before_recovery": None,
            "answer_after_recovery": None, "recovery_enabled": False}


def run(config, limit=None):
    counter = methods.TokenCounter()
    runner.verify_resources(config)
    questions = _questions(config)
    slots = _slots(config, questions)
    run_dir = _run_dir(config, sorted({qid for qid, _, _ in questions}))
    run_dir.mkdir(parents=True, exist_ok=True)
    lock = run_dir / ".running"
    results_path = run_dir / "results.jsonl"
    if lock.exists():
        raise RuntimeError(f"Run already active: {run_dir}; remove {lock} only if no process runs")
    lock.write_text("running\n", encoding="utf-8")
    done = {}
    if results_path.exists():
        for row in common.read_jsonl(results_path):
            done[row["slot_id"]] = row
    compressor = None
    compressor_meta = None
    client = None
    new_calls = 0
    written = 0
    try:
        for slot in slots:
            previous = done.get(slot["slot_id"])
            if previous and previous.get("status") == "success":
                continue
            if limit is not None and new_calls >= limit:
                break
            method = slot["method"]
            spec = compression.method_spec(config, method)
            sample = data.visible_sample(slot["row"])
            original_prompt = methods.prompt(sample["question"], sample["documents"])
            started = time.perf_counter()
            try:
                if compressor is None:
                    compressor, compressor_meta = compression.load_compressor(config, counter)
                    client = api.DeepSeekClient(config, api.get_key(config))
                    meta_path = run_dir / "run.json"
                    meta = common.read_json(meta_path) if meta_path.exists() else {
                        "run_id": run_dir.name, "stage": 2, "split": config["split"],
                        "question_ids": sorted({qid for qid, _, _ in questions}),
                        "config": config,
                        "config_hash": common.configuration_hash(config),
                        "implementation_hash": common.implementation_hash(),
                        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "upstream": config["upstream"],
                        "tokenizer": config["tokenizer"],
                    }
                    meta["compressor"] = compressor_meta
                    common.atomic_json(meta_path, meta)
                compressed, compression_hit, compression_key = _compress_cached(
                    compressor, config, method, sample, counter)
                prompt = compressed["prompt"]
                prompt_tokens = counter.count(prompt)
                if prompt_tokens > config["max_context_tokens"]:
                    row = _error_row(slot, f"prompt tokens {prompt_tokens} exceed "
                                           f"max_context_tokens {config['max_context_tokens']}")
                    common.append_jsonl(results_path, row)
                    written += 1
                    continue
                payload = api.request_payload(config, prompt)
                saved, hit = api.cached_completion(
                    config, payload, client,
                    provenance={"run_id": run_dir.name, "slot_id": slot["slot_id"],
                                "stage": 2, "method": method})
                if not hit:
                    new_calls += 1
                answer = saved["result"]["answer"]
                if spec.get("recovery"):
                    recovered, recovery_stats = recovery.recover_answer(
                        original_prompt, prompt, answer, counter)
                else:
                    recovered = answer
                    recovery_stats = {"changed": False, "enabled": False,
                                      "response_tokens": counter.count(answer),
                                      "recovered_tokens": counter.count(answer)}
                row = {
                    "slot_id": slot["slot_id"], "question_id": slot["question_id"],
                    "position": slot["position"], "split": slot["split"], "stage": 2,
                    "method": method, "answers": slot["answers"], "status": "success",
                    "prompt": prompt, "prompt_hash": common.digest(prompt),
                    "prompt_tokens": prompt_tokens,
                    "origin_prompt_tokens": compressed["origin_tokens"],
                    "target_tokens": compressed["target_tokens"],
                    "actual_ratio": compressed["actual_ratio"],
                    "target_ratio": compressed["target_ratio"],
                    "budget_satisfied": compressed["budget_satisfied"],
                    "selected_doc_ids": compressed["selected_doc_ids"],
                    "truncated_doc_ids": compressed["truncated_doc_ids"],
                    "ranking": compressed["ranking"],
                    "trace": compressed["trace"],
                    "compression_seconds": compressed["compression_seconds"],
                    "compression_cache_hit": compression_hit,
                    "compression_cache_key": compression_key,
                    "method_version": compressed["method_version"],
                    "answer": answer,
                    "answer_before_recovery": answer,
                    "answer_after_recovery": recovered,
                    "recovery_enabled": bool(spec.get("recovery")),
                    "recovery_stats": recovery_stats,
                    "score_before_recovery": evaluation.score(answer, slot["answers"]),
                    "score_after_recovery": evaluation.score(recovered, slot["answers"]),
                    "score": evaluation.score(recovered if spec.get("recovery") else answer,
                                              slot["answers"]),
                    "cache_key": saved["cache_key"],
                    "cache_hit": hit,
                    "cache_source_provenance": saved.get("provenance"),
                    "config_hash": common.configuration_hash(config),
                    "implementation_hash": common.implementation_hash(),
                    "expected_model_version": config["expected_model_version"],
                    "model": config["model"], "endpoint": config["base_url"],
                    "upstream": config["upstream"], "tokenizer": config["tokenizer"],
                    "usage": saved["result"].get("usage"),
                    "response_model": saved["result"].get("response_model"),
                    "system_fingerprint": saved["result"].get("system_fingerprint"),
                    "response_id": saved["result"].get("response_id"),
                    "finish_reason": saved["result"].get("finish_reason"),
                    "api_seconds": saved["result"].get("api_seconds"),
                    "attempts": saved["result"].get("attempts"),
                    "generation_created_at": saved["result"].get("created_at"),
                    "total_pipeline_seconds": time.perf_counter() - started,
                }
            except api.APIError as exc:
                row = _error_row(slot, f"APIError: {exc}")
                row.update({"fatal": getattr(exc, "fatal", None),
                            "api_attempts": getattr(exc, "attempts", None)})
            except Exception as exc:  # noqa: BLE001 - fail the slot, keep the matrix honest
                row = _error_row(slot, f"{type(exc).__name__}: {exc}")
            row.setdefault("total_pipeline_seconds", time.perf_counter() - started)
            common.append_jsonl(results_path, row)
            written += 1
            print(f"{row['status']}: {slot['slot_id']} requests={new_calls}/"
                  f"{config['max_requests_per_run']}", flush=True)
    finally:
        lock.unlink(missing_ok=True)
    return run_dir, written


def summarize(run_dir):
    run_dir = Path(run_dir)
    meta = common.read_json(run_dir / "run.json")
    latest = {}
    for row in common.read_jsonl(run_dir / "results.jsonl"):
        latest[row["slot_id"]] = row
    groups = {}
    for row in latest.values():
        groups.setdefault((row["method"], row["position"]), []).append(row)
    expected = len(meta["question_ids"])
    summary = []
    for method in meta["config"]["methods"]:
        for position in meta["config"]["positions"]:
            rows = groups.get((method, position), [])
            ok = [row for row in rows if row["status"] == "success"]
            count = len(ok) or 1
            summary.append({
                "method": method, "position": position, "expected": expected,
                "success": len(ok), "failed": len(rows) - len(ok),
                "missing": expected - len(rows),
                "best_subspan_em": sum(r["score"] for r in ok) / len(ok) if ok else None,
                "best_subspan_em_before_recovery":
                    sum(r["score_before_recovery"] for r in ok) / len(ok) if ok else None,
                "best_subspan_em_after_recovery":
                    sum(r["score_after_recovery"] for r in ok) / len(ok) if ok else None,
                "mean_actual_ratio": sum(r["actual_ratio"] for r in ok) / count if ok else None,
                "budget_satisfied_rate": sum(r["budget_satisfied"] for r in ok) / count if ok else None,
                "mean_compression_seconds": sum(r["compression_seconds"] for r in ok) / count if ok else None,
                "recovery_changed_rate": sum(bool(r["recovery_stats"].get("changed")) for r in ok) / count if ok else None,
                "api_input_tokens": sum(r.get("usage", {}).get("prompt_tokens", 0) for r in ok),
                "api_output_tokens": sum(r.get("usage", {}).get("completion_tokens", 0) for r in ok),
            })
    complete = all(row["success"] == row["expected"] for row in summary)
    report = {"complete": complete, "groups": summary,
              "budget_mode": meta["config"]["compressor"]["budget_mode"],
              "compressor": meta.get("compressor")}
    common.atomic_json(run_dir / "summary.json", report)
    lines = ["# Stage-two compression results", "",
             f"Complete matrix: **{complete}** (budget mode: "
             f"{meta['config']['compressor']['budget_mode']})", "",
             "Scores use successful records only; check failed/missing before comparing.", "",
             "| Method | Position | Expected | Success | Failed | Missing | EM (scored answer) | EM before recovery | EM after recovery | Actual ratio | Budget met | Recovery changed |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in summary:
        def fmt(value, pattern="{:.2f}"):
            return pattern.format(value) if value is not None else "pending"
        lines.append(
            f"| {row['method']} | {row['position']} | {row['expected']} | {row['success']} | "
            f"{row['failed']} | {row['missing']} | {fmt(row['best_subspan_em'])} | "
            f"{fmt(row['best_subspan_em_before_recovery'])} | "
            f"{fmt(row['best_subspan_em_after_recovery'])} | {fmt(row['mean_actual_ratio'])} | "
            f"{fmt(row['budget_satisfied_rate'])} | {fmt(row['recovery_changed_rate'])} |")
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def casebook(run_dir, limit=8):
    """Write one trace/case record per (method, position) for the mechanism report."""
    run_dir = Path(run_dir)
    meta = common.read_json(run_dir / "run.json")
    latest = {}
    for row in common.read_jsonl(run_dir / "results.jsonl"):
        latest[row["slot_id"]] = row
    chosen = []
    for method in meta["config"]["methods"]:
        for position in meta["config"]["positions"]:
            for row in latest.values():
                if row["status"] == "success" and row["method"] == method and row["position"] == position:
                    chosen.append(row)
                    break
    chosen = chosen[:limit]
    blocks = ["# Stage-two compression traces", "",
              f"Run `{meta['run_id']}`; split `{meta['split']}`; "
              f"compressor `{meta.get('compressor', {}).get('model_name')}` "
              f"on `{meta.get('compressor', {}).get('device')}`.", ""]
    for row in chosen:
        trace = row["trace"]
        blocks += [f"## {row['slot_id']}", "",
                   f"- origin tokens: {row['origin_prompt_tokens']}; "
                   f"target: {row['target_tokens']}; compressed: {row['prompt_tokens']}; "
                   f"actual ratio {row['actual_ratio']:.2f}x; budget met: {row['budget_satisfied']}",
                   f"- retained documents: {len(row['selected_doc_ids'])}/"
                   f"{len(row['selected_doc_ids']) + len(trace['dropped_doc_ids'])}; "
                   f"attempts: {len(trace['attempts'])}",
                   f"- restrict switch: {trace['restrict_enabled']}; "
                   f"dynamic ratios: {[round(v, 3) for v in trace['dynamic_ratios']]}",
                   f"- recovery: changed={row['recovery_stats'].get('changed')}, "
                   f"spans={row['recovery_stats'].get('matched_spans')}, "
                   f"answer tokens={row['recovery_stats'].get('response_tokens')}", "",
                   "| doc | doc_id | condition score | retained |", "| ---: | --- | ---: | --- |"]
        for item in trace["document_scores"]:
            blocks.append(f"| {item['doc_index']} | {item['doc_id']} | "
                          f"{item['score']:.3f} | {item['retained']} |")
        blocks += ["", "Compressed text preview:", "", "```text",
                   trace["compressed_context_preview"].replace("```", "'''"), "```", "",
                   f"Answer before recovery: `{row['answer_before_recovery']}`", "",
                   f"Answer after recovery: `{row['answer_after_recovery']}`", "",
                   f"Scores: before={row['score_before_recovery']}, "
                   f"after={row['score_after_recovery']}", ""]
    path = run_dir / "casebook.md"
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description="LongLLMLingua stage-two compression matrix")
    parser.add_argument("--config", help="JSON config path (default: configs/stage2.json)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("plan", help="Offline matrix/token budget check; no model load, no API calls")
    run_parser = sub.add_parser("run", help="Run/resume compression + real API + recovery")
    run_parser.add_argument("--limit", type=int, help="Max new logical API calls in this invocation")
    summary = sub.add_parser("summarize", help="Rescore saved predictions without API calls")
    summary.add_argument("run_dir", type=Path)
    book = sub.add_parser("casebook", help="Write per-config traces from saved predictions")
    book.add_argument("run_dir", type=Path)
    book.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()
    config = load_stage2_config(args.config)
    if args.command == "plan":
        print(json.dumps(plan(config), ensure_ascii=False, indent=2))
    elif args.command == "run":
        run_dir, written = run(config, args.limit)
        print(f"Results: {run_dir}; new_rows={written}")
    elif args.command == "summarize":
        print(json.dumps(summarize(args.run_dir), ensure_ascii=False, indent=2))
    elif args.command == "casebook":
        print(casebook(args.run_dir, args.limit))


if __name__ == "__main__":
    main()
