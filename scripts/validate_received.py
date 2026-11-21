"""Validate raw returned runs offline and export compact metrics for PR rebuilds."""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduction import common, data, methods, evaluation, recovery


def compact(row, source):
    keep = ("slot_id", "question_id", "position", "method", "status", "error", "fatal",
            "score_before_recovery", "score_after_recovery", "score", "actual_ratio",
            "origin_prompt_tokens", "prompt_tokens", "target_tokens", "budget_satisfied",
            "compression_seconds", "api_seconds", "total_pipeline_seconds", "cache_hit",
            "compression_cache_hit", "cache_key", "response_id", "usage", "generation_created_at")
    result = {k: row.get(k) for k in keep}
    result.update(source=source, recovery_seconds=row.get("recovery_stats", {}).get("seconds"),
                  recovery_changed=row.get("answer") != row.get("answer_after_recovery"),
                  telemetry={k: v for k, v in row.get("telemetry", {}).items()
                             if k in ("peak_allocated_bytes", "peak_reserved_bytes", "compression_measured", "qa_measured")})
    return result


def check_ablation_caches(directory, cache_root):
    from reproduction import api
    meta = common.read_json(directory / "run.json")
    checked_api = checked_compression = 0
    for row in common.read_jsonl(directory / "results.jsonl"):
        if row["status"] != "success": continue
        saved = common.read_json(cache_root / "api" / (row["cache_key"] + ".json"))
        payload = api.request_payload(meta["config"], row["prompt"])
        assert saved["payload"] == payload
        assert saved["cache_key"] == row["cache_key"] == api.cache_key(meta["config"], payload)
        assert saved["result"]["answer"] == row["answer"]
        assert saved["result"]["usage"] == row["usage"]
        checked_api += 1
        if row.get("compression_cache_key"):
            compressed = common.read_json(cache_root / "compress2" / (row["compression_cache_key"] + ".json"))
            assert compressed["result"]["prompt"] == row["prompt"]
            assert compressed["result"]["trace"] == row["trace"]
            checked_compression += 1
    return {"api_slots_checked": checked_api, "compression_slots_checked": checked_compression}


def validate(paths, data_root, output, cache_root=None):
    counter = methods.TokenCounter(data_root / "tokenizer/tokenizer.json")
    data.RAW = data_root / "raw"
    sources, report, metrics, cases = {}, {}, [], []
    for label, directory in paths.items():
        meta = common.read_json(directory / "run.json")
        config = meta["config"]
        expected_ids = common.read_json(ROOT / f"manifests/{config['split']}.json")["question_ids"]
        assert meta["question_ids"] == expected_ids
        expected = {f"{q}:{p}:{m}" for q in expected_ids for p in config["positions"] for m in config["methods"]}
        rows = common.read_jsonl(directory / "results.jsonl")
        latest = {r["slot_id"]: r for r in rows}
        assert set(latest) <= expected
        for r in rows:
            assert r["slot_id"] == f"{r['question_id']}:{r['position']}:{r['method']}"
        sources[label] = (meta, latest)
        report[label] = {"run_id": meta["run_id"], "expected": len(expected),
            "rows": len(rows), "unique_slots": len(latest), "superseded_attempts": len(rows)-len(latest),
            "success": sum(r["status"] == "success" for r in latest.values()),
            "failed": sum(r["status"] != "success" for r in latest.values()), "missing": len(expected - latest.keys()),
            "recovery_replayed": 0, "baseline_prompts_rebuilt": 0}
        if label == "ablation":
            assert set(latest) == expected and len(latest) == 3500
            full = config["methods"]["longllmlingua_2x"]
            for m, spec in config["methods"].items():
                if m.startswith("longllmlingua_2x_"):
                    assert sum(spec[k] != full[k] for k in full) == 1
    for position in common.POSITIONS:
        original = data.load_position(position)
        for label, (meta, records) in sources.items():
            config = meta["config"]
            for row in records.values():
                if row["position"] != position: continue
                if row["status"] != "success":
                    assert row.get("error")
                    metrics.append(compact(row, label)); continue
                raw = original[row["question_id"]]
                sample = data.visible_sample(raw)
                assert sorted(raw["answers"]) == sorted(row["answers"])
                assert row["config_hash"] == meta["config_hash"]
                assert row["implementation_hash"] == meta["implementation_hash"]
                assert row["prompt_hash"] == common.digest(row["prompt"])
                assert row["prompt_tokens"] == counter.count(row["prompt"])
                origin_prompt = methods.prompt(sample["question"], sample["documents"])
                origin_tokens = counter.count(origin_prompt)
                assert origin_tokens == row["origin_prompt_tokens"]
                spec = config["methods"][row["method"]]
                assert row["target_tokens"] == math.floor(origin_tokens / spec["ratio"])
                assert abs(row["actual_ratio"] - origin_tokens / row["prompt_tokens"]) < 1e-9
                assert row["budget_satisfied"] == (row["prompt_tokens"] <= row["target_tokens"])
                assert row["answer"] == row["answer_before_recovery"]
                b, a = evaluation.score(row["answer"], raw["answers"]), evaluation.score(row["answer_after_recovery"], raw["answers"])
                assert b == row["score_before_recovery"] and a == row["score_after_recovery"]
                assert row["score"] == (a if spec.get("recovery") else b)
                assert row["recovery_enabled"] == bool(spec.get("recovery"))
                if spec["kind"] in ("original", "bm25"):
                    built = methods.build_prompt(sample, row["method"], config, counter)
                    assert built["prompt"] == row["prompt"]
                    report[label]["baseline_prompts_rebuilt"] += 1
                else:
                    assert row["trace"]["restrict_enabled"] == spec["restrict"]
                    assert row["trace"]["used_doc_ids"] == row["selected_doc_ids"]
                    if spec["reorder_context"] == "original":
                        assert row["trace"]["used_doc_indices"] == sorted(row["trace"]["used_doc_indices"])
                if spec.get("recovery"):
                    text, stats = recovery.recover_answer(origin_prompt, row["prompt"], row["answer"], counter)
                    assert text == row["answer_after_recovery"]
                    for k in ("changed", "matched_spans", "matched_response_tokens", "recovered_tokens"):
                        assert stats[k] == row["recovery_stats"][k]
                    report[label]["recovery_replayed"] += 1
                else: assert row["answer_after_recovery"] == row["answer"]
                if label == "efficiency":
                    assert not row["cache_hit"] and not row["compression_cache_hit"]
                    assert row["telemetry"]["qa_measured"]
                if label == "ablation" and row["method"] == "longllmlingua_2x" and a != b:
                    cases.append({"question_id": row["question_id"], "position": position,
                        "question": raw["question"], "before_score": b, "after_score": a,
                        "before_first_line": row["answer"].split("\n")[0][:300],
                        "after_first_line": row["answer_after_recovery"].split("\n")[0][:300]})
                metrics.append(compact(row, label))
        print(f"Validated position {position}", flush=True)
    output.mkdir(parents=True, exist_ok=True)
    for label, (meta, _) in sources.items():
        common.atomic_json(output / f"{label}-run.json", meta)
    (output / "metrics.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in metrics), encoding="utf-8")
    cache_checks = check_ablation_caches(paths["ablation"], cache_root) if cache_root and "ablation" in paths else None
    common.atomic_json(output / "validation.json", {"passed": True, "runs": report, "cache_checks": cache_checks,
        "scope": "Raw answers rescored, budgets counted and recovery replayed; no compression or API rerun"})
    common.atomic_json(output / "recovery-cases.json", cases)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ablation", type=Path, required=True)
    p.add_argument("--efficiency", type=Path, required=True)
    p.add_argument("--data-root", type=Path, required=True)
    p.add_argument("--out", type=Path, default=ROOT / "reports/stage4-ablation-efficiency/inputs")
    p.add_argument("--cache-root", type=Path, help="Optional returned cache directory; check ablation caches only")
    a = p.parse_args()
    validate({"ablation": a.ablation, "efficiency": a.efficiency}, a.data_root, a.out, a.cache_root)
