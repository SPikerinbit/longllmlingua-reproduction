"""Independently rescore and audit the received stage-three pilot, offline.

Inputs are a source package directory and its extracted full run directory.
The received code is used only for pure coverage/summary/statistics reconstruction.
Compression is not rerun; recovery is replayed using verified local resources.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduction import api, common, data, evaluation, methods, recovery


def equivalent(a, b):
    """Allow floating summation drift across Python versions; counts stay exact."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(equivalent(x, y) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
    return a == b


def audit(package, run_dir):
    meta = common.read_json(run_dir / "run.json")
    config = meta["config"]
    assert meta["stage"] == config["stage"] == 3
    assert meta["split"] == config["split"] == "pilot"
    manifest = common.read_json(ROOT / "manifests/pilot.json")
    assert meta["question_ids"] == manifest["question_ids"] and len(meta["question_ids"]) == 100
    assert config == common.read_json(package / "configs/stage3-pilot.json")
    files = {f"reproduction/{p.name}": hashlib.sha256(p.read_bytes()).hexdigest()
             for p in (package / "reproduction").glob("*.py")}
    files.update({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in list((ROOT / "vendor").rglob("*.py")) + list((ROOT / "vendor").rglob("*.prompt"))})
    impl = common.digest(files)
    assert impl == meta["implementation_hash"]
    assert common.digest({"config": config, "implementation": impl}) == meta["config_hash"]
    changed = []
    for p in (package / "reproduction").glob("*.py"):
        original = ROOT / "reproduction" / p.name
        if not original.exists() or p.read_bytes().replace(b"\r\n", b"\n") != original.read_bytes().replace(b"\r\n", b"\n"):
            changed.append(p.name)
    rows = common.read_jsonl(run_dir / "results.jsonl")
    records = {r["slot_id"]: r for r in rows}
    expected = {f"{q}:{p}:{m}" for q in meta["question_ids"]
                for p in common.POSITIONS for m in config["methods"]}
    assert len(rows) == len(records) == len(expected) == 3500 and set(records) == expected
    counter = methods.TokenCounter()
    grouped, unique_requests = defaultdict(list), {}
    replayed, rebuilt, overshoots = 0, 0, []
    for position in common.POSITIONS:
        source = data.load_position(position)
        for qid in meta["question_ids"]:
            raw = source[qid]
            sample = data.visible_sample(raw)
            original_prompt = methods.prompt(sample["question"], sample["documents"])
            original_tokens = counter.count(original_prompt)
            for method, spec in config["methods"].items():
                r = records[f"{qid}:{position}:{method}"]
                assert r["status"] == "success" and r["finish_reason"] == "stop"
                assert r["question_id"] == qid and r["position"] == position and r["method"] == method
                assert r["stage"] == 3 and r["split"] == "pilot"
                assert r["question"] == raw["question"] and sorted(r["answers"]) == sorted(raw["answers"])
                assert r["implementation_hash"] == impl and r["config_hash"] == meta["config_hash"]
                assert r["model"] == config["model"] and r["endpoint"] == config["base_url"]
                assert r["tokenizer"] == config["tokenizer"] and r["upstream"] == config["upstream"]
                assert r["prompt_hash"] == common.digest(r["prompt"])
                assert r["prompt_tokens"] == counter.count(r["prompt"])
                assert r["origin_prompt_tokens"] == original_tokens
                assert r["target_ratio"] == spec["ratio"]
                assert r["target_tokens"] == math.floor(original_tokens / spec["ratio"])
                assert abs(r["actual_ratio"] - original_tokens / r["prompt_tokens"]) < 1e-9
                assert r["budget_satisfied"] == (r["prompt_tokens"] <= r["target_tokens"])
                assert r["cache_key"] == api.cache_key(config, api.request_payload(config, r["prompt"]))
                assert r["answer"] == r["answer_before_recovery"]
                before = evaluation.score(r["answer_before_recovery"], raw["answers"])
                after = evaluation.score(r["answer_after_recovery"], raw["answers"])
                assert before == r["score_before_recovery"] and after == r["score_after_recovery"]
                assert r["recovery_enabled"] == bool(spec.get("recovery"))
                assert r["score"] == (after if spec.get("recovery") else before)
                if spec["kind"] in ("original", "bm25"):
                    built = methods.build_prompt(sample, method, config, counter)
                    assert built["prompt"] == r["prompt"]
                    assert built["selected_doc_ids"] == r["selected_doc_ids"]
                    rebuilt += 1
                else:
                    assert r["trace"]["restrict_enabled"] == spec["restrict"]
                    assert spec["reorder_context"] == "original"
                    assert r["trace"]["used_doc_indices"] == sorted(r["trace"]["used_doc_indices"])
                if spec.get("recovery"):
                    text, stats = recovery.recover_answer(original_prompt, r["prompt"], r["answer"], counter)
                    assert text == r["answer_after_recovery"], f"Recovery mismatch {r['slot_id']}"
                    for key in ("matched_spans", "matched_response_tokens", "recovered_tokens", "changed"):
                        assert stats[key] == r["recovery_stats"][key]
                    replayed += 1
                else:
                    assert r["answer_after_recovery"] == r["answer"]
                if not r["budget_satisfied"]:
                    overshoots.append({"slot_id": r["slot_id"], "tokens": r["prompt_tokens"], "target": r["target_tokens"]})
                if r["cache_key"] in unique_requests:
                    first = unique_requests[r["cache_key"]]
                    assert first["answer"] == r["answer"] and first["usage"] == r["usage"]
                else:
                    unique_requests[r["cache_key"]] = r
                grouped[method].append(r)
        print(f"Verified position {position}: scores, tokens, baselines and recovery", flush=True)
    spec = importlib.util.spec_from_file_location("reproduction.stage3_received", package / "reproduction/stage3.py")
    stage3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stage3)
    report_dir = package / "reports/stage3-pilot"
    assert equivalent(stage3.summarize_records(meta, records), common.read_json(report_dir / "summary.json"))
    assert stage3.coverage_from_records(meta, records) == common.read_json(report_dir / "coverage.json")
    comparisons = stage3.paired_comparisons(meta, records)
    assert comparisons == common.read_json(report_dir / "stats.json")["comparisons"]
    return {
        "passed": True, "scope": "Independent pilot rescore and stored output verification; no compression/API rerun",
        "run_id": meta["run_id"], "split": "pilot", "questions": 100,
        "slots": len(rows), "success": len(rows), "failed": 0, "missing": 0,
        "changed_or_new_source_files": changed, "implementation_hash": impl,
        "baseline_prompts_rebuilt": rebuilt, "recovery_replayed": replayed,
        "summary_reproduced": True, "coverage_reproduced": True, "paired_statistics_reproduced": True,
        "comparisons_vs_original": comparisons,
        "methods": [{"method": name, "slots": len(v),
            "em_before": sum(r["score_before_recovery"] for r in v) / len(v),
            "em_after": sum(r["score_after_recovery"] for r in v) / len(v),
            "actual_ratio": sum(r["actual_ratio"] for r in v) / len(v),
            "budget_misses": sum(not r["budget_satisfied"] for r in v),
            "recovery_changed": sum(r["answer"] != r["answer_after_recovery"] for r in v),
            "recovery_helped": sum(r["score_after_recovery"] > r["score_before_recovery"] for r in v),
            "recovery_harmed": sum(r["score_after_recovery"] < r["score_before_recovery"] for r in v)} for name, v in grouped.items()],
        "budget_misses": overshoots,
        "unique_request_keys": len(unique_requests),
        "local_api_cache_hit_slots": sum(r["cache_hit"] for r in rows),
        "non_cache_hit_success_slots": sum(not r["cache_hit"] for r in rows),
        "slot_usage": {k: sum(r["usage"].get(k, 0) for r in rows) for k in ("prompt_tokens", "completion_tokens")},
        "unique_response_usage": {k: sum(r["usage"].get(k, 0) for r in unique_requests.values()) for k in ("prompt_tokens", "completion_tokens")},
        "response_models": dict(Counter(r["response_model"] for r in rows)),
        "system_fingerprints": dict(Counter(r["system_fingerprint"] for r in rows)),
        "main_present": False, "new_api_requests": 0, "new_compression_calls": 0,
        "limitations": ["Source API/compression caches not included in this package",
                        "No exact GPU model or cloud session manifest supplied",
                        "Main 500-question matrix absent; pilot is not formal main acceptance"],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("package", type=Path)
    p.add_argument("run_dir", type=Path)
    p.add_argument("--out", type=Path, default=ROOT / "outputs/member3-handoff-verification.json")
    a = p.parse_args()
    result = audit(a.package, a.run_dir)
    common.atomic_json(a.out, result)
    print(json.dumps({k: v for k, v in result.items() if k != "budget_misses"}, indent=2))


if __name__ == "__main__":
    main()
