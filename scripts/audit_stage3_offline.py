#!/usr/bin/env python3
"""Check committed stage-three summary, coverage and paired stats. No API."""

from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(root: Path = ROOT) -> dict:
    started = time.perf_counter()
    summary = json.loads((root / "reports/stage3-main/summary.json").read_text())
    coverage = json.loads((root / "reports/stage3-main/coverage.json").read_text())
    stats = json.loads((root / "reports/stage3-main/stats.json").read_text())
    by_method = {row["method"]: row for row in summary["methods"]}
    problems = []
    if coverage["success"] != coverage["expected_slots"] or coverage["failed"] or coverage["missing"]:
        problems.append("coverage is not a complete  success matrix")
    if sum(row["success"] for row in summary["methods"]) != coverage["success"]:
        problems.append("summary success does not add up to coverage")
    original = by_method["original"]["mean_em"]
    for comparison in stats["comparisons"]:
        if abs(comparison["baseline_mean"] - original) > 1e-12:
            problems.append(f"baseline mean drift for {comparison['method']}")
        if abs(comparison["method_mean"] - by_method[comparison["method"]]["mean_em"]) > 1e-12:
            problems.append(f"method mean drift for {comparison['method']}")
        if comparison["n_questions"] != summary["expected"]:
            problems.append(f"question count drift for {comparison['method']}")
    if stats["bootstrap"] != {"bootstrap_samples": 2000, "seed": 42, "confidence": 0.95}:
        problems.append("bootstrap settings are not the registered 2000/42/0.95")
    return {
        "kind": "stage3-offline-audit",
        "api_calls": 0,
        "elapsed_seconds": time.perf_counter() - started,
        "questions": summary["expected"],
        "slots": coverage["success"],
        "mean_em": {method: row["mean_em"] for method, row in by_method.items()},
        "longllmlingua_2x_minus_original": by_method["longllmlingua_2x"]["mean_em"] - original,
        "longllmlingua_4x_budget_satisfied_rate": by_method["longllmlingua_4x"]["budget_satisfied_rate"],
        "problems": problems,
    }


def main() -> int:
    report = audit()
    out = ROOT / "reports/stage3-supplement"
    out.mkdir(parents=True, exist_ok=True)
    (out / "offline-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("slots", "mean_em", "problems")}, indent=2))
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
