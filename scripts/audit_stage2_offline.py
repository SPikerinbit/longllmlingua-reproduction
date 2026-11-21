#!/usr/bin/env python3
"""Check committed stage-two smoke records against each other. No compressor."""

from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(root: Path = ROOT) -> dict:
    started = time.perf_counter()
    verification = json.loads((root / "reports/stage2-smoke/verification.json").read_text())
    summary = json.loads((root / "reports/stage2-smoke/summary.json").read_text())
    groups = summary["groups"]
    success = sum(group["success"] for group in groups)
    expected = sum(group["expected"] for group in groups)
    failed = sum(group["failed"] for group in groups)
    missing = sum(group["missing"] for group in groups)
    means = {}
    for group in groups:
        bucket = means.setdefault(group["method"], {"score": 0.0, "n": 0})
        bucket["score"] += group["best_subspan_em"] * group["success"]
        bucket["n"] += group["success"]
    official = {method: bucket["score"] / bucket["n"] for method, bucket in means.items()}
    misses = verification["budget_misses"]
    problems = []
    if success != verification["rows"] or expected != verification["expected_slots"]:
        problems.append("summary coverage does not match verification row counts")
    if verification["budget_satisfied"] + len(misses) != verification["rows"]:
        problems.append("budget_satisfied plus listed misses does not equal rows")
    if any(miss["tokens"] <= miss["target"] for miss in misses):
        problems.append("a listed budget miss is not actually over target")
    if failed or missing:
        problems.append("summary has failed or missing slots")
    return {
        "kind": "stage2-offline-audit",
        "api_calls": 0,
        "compression_rerun": False,
        "elapsed_seconds": time.perf_counter() - started,
        "run_id": verification["run_id"],
        "rows": verification["rows"],
        "budget_satisfied": verification["budget_satisfied"],
        "budget_misses": misses,
        "official_mean_score": official,
        "problems": problems,
    }


def main() -> int:
    report = audit()
    out = ROOT / "reports/stage2-supplement"
    out.mkdir(parents=True, exist_ok=True)
    (out / "offline-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("rows", "budget_satisfied", "official_mean_score", "problems")}, indent=2))
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
