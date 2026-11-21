"""Rescore saved recovery outputs and compare removing recovery, without API calls.

Requires a complete run.json and full results.jsonl, not a lightweight export.
Five positions stay together in a question-level paired bootstrap. This analyzes
the saved before/after answers; it does not replay the recovery algorithm.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSITIONS = (1, 5, 10, 15, 20)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def upstream_score():
    path = ROOT / "vendor/lost_in_the_middle/metrics.py"
    spec = importlib.util.spec_from_file_location("stage4_upstream_metrics", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return lambda answer, gold: module.best_subspan_em(answer.split("\n")[0].strip(), gold)


def percentile(values, probability):
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def paired_bootstrap(question_deltas, seed=42, repetitions=2000):
    """Each delta is a question's mean across all five positions (EM units)."""
    if not question_deltas:
        return None
    rng = random.Random(seed)
    size = len(question_deltas)
    draws = [sum(rng.choices(question_deltas, k=size)) / size for _ in range(repetitions)]
    return {"delta": sum(question_deltas) / size,
            "ci95": [percentile(draws, .025), percentile(draws, .975)],
            "question_denominator": size, "seed": seed, "repetitions": repetitions}


def analyze(meta, rows, question_ids, method="longllmlingua_2x"):
    if len(question_ids) != len(set(question_ids)) or not question_ids:
        raise ValueError("Manifest must contain nonempty unique question IDs")
    if set(meta["question_ids"]) != set(question_ids) or len(meta["question_ids"]) != len(question_ids):
        raise ValueError("Run question IDs do not match the fixed split manifest")
    if set(meta["config"]["positions"]) != set(POSITIONS) or len(meta["config"]["positions"]) != 5:
        raise ValueError("Recovery comparison requires all five fixed positions")
    method_spec = meta["config"]["methods"][method]
    if not method_spec.get("recovery") or method_spec.get("ratio") != 2:
        raise ValueError("Source method must be the full 2x method with recovery enabled")
    if method_spec.get("reorder_context") != "original":
        raise ValueError("Full-method comparison requires reordering disabled")
    expected = {(qid, position) for qid in question_ids for position in POSITIONS}
    latest = {}
    attempts = 0
    for row in rows:
        if row.get("method") != method:
            continue
        key = (row["question_id"], row["position"])
        if key not in expected:
            raise ValueError(f"Unexpected question/position: {key}")
        if row.get("slot_id") != f"{key[0]}:{key[1]}:{method}":
            raise ValueError("Slot ID does not match its question, position and method")
        latest[key] = row
        attempts += 1
    score = upstream_score()
    success, failed, gold_by_question, mismatches = {}, [], {}, []
    for key, row in latest.items():
        if row.get("status") != "success":
            failed.append({"question_id": key[0], "position": key[1],
                           "status": row.get("status"), "error": row.get("error")})
            continue
        before, after, gold = (row.get("answer_before_recovery"),
                               row.get("answer_after_recovery"), row.get("answers"))
        if not isinstance(before, str) or not isinstance(after, str):
            raise ValueError("Full saved before/after answer strings are required")
        if not isinstance(gold, list) or not gold or not all(isinstance(a, str) and a.strip() for a in gold):
            raise ValueError("Full saved gold answer lists are required for offline rescoring")
        if row.get("recovery_enabled") is not True:
            raise ValueError("Successful source row must have recovery enabled")
        canonical_gold = tuple(sorted(gold))
        if gold_by_question.setdefault(key[0], canonical_gold) != canonical_gold:
            raise ValueError("Gold answer set differs across positions of the same question")
        b, a = score(before, gold), score(after, gold)
        for name, measured in (("score_before_recovery", b), ("score_after_recovery", a)):
            if name in row and row[name] != measured:
                mismatches.append({"slot_id": row["slot_id"], "field": name,
                                   "stored": row[name], "rescored": measured})
        success[key] = {"question_id": key[0], "position": key[1],
                        "full_score": a, "no_recovery_score": b,
                        "answer_changed": before != after}
    complete_questions = [qid for qid in question_ids
                          if all((qid, p) in success for p in POSITIONS)]
    paired = [success[qid, p] for qid in complete_questions for p in POSITIONS]
    deltas = [sum(success[qid, p]["no_recovery_score"] - success[qid, p]["full_score"]
                  for p in POSITIONS) / 5 for qid in complete_questions]
    position_results = []
    for position in POSITIONS:
        cell = [r for r in paired if r["position"] == position]
        position_results.append({"position": position, "denominator": len(cell),
            "full_em": sum(r["full_score"] for r in cell) / len(cell) if cell else None,
            "no_recovery_em": sum(r["no_recovery_score"] for r in cell) / len(cell) if cell else None})
    return {
        "analysis": "Stored recovery outputs rescored; recovery algorithm not replayed",
        "method": method, "split": meta.get("split"),
        "complete": len(success) == len(expected), "expected_slots": len(expected),
        "success_slots": len(success), "failed_or_skipped_slots": len(failed),
        "missing_slots": [{"question_id": q, "position": p} for q, p in sorted(expected - latest.keys())],
        "failed_or_skipped": failed, "superseded_records": attempts - len(latest),
        "stored_score_mismatches": mismatches,
        "paired_question_denominator": len(complete_questions),
        "paired_slot_denominator": len(paired),
        "paired_question_coverage": len(complete_questions) / len(question_ids),
        "paired_questions": complete_questions,
        "excluded_questions": [q for q in question_ids if q not in complete_questions],
        "full_em": sum(r["full_score"] for r in paired) / len(paired) if paired else None,
        "no_recovery_em": sum(r["no_recovery_score"] for r in paired) / len(paired) if paired else None,
        "removing_recovery_minus_full": paired_bootstrap(deltas),
        "positions": position_results,
        "recovery_changed_slots": sum(r["answer_changed"] for r in paired),
        "recovery_helped_slots": sum(r["full_score"] > r["no_recovery_score"] for r in paired),
        "recovery_harmed_slots": sum(r["full_score"] < r["no_recovery_score"] for r in paired),
        "new_api_requests": 0, "new_compression_calls": 0,
        "paired_scores": paired,
    }


def run(run_dir, output):
    meta_path, rows_path = run_dir / "run.json", run_dir / "results.jsonl"
    meta = read_json(meta_path)
    split = meta["split"]
    if split not in ("smoke", "pilot", "main") or meta["config"]["split"] != split:
        raise ValueError("Inconsistent or unsupported split")
    manifest = read_json(ROOT / f"manifests/{split}.json")
    # Strict parsing: do not silently treat an interrupted last line as a complete run.
    rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    report = analyze(meta, rows, manifest["question_ids"])
    report["source"] = {"run_id": meta.get("run_id"), "run_dir": str(run_dir.resolve()),
        "config_hash": meta.get("config_hash"), "implementation_hash": meta.get("implementation_hash"),
        "files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (meta_path, rows_path)}}
    output.mkdir(parents=True, exist_ok=True)
    (output / "recovery-comparison.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs/stage4/recovery-analysis")
    args = parser.parse_args()
    report = run(args.run_dir, args.out)
    print(json.dumps({key: report[key] for key in (
        "split", "complete", "expected_slots", "success_slots", "paired_question_denominator",
        "full_em", "no_recovery_em", "removing_recovery_minus_full")}, indent=2))
    return 0 if report["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
