"""Offline acceptance for the stage-two matrix; never sends API requests.

Checks the invariants that the stage-three owner relies on: complete 4-method x
5-position matrix on the smoke split, prompts rebuildable from visible inputs,
budget/token arithmetic consistent with the hard-budget contract, per-method
mechanism switches visible in the trace, recovery before/after answers both
scored, and no evaluation-only field leaking into the compression inputs.

Usage: python scripts/accept_stage2.py outputs/stage2/<run_id>
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reproduction import common, data, evaluation, methods, recovery, runner
from reproduction.stage2 import _questions, _slots, load_stage2_config, summarize

ROWS_REQUIRED = (
    "slot_id", "question_id", "position", "split", "stage", "method", "answers",
    "status", "prompt", "prompt_hash", "prompt_tokens", "origin_prompt_tokens",
    "target_tokens", "actual_ratio", "target_ratio", "budget_satisfied",
    "selected_doc_ids", "truncated_doc_ids", "ranking", "trace",
    "compression_seconds", "compression_cache_key", "method_version",
    "answer", "answer_before_recovery", "answer_after_recovery",
    "recovery_enabled", "recovery_stats", "score_before_recovery",
    "score_after_recovery", "score", "cache_key", "cache_hit",
    "config_hash", "implementation_hash", "expected_model_version", "model",
    "endpoint", "upstream", "tokenizer", "usage", "response_model",
    "system_fingerprint", "finish_reason", "total_pipeline_seconds",
)
TRACE_REQUIRED = (
    "budget_mode", "target_tokens", "attempts", "document_scores",
    "used_doc_ids", "dropped_doc_ids", "dynamic_ratios",
    "compressed_context_tokens", "compressed_context_preview", "restrict_enabled",
    "library_origin_tokens", "library_compressed_tokens", "library_ratio_label",
)


def _fail(checks, name, detail=""):
    checks.append({"check": name, "passed": False, "detail": detail})
    raise AssertionError(f"{name}: {detail}")


def _ok(checks, name):
    checks.append({"check": name, "passed": True, "detail": ""})


def accept(run_dir):
    run_dir = Path(run_dir).resolve()
    config = load_stage2_config()
    runner.verify_resources(config)
    counter = methods.TokenCounter()
    checks = []
    budget_misses = []

    meta = common.read_json(run_dir / "run.json")
    if meta.get("config_hash") != common.configuration_hash(config):
        _fail(checks, "config hash matches current config")
    if meta.get("implementation_hash") != common.implementation_hash():
        _fail(checks, "implementation hash matches current code")
    if meta.get("stage") != 2 or meta.get("split") != config["split"]:
        _fail(checks, "run metadata identifies stage 2 and the configured split")
    for key in ("compressor", "tokenizer", "upstream", "started_at"):
        if not meta.get(key):
            _fail(checks, "run metadata carries " + key)
    _ok(checks, "run metadata is stage-two and reproducible")

    questions = _questions(config)
    expected = {slot["slot_id"]: slot for slot in _slots(config, questions)}
    latest = {}
    for row in common.read_jsonl(run_dir / "results.jsonl"):
        latest[row["slot_id"]] = row
    if len(expected) != len(config["methods"]) * len(questions):
        _fail(checks, "expected slot count derives from methods x questions")
    if len(latest) != len(expected):
        _fail(checks, "matrix complete", f"{len(latest)}/{len(expected)} rows")
    if set(latest) != set(expected):
        _fail(checks, "slot ids match the manifest x methods", str(set(latest) ^ set(expected))[:200])
    _ok(checks, f"matrix complete ({len(expected)} slots)")

    stored_summary = run_dir / "summary.json"
    if stored_summary.exists():
        if common.read_json(stored_summary) != summarize(run_dir):
            _fail(checks, "stored summary reproduces offline")
        _ok(checks, "stored summary reproduces offline")

    spec_by_method = config["methods"]
    method_positions = defaultdict(int)
    used_sets = defaultdict(dict)
    for slot_id, row in latest.items():
        slot = expected[slot_id]
        for field in ROWS_REQUIRED:
            if field not in row:
                _fail(checks, f"{slot_id} carries field {field}")
        if row["status"] != "success" or row.get("finish_reason") != "stop":
            _fail(checks, f"{slot_id} finished successfully", str(row.get("error"))[:200])
        if row["method"] != slot["method"] or row["position"] != slot["position"]:
            _fail(checks, f"{slot_id} row identity matches slot")
        if row["prompt_hash"] != common.digest(row["prompt"]):
            _fail(checks, f"{slot_id} prompt hash matches prompt")
        if counter.count(row["prompt"]) != row["prompt_tokens"]:
            _fail(checks, f"{slot_id} prompt token count reproducible")

        sample = data.visible_sample(slot["row"])
        original_prompt = methods.prompt(sample["question"], sample["documents"])
        origin = counter.count(original_prompt)
        if row["origin_prompt_tokens"] != origin:
            _fail(checks, f"{slot_id} original prompt tokens reproduce")
        ratio = float(row["target_ratio"])
        if ratio <= 1.0:
            _fail(checks, f"{slot_id} target ratio > 1")
        if row["target_tokens"] != math.floor(origin / ratio):
            _fail(checks, f"{slot_id} target tokens = floor(original/ratio)")
        if not row["prompt"].rstrip().endswith("Answer:"):
            _fail(checks, f"{slot_id} prompt keeps the stage-one template tail")
        expected_ratio = origin / row["prompt_tokens"]
        if abs(expected_ratio - row["actual_ratio"]) > 1e-6:
            _fail(checks, f"{slot_id} actual ratio = original/compressed")
        if config["compressor"]["budget_mode"] == "hard":
            attempts = row["trace"]["attempts"]
            if not attempts:
                _fail(checks, f"{slot_id} budget attempts recorded")
            if row["prompt_tokens"] != int(attempts[-1]["compressed_tokens"]):
                _fail(checks, f"{slot_id} selected attempt is the reported prompt")
            if row["budget_satisfied"]:
                if row["prompt_tokens"] > row["target_tokens"]:
                    _fail(checks, f"{slot_id} hard budget respected",
                          f"{row['prompt_tokens']} > {row['target_tokens']}")
            else:
                # Honest misses are allowed if the retry budget was exhausted and the
                # overshoot stays small; the summary reports the satisfied rate.
                if len(attempts) != config["compressor"]["max_budget_passes"]:
                    _fail(checks, f"{slot_id} miss exhausted the retry budget")
                if row["prompt_tokens"] <= row["target_tokens"]:
                    _fail(checks, f"{slot_id} miss is genuinely over budget")
                if row["prompt_tokens"] > row["target_tokens"] * 1.05:
                    _fail(checks, f"{slot_id} miss overshoot beyond 5%")
                budget_misses.append((slot_id, row["prompt_tokens"], row["target_tokens"]))

        spec = spec_by_method[row["method"]]
        trace = row["trace"]
        for field in TRACE_REQUIRED:
            if field not in trace:
                _fail(checks, f"{slot_id} trace carries {field}")
        if trace["budget_mode"] != config["compressor"]["budget_mode"]:
            _fail(checks, f"{slot_id} trace budget mode matches config")
        if bool(trace["restrict_enabled"]) != bool(spec["restrict"]):
            _fail(checks, f"{slot_id} restrict switch visible in trace")
        if row["recovery_enabled"] != bool(spec["recovery"]):
            _fail(checks, f"{slot_id} recovery switch matches config")
        if row["answer_before_recovery"] != row["answer"]:
            _fail(checks, f"{slot_id} original answer preserved for recovery")
        if row["score"] != evaluation.score(row["answer_after_recovery"]
                                            if spec["recovery"] else row["answer"],
                                            slot["answers"]):
            _fail(checks, f"{slot_id} score matches the reported answer path")
        if row["score_before_recovery"] != evaluation.score(row["answer"], slot["answers"]):
            _fail(checks, f"{slot_id} before-recovery score reproducible")
        if row["score_after_recovery"] != evaluation.score(row["answer_after_recovery"],
                                                           slot["answers"]):
            _fail(checks, f"{slot_id} after-recovery score reproducible")
        changed = row["answer_after_recovery"] != row["answer"]
        if spec["recovery"]:
            if changed != bool(row["recovery_stats"].get("changed")):
                _fail(checks, f"{slot_id} recovery changed flag matches text")
        elif row["answer_after_recovery"] != row["answer"]:
            _fail(checks, f"{slot_id} recovery-off keeps the answer unchanged")

        dynamic = float(spec["dynamic_context_compression_ratio"])
        ratios = trace["dynamic_ratios"]
        if dynamic > 0:
            if len(ratios) != len(trace["used_doc_ids"]):
                _fail(checks, f"{slot_id} one dynamic ratio per retained document")
            if any(abs(value) > dynamic + 1e-9 for value in ratios):
                _fail(checks, f"{slot_id} dynamic offsets stay within +/-delta")
        elif any(value != 0.0 for value in ratios):
            _fail(checks, f"{slot_id} dynamic offsets stay zero when the switch is off")

        cached = ROOT / "cache/compress2" / f"{row['compression_cache_key']}.json"
        if not cached.exists():
            _fail(checks, f"{slot_id} compression cache entry exists")
        saved = common.read_json(cached)
        if saved["result"]["trace"]["used_doc_ids"] != trace["used_doc_ids"]:
            _fail(checks, f"{slot_id} cached trace matches the row")
        api_cached = ROOT / "cache/api" / f"{row['cache_key']}.json"
        if not api_cached.exists():
            _fail(checks, f"{slot_id} answer cache entry exists")
        if common.read_json(api_cached)["result"]["answer"] != row["answer"]:
            _fail(checks, f"{slot_id} cached answer matches the row")

        method_positions[(row["method"], row["position"])] += 1
        used_sets[row["method"]][(row["question_id"], row["position"])] = tuple(
            trace["used_doc_ids"])

    # Recovery is offline: replay Algorithm 1 on a sample of stored rows and require
    # the stored after-recovery answer and stats to reproduce exactly.
    replay_budget, replay_checked = 10, 0
    for slot_id in sorted(latest):
        row = latest[slot_id]
        spec = spec_by_method[row["method"]]
        if not spec["recovery"] or replay_checked >= replay_budget:
            continue
        slot = expected[slot_id]
        sample = data.visible_sample(slot["row"])
        original_prompt = methods.prompt(sample["question"], sample["documents"])
        text, stats = recovery.recover_answer(original_prompt, row["prompt"],
                                              row["answer"], counter)
        if text != row["answer_after_recovery"]:
            _fail(checks, f"{slot_id} recovered answer replays", "text differs")
        for key in ("matched_spans", "matched_response_tokens", "recovered_tokens", "changed"):
            if stats.get(key) != row["recovery_stats"].get(key):
                _fail(checks, f"{slot_id} recovery stat {key} replays",
                      f"{stats.get(key)} != {row['recovery_stats'].get(key)}")
        replay_checked += 1
    if replay_checked:
        _ok(checks, f"recovery replays offline on {replay_checked} stored rows")

    expected_per_cell = len(questions) // len(config["positions"])
    for method in config["methods"]:
        for position in config["positions"]:
            if method_positions[(method, position)] != expected_per_cell:
                _fail(checks, f"{method} position {position} has {expected_per_cell} rows")
    _ok(checks, "every method x position cell is complete")

    if config["compressor"]["budget_mode"] == "hard":
        total = len(latest)
        satisfied = sum(1 for row in latest.values() if row["budget_satisfied"])
        if satisfied / total < 0.95:
            _fail(checks, "hard-budget satisfaction rate >= 95%",
                  f"{satisfied}/{total}")
        _ok(checks, f"hard-budget satisfaction {satisfied}/{total}"
                   + (f", honest misses: {len(budget_misses)}" if budget_misses else ""))

    if "llmlingua_2x" in config["methods"] and "longllmlingua_2x" in config["methods"]:
        left = used_sets["llmlingua_2x"]
        right = used_sets["longllmlingua_2x"]
        differing = sum(1 for key in left if left[key] != right.get(key))
        if differing == 0:
            _fail(checks, "question-aware ranking changes retained documents")
        _ok(checks, f"question-aware ranking differs on {differing}/{len(left)} samples")

    report = {
        "accepted_run": str(run_dir.relative_to(ROOT)),
        "config_hash": meta["config_hash"],
        "implementation_hash": meta["implementation_hash"],
        "slots": len(latest),
        "methods": list(config["methods"]),
        "positions": config["positions"],
        "budget_mode": config["compressor"]["budget_mode"],
        "budget_satisfied": sum(1 for row in latest.values() if row["budget_satisfied"]),
        "budget_honest_misses": [{"slot_id": slot, "prompt_tokens": got, "target": want}
                                 for slot, got, want in budget_misses],
        "checks": checks,
        "passed": True,
    }
    out = ROOT / "reports" / f"{config['split']}-stage2-acceptance.json"
    common.atomic_json(out, report)
    return report, latest


def sample_rows(latest, limit=6):
    chosen = []
    seen = set()
    for slot_id in sorted(latest):
        method = latest[slot_id]["method"]
        if method in seen:
            continue
        seen.add(method)
        row = latest[slot_id]
        chosen.append({key: row.get(key) for key in (
            "slot_id", "question_id", "position", "method", "prompt_tokens",
            "origin_prompt_tokens", "target_tokens", "actual_ratio",
            "budget_satisfied", "selected_doc_ids", "recovery_enabled",
            "score_before_recovery", "score_after_recovery",
            "compression_seconds")})
        if len(chosen) >= limit:
            break
    return chosen


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args(argv)
    report, latest = accept(args.run_dir)
    path = ROOT / "reports" / "stage2-smoke"
    path.mkdir(parents=True, exist_ok=True)
    sample_path = path / "accepted-sample.jsonl"
    with sample_path.open("w", encoding="utf-8") as handle:
        for row in sample_rows(latest):
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    report_path = ROOT / "reports" / f"{load_stage2_config()['split']}-stage2-acceptance.json"
    print(json.dumps({"passed": report["passed"], "slots": report["slots"],
                      "checks": len(report["checks"]), "report": str(report_path),
                      "sample": str(sample_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
