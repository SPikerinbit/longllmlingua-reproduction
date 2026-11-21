#!/usr/bin/env python3
"""Check committed stage-four tables against each other. Does not rewrite them."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/stage4-ablation-efficiency"


def audit(root: Path = ROOT) -> dict:
    started = time.perf_counter()
    report_dir = root / "reports/stage4-ablation-efficiency"
    coverage = json.loads((report_dir / "coverage.json").read_text())
    stats = json.loads((report_dir / "ablation-statistics.json").read_text())
    with (report_dir / "ablation.csv").open(encoding="utf-8") as handle:
        ablation = list(csv.DictReader(handle))
    with (report_dir / "efficiency.csv").open(encoding="utf-8") as handle:
        efficiency = list(csv.DictReader(handle))
    problems = []
    if coverage["ablation"]["success"] != coverage["ablation"]["expected"]:
        problems.append("ablation coverage is incomplete")
    if coverage["efficiency"]["success"] != coverage["efficiency"]["expected"] or coverage["efficiency"]["failed"] or coverage["efficiency"]["missing"]:
        problems.append("efficiency coverage is incomplete")
    by_csv = {row["method"]: row for row in ablation}
    if "longllmlingua_2x" not in by_csv or int(by_csv["longllmlingua_2x"]["n"]) != 500:
        problems.append("full-method row missing from ablation csv")
    for row in stats:
        csv_row = by_csv.get(row["method"])
        if csv_row is None or abs(float(csv_row["em_percent"]) - 100 * row["method_mean"]) > 1e-6:
            problems.append(f"ablation csv does not match statistics for {row['method']}")
        if int(csv_row["n"]) != 500:
            problems.append(f"sample size drift for {row['method']}")
        if abs(row["baseline_mean"] - 0.826) > 1e-12:
            problems.append(f"baseline drift for {row['method']}")
    if any(int(row["n"]) != 99 for row in efficiency):
        problems.append("efficiency rows are not all n=99")
    cases = json.loads((report_dir / "inputs/recovery-cases.json").read_text())
    if len(cases) != 3 or any(case["before_score"] != 1.0 or case["after_score"] != 0.0 for case in cases):
        problems.append("recovery case file is not the three recorded regressions")
    return {
        "kind": "stage4-offline-audit",
        "api_calls": 0,
        "compression_rerun": False,
        "elapsed_seconds": time.perf_counter() - started,
        "ablation_slots": coverage["ablation"]["success"],
        "efficiency_slots": coverage["efficiency"]["success"],
        "em_percent": {row["method"]: float(row["em_percent"]) for row in ablation},
        "recovery_regressions": len(cases),
        "problems": problems,
    }


def main() -> int:
    report = audit()
    out = ROOT / "reports/stage4-supplement"
    out.mkdir(parents=True, exist_ok=True)
    (out / "offline-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("ablation_slots", "efficiency_slots", "recovery_regressions", "problems")}, indent=2))
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
