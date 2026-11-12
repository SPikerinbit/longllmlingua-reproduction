"""Validate the received stage-two archive offline, leaving original outputs intact.

Requires its verified raw data and tokenizer installed under data/raw and
data/tokenizer. Never loads the compressor or sends a network request.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduction import api, common, data, evaluation, methods, recovery


def verify(handoff):
    runtime = handoff / "scratch/modelarts"
    runs = list((runtime / "outputs/stage2").glob("*/run.json"))
    if len(runs) != 1:
        raise ValueError("Expected one stage-two run; choose the archive explicitly")
    run_dir = runs[0].parent
    meta = common.read_json(runs[0])
    config = meta["config"]
    files = sorted((ROOT / "reproduction").glob("*.py"))
    files += sorted((ROOT / "vendor").rglob("*.py"))
    files += sorted((ROOT / "vendor").rglob("*.prompt"))
    portable_hash = common.digest({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in files})
    assert portable_hash == meta["implementation_hash"], "Code differs beyond path separators"
    assert common.digest({"config": config, "implementation": portable_hash}) == meta["config_hash"]
    assert config == common.read_json(ROOT / "configs/stage2.json")
    manifest = common.read_json(ROOT / f"manifests/{config['split']}.json")
    assert sorted(meta["question_ids"]) == sorted(manifest["question_ids"])
    expected = {f"{qid}:{p}:{m}" for qid in manifest["question_ids"]
                for p in config["positions"] for m in config["methods"]}
    records = common.read_jsonl(run_dir / "results.jsonl")
    latest = {r["slot_id"]: r for r in records}
    assert set(latest) == expected
    counter = methods.TokenCounter()
    groups, replayed, unique_requests, budget_misses = defaultdict(list), 0, {}, []
    reference = None
    population = {}
    for position in config["positions"]:
        source = data.load_position(position)
        population[position] = len(source)
        aligned = {qid: (row["question"], sorted(row["answers"]), data.document_set(row))
                   for qid, row in source.items()}
        if reference is None:
            reference = aligned
        else:
            assert aligned == reference, "Question/answer/document sets differ across positions"
        for qid in manifest["question_ids"]:
            original = source[qid]
            visible = data.visible_sample(original)
            original_prompt = methods.prompt(visible["question"], visible["documents"])
            origin_tokens = counter.count(original_prompt)
            for method, spec in config["methods"].items():
                r = latest[f"{qid}:{position}:{method}"]
                assert r["status"] == "success" and r["finish_reason"] == "stop"
                assert r["question_id"] == qid and r["position"] == position and r["method"] == method
                assert sorted(r["answers"]) == sorted(original["answers"])
                assert r["config_hash"] == meta["config_hash"] and r["implementation_hash"] == portable_hash
                assert r["model"] == config["model"] and r["endpoint"] == config["base_url"]
                assert r["tokenizer"] == config["tokenizer"] and r["upstream"] == config["upstream"]
                assert common.digest(r["prompt"]) == r["prompt_hash"]
                assert counter.count(r["prompt"]) == r["prompt_tokens"]
                assert origin_tokens == r["origin_prompt_tokens"]
                assert r["target_tokens"] == math.floor(origin_tokens / spec["ratio"])
                assert abs(origin_tokens / r["prompt_tokens"] - r["actual_ratio"]) < 1e-9
                assert r["budget_satisfied"] == (r["prompt_tokens"] <= r["target_tokens"])
                if not r["budget_satisfied"]:
                    budget_misses.append({"slot_id": r["slot_id"], "tokens": r["prompt_tokens"],
                                          "target": r["target_tokens"]})
                cached = common.read_json(runtime / f"cache/compress2/{r['compression_cache_key']}.json")
                assert cached["key"] == r["compression_cache_key"]
                assert cached["result"]["prompt"] == r["prompt"]
                assert cached["result"]["trace"] == r["trace"]
                assert r["trace"]["restrict_enabled"] == spec["restrict"]
                assert r["trace"]["budget_mode"] == config["compressor"]["budget_mode"]
                assert r["recovery_enabled"] == spec["recovery"]
                saved = common.read_json(runtime / f"cache/api/{r['cache_key']}.json")
                payload = api.request_payload(config, r["prompt"])
                assert saved["cache_key"] == r["cache_key"] == api.cache_key(config, payload)
                assert saved["payload"] == payload and saved["endpoint"] == config["base_url"]
                assert saved["result"]["answer"] == r["answer"] == r["answer_before_recovery"]
                assert saved["result"]["usage"] == r["usage"]
                assert saved["result"]["finish_reason"] == "stop"
                unique_requests[r["cache_key"]] = saved["result"]
                before = evaluation.score(r["answer_before_recovery"], original["answers"])
                after = evaluation.score(r["answer_after_recovery"], original["answers"])
                assert before == r["score_before_recovery"] and after == r["score_after_recovery"]
                assert r["score"] == (after if spec["recovery"] else before)
                if spec["recovery"]:
                    text, stats = recovery.recover_answer(original_prompt, r["prompt"], r["answer"], counter)
                    assert text == r["answer_after_recovery"], f"Recovery differs: {r['slot_id']}"
                    for key in ("matched_spans", "matched_response_tokens", "recovered_tokens", "changed"):
                        assert stats[key] == r["recovery_stats"][key]
                    replayed += 1
                else:
                    assert r["answer_after_recovery"] == r["answer_before_recovery"]
                groups[method].append(r)
    summary = common.read_json(run_dir / "summary.json")
    for cell in summary["groups"]:
        rows = [r for r in groups[cell["method"]] if r["position"] == cell["position"]]
        assert len(rows) == cell["expected"] == cell["success"]
        assert sum(r["score"] for r in rows) / len(rows) == cell["best_subspan_em"]
    return {
        "passed": True, "scope": "Offline artifact consistency and recovery replay; no compression rerun",
        "run_id": meta["run_id"], "split": config["split"], "rows": len(records),
        "unique_slots": len(latest), "expected_slots": len(expected),
        "full_population_alignment": population, "recovery_replayed_slots": replayed,
        "portable_implementation_hash": portable_hash,
        "hash_note": "Stored Linux hash reproduced by POSIX path separators with unchanged file bytes",
        "unique_api_requests": len(unique_requests), "budget_satisfied": len(latest) - len(budget_misses),
        "budget_misses": budget_misses,
        "unique_saved_response_usage": {
            key: sum(r.get("usage", {}).get(key, 0) for r in unique_requests.values())
            for key in ("prompt_tokens", "completion_tokens")},
        "logical_slot_usage_including_reused_responses": {
            key: sum(r.get("usage", {}).get(key, 0) for r in latest.values())
            for key in ("prompt_tokens", "completion_tokens")},
        "local_api_cache_hit_slots": sum(r["cache_hit"] for r in latest.values()),
        "methods": [{"method": m, "slots": len(rows),
            "em_before": sum(r["score_before_recovery"] for r in rows) / len(rows),
            "em_after": sum(r["score_after_recovery"] for r in rows) / len(rows),
            "changed_answers": sum(r["answer_before_recovery"] != r["answer_after_recovery"] for r in rows),
            "mean_actual_ratio": sum(r["actual_ratio"] for r in rows) / len(rows)} for m, rows in groups.items()],
        "new_api_requests": 0, "new_compression_calls": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff_data", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs/stage4/member2-handoff-verification.json")
    args = parser.parse_args()
    report = verify(args.handoff_data)
    common.atomic_json(args.out, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
