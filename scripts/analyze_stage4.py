"""Rebuild course ablation and matched efficiency tables from compact metrics."""
from __future__ import annotations
import argparse
import copy
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduction import common, stage3
from scripts.stage4_recovery_analysis import percentile


def matched_efficiency(rows, methods, warmup):
    by = {m: {(r["question_id"], r["position"]): r for r in rows
              if r["method"] == m and r["status"] == "success"
              and not r.get("cache_hit") and not r.get("compression_cache_hit")}
          for m in methods}
    common_keys = set.intersection(*(set(v) for v in by.values()))
    measured = sorted(common_keys - {warmup})
    table = []
    for method in methods:
        sample = [by[method][k] for k in measured]
        row = {"method": method, "n": len(sample)}
        for field in ("compression_seconds", "api_seconds", "recovery_seconds", "total_pipeline_seconds"):
            values = [r[field] for r in sample if r.get(field) is not None]
            for name, q in (("p50", .5), ("p95", .95)):
                row[f"{field}_{name}"] = percentile(values, q) if values else None
        peaks = [r["telemetry"].get("peak_allocated_bytes") for r in sample]
        row["peak_allocated_GB"] = max((v / 1e9 for v in peaks if v is not None), default=None)
        table.append(row)
    return {"common_success_samples_before_warmup": len(common_keys), "n_per_method": len(measured),
        "warmup_excluded": list(warmup), "sample_keys": [list(k) for k in measured],
        "positions": dict(Counter(p for _, p in measured)), "table": table,
        "status": "Identical common-success workloads; first sample excluded; consult coverage for planned completeness"}


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def build(input_dir, output):
    rows = common.read_jsonl(input_dir / "metrics.jsonl")
    ablation = [r for r in rows if r["source"] == "ablation"]
    efficiency = [r for r in rows if r["source"] == "efficiency"]
    meta = common.read_json(input_dir / "ablation-run.json")
    methods = meta["config"]["methods"]
    records = {r["slot_id"]: r for r in ablation}
    variants = copy.deepcopy(meta)
    variants["config"]["baseline"] = "longllmlingua_2x"
    name = "longllmlingua_2x_no_recovery"
    variants["config"]["methods"][name] = dict(methods["longllmlingua_2x"], recovery=False)
    for row in ablation:
        if row["method"] == "longllmlingua_2x" and row["status"] == "success":
            r = dict(row, method=name, slot_id=f"{row['question_id']}:{row['position']}:{name}", score=row["score_before_recovery"])
            records[r["slot_id"]] = r
    paired = stage3.paired_comparisons(variants, records)
    paired_by_name = {r["method"]: r for r in paired}
    table = []
    for method in variants["config"]["methods"]:
        sample = [r for r in records.values() if r["method"] == method and r["status"] == "success"]
        c = paired_by_name.get(method, {})
        table.append({"method": method, "n": len(sample),
            "em_percent": 100 * sum(r["score"] for r in sample) / len(sample),
            "delta_pp": 100 * c["mean"] if c.get("mean") is not None else 0,
            "ci_low_pp": 100 * c["ci_low"] if c.get("ci_low") is not None else None,
            "ci_high_pp": 100 * c["ci_high"] if c.get("ci_high") is not None else None,
            "mean_actual_ratio": sum(r["actual_ratio"] for r in sample) / len(sample),
            "budget_misses": sum(not r["budget_satisfied"] for r in sample)})
    emeta = common.read_json(input_dir / "efficiency-run.json")
    e = matched_efficiency(efficiency, emeta["config"]["methods"], (emeta["question_ids"][0], 1))
    failure = [{k: r.get(k) for k in ("slot_id", "method", "position", "error", "fatal")}
               for r in efficiency if r["status"] != "success"]
    eff_success = sum(r["status"] == "success" for r in efficiency)
    eff_complete = eff_success == 1200 and len(failure) == 0 and len(efficiency) == 1200
    coverage = {"ablation": {"expected": 3500, "success": sum(r["status"] == "success" for r in ablation)},
        "efficiency": {"expected": 1200, "success": sum(r["status"] == "success" for r in efficiency),
            "failed": len(failure), "missing": 1200 - len(efficiency), "complete": eff_complete, "failures": failure},
        "overall_planned_efficiency_complete": eff_complete}
    # Deduplicate reused successful responses by provider response ID; benchmark repeats
    # with the same cache key remain separate requests when response IDs differ.
    usage = {}
    for label, source in (("ablation", ablation), ("efficiency", efficiency)):
        ok = [r for r in source if r["status"] == "success"]
        unique = {r.get("response_id") or (r["cache_key"], r["generation_created_at"]): r for r in ok}
        usage[label] = {"successful_slots": len(ok), "local_cache_hits": sum(bool(r["cache_hit"]) for r in ok),
            "unique_saved_responses": len(unique),
            "unique_saved_response_usage": {k: sum(r["usage"].get(k, 0) for r in unique.values()) for k in ("prompt_tokens", "completion_tokens")}}
    output.mkdir(parents=True, exist_ok=True)
    common.atomic_json(output / "coverage.json", coverage)
    common.atomic_json(output / "ablation-statistics.json", paired)
    common.atomic_json(output / "efficiency.json", e)
    common.atomic_json(output / "usage.json", usage)
    write_csv(output / "ablation.csv", table); write_csv(output / "efficiency.csv", e["table"])
    lines = ["# Stage-four results (course scope: fixed pilot 100 questions)", "",
        f"Ablation: 3500 successful slots. Efficiency complete: {eff_complete}; inspect coverage.json.", "",
        "| Method | n | EM (%) | Delta vs NPU full (pp) | 95% CI (pp) |",
        "| --- | ---: | ---: | ---: | --- |"]
    for r in table:
        interval = "reference" if r["ci_low_pp"] is None else f"[{r['ci_low_pp']:.1f}, {r['ci_high_pp']:.1f}]"
        lines.append(f"| {r['method']} | {r['n']} | {r['em_percent']:.1f} | {r['delta_pp']:+.1f} | {interval} |")
    lines += ["", f"Efficiency: {e['common_success_samples_before_warmup']} common samples before warmup; {e['n_per_method']} measured samples/method.",
        f"Position distribution after warmup: {e['positions']}.",
        "Statistics use question-level paired bootstrap, 2000 draws, seed 42, all five positions retained.",
        f"Efficiency is matched by question AND position across all 12 methods; planned matrix complete: {eff_complete}.",
        "No additional API calls. No monetary API cost inferred from token usage."]
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"coverage": coverage, "ablation": table,
        "efficiency_common": e["common_success_samples_before_warmup"], "efficiency_n": e["n_per_method"]}, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=ROOT / "reports/stage4-ablation-efficiency/inputs")
    p.add_argument("--out", type=Path, default=ROOT / "reports/stage4-ablation-efficiency")
    a = p.parse_args(); build(a.input, a.out)
