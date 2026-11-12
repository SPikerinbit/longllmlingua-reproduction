"""910B launcher around the reviewed stage-three engine; no algorithm changes."""
from __future__ import annotations
import argparse
import copy
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduction import common, api, data, methods, compression, stage3


def environment():
    result = {"python": sys.version, "packages": {}}
    for name in ("torch", "torch-npu", "transformers", "tokenizers", "numpy", "accelerate"):
        try: result["packages"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: result["packages"][name] = None
    try:
        import torch
        import torch_npu  # registers torch.npu
        result.update(npu_available=torch.npu.is_available(), npu_name=torch.npu.get_device_name(0))
    except (ImportError, RuntimeError) as exc:
        result.update(npu_available=False, npu_error=str(exc))
    return result


def seed():
    count = 0
    for file in sorted((ROOT / "seed").glob("*/results.jsonl")):
        meta = common.read_json(file.parent / "run.json")
        for row in common.read_jsonl(file):
            if row.get("status", "success") != "success" or row.get("finish_reason") != "stop": continue
            payload = api.request_payload(meta["config"], row["prompt"])
            key = api.cache_key(meta["config"], payload)
            assert key == row["cache_key"]
            path = ROOT / "cache/api" / (key + ".json")
            if path.exists(): continue
            fields = ("usage", "response_model", "response_id", "system_fingerprint", "finish_reason", "api_seconds", "attempts")
            result = {k: row.get(k) for k in fields}
            result.update(answer=row["answer"], created_at=row["generation_created_at"])
            common.atomic_json(path, {"cache_key": key, "payload": payload, "endpoint": meta["config"]["base_url"],
                                     "result": result, "provenance": {"run_id": meta["run_id"], "slot_id": row["slot_id"], "imported": True}})
            count += 1
    print(f"Imported {count} saved successful QA responses; no API requests")


def latest(config_path):
    return ROOT / "outputs/cloud" / (Path(config_path).stem + "-latest.json")


def run(config_path, limit):
    import torch
    import torch_npu
    config = stage3.load_stage3_config(config_path)
    assert config["compressor"]["device"] == "npu:0"
    counter = methods.TokenCounter()
    sample = data.visible_sample(next(data.iter_samples(config))[2])
    # Load and warm outside per-slot timing, including when resumed.
    compressor, model_meta = compression.load_compressor(config, counter)
    warm_config = copy.deepcopy(config)
    warm_method = "longllmlingua_2x"
    for _ in range(2): compression.compress_sample(compressor, warm_config, warm_method, sample, counter)
    torch.npu.synchronize()
    model_meta.update(model_revision=config["compressor"]["model_revision"], warmup_compressions=2)
    original_compress, original_append = compression.compress_sample, common.append_jsonl
    original_load = compression.load_compressor
    from reproduction import stage2
    original_cached_compress, original_cached_qa = stage2._compress_cached, api.cached_completion
    last = {}
    def measured(*args, **kwargs):
        torch.npu.synchronize(); torch.npu.reset_peak_memory_stats()
        started = time.perf_counter()
        result = original_compress(*args, **kwargs)
        torch.npu.synchronize()
        result["compression_seconds"] = time.perf_counter() - started
        last.update(peak_allocated_bytes=torch.npu.max_memory_allocated(),
                    peak_reserved_bytes=torch.npu.max_memory_reserved())
        return result
    def append(path, row):
        if Path(path).name == "results.jsonl":
            actual = row.get("kind") in ("llmlingua", "longllmlingua") and not row.get("compression_cache_hit")
            row["telemetry"] = dict(last) if actual else {}
            row["telemetry"].update(environment_file="outputs/cloud/environment.json",
                model_loaded_and_warmed_before_slots=True, concurrency=1,
                compression_measured=actual, qa_measured=not bool(row.get("cache_hit")),
                experiment_phase=config.get("experiment_phase"), model_revision=config["compressor"]["model_revision"])
        original_append(path, row)
    compression.compress_sample = measured
    compression.load_compressor = lambda *a, **k: (compressor, model_meta)
    common.append_jsonl = append
    if config.get("benchmark_no_cache"):
        def fresh_compress(compressor, cfg, method, sample, counter):
            return compression.compress_sample(compressor, cfg, method, sample, counter), False, stage2._compression_key(cfg, method, sample)
        def fresh_qa(cfg, payload, client, provenance, **kwargs):
            return {"cache_key": api.cache_key(cfg, payload), "result": client.complete(payload), "provenance": provenance}, False
        stage2._compress_cached, api.cached_completion = fresh_compress, fresh_qa
    common.atomic_json(ROOT / "outputs/cloud/environment.json", environment())
    try:
        directory, _ = stage3.run(config, limit=limit)
        common.atomic_json(latest(config_path), {"run_dir": str(directory.relative_to(ROOT)), "config": str(config_path)})
        report = stage3.summarize(directory)
        print(f"RUN_DIR={directory}")
        return 0 if report["complete"] else 2
    finally:
        compression.compress_sample, compression.load_compressor = original_compress, original_load
        common.append_jsonl = original_append
        stage2._compress_cached, api.cached_completion = original_cached_compress, original_cached_qa


def analyze(config_path):
    pointer = common.read_json(latest(config_path))
    directory = ROOT / pointer["run_dir"]
    meta = common.read_json(directory / "run.json")
    report = stage3.summarize(directory)
    stage3.stats(directory)
    if meta["config"].get("experiment_phase") == "ablation":
        paired_meta = copy.deepcopy(meta)
        paired_meta["config"]["baseline"] = "longllmlingua_2x"
        common.atomic_json(directory / "ablation-vs-full.json", stage3.paired_comparisons(paired_meta, stage3.load_records(directory / "results.jsonl")))
    from scripts.stage4_recovery_analysis import run as recovery_analysis
    recovery_analysis(directory, directory / "recovery-analysis")
    rows = {}
    for row in common.read_jsonl(directory / "results.jsonl"): rows[row["slot_id"]] = row
    if meta["config"].get("experiment_phase") == "ablation":
        traces = {}
        for method in meta["config"]["methods"]:
            if not method.startswith("longllmlingua_2x_"): continue
            pairs = [(r, rows.get(f"{r['question_id']}:{r['position']}:longllmlingua_2x"))
                     for r in rows.values() if r["method"] == method and r["status"] == "success"]
            pairs = [(a, b) for a, b in pairs if b and b["status"] == "success"]
            traces[method] = {"paired_slots": len(pairs),
                "prompt_changed": sum(a["prompt_hash"] != b["prompt_hash"] for a, b in pairs),
                "documents_changed": sum(a["selected_doc_ids"] != b["selected_doc_ids"] for a, b in pairs),
                "document_scores_changed": sum(a["trace"]["document_scores"] != b["trace"]["document_scores"] for a, b in pairs),
                "dynamic_offsets_changed": sum(a["trace"]["dynamic_ratios"] != b["trace"]["dynamic_ratios"] for a, b in pairs)}
        common.atomic_json(directory / "mechanism-checks.json", traces)
    efficiency = {}
    for method in meta["config"]["methods"]:
        values = [r for r in rows.values() if r["method"] == method and r["status"] == "success"]
        # Exclude the first fresh sample of each method for API warmup; retain counts.
        fresh = [r for r in values if not r.get("cache_hit") and not r.get("compression_cache_hit")][1:]
        from scripts.stage4_recovery_analysis import percentile
        timings = {}
        for field in ("compression_seconds", "api_seconds", "total_pipeline_seconds"):
            v = [r[field] for r in fresh if r.get(field) is not None]
            timings[field] = {"n": len(v), "p50": percentile(v, .5) if v else None, "p95": percentile(v, .95) if v else None}
        v = [r.get("recovery_stats", {}).get("seconds") for r in fresh]
        v = [x for x in v if x is not None]
        timings["recovery_seconds"] = {"n": len(v), "p50": percentile(v, .5) if v else None, "p95": percentile(v, .95) if v else None}
        peaks = [r.get("telemetry", {}).get("peak_allocated_bytes") for r in fresh]
        timings["peak_allocated_bytes"] = max((x for x in peaks if x is not None), default=None)
        timings.update(success=len(values), api_cache_hits=sum(bool(r.get("cache_hit")) for r in values),
                       compression_cache_hits=sum(bool(r.get("compression_cache_hit")) for r in values))
        efficiency[method] = timings
    common.atomic_json(directory / "efficiency.json", efficiency)
    print(f"Analysis: {directory}; complete={report['complete']}")
    return 0 if report["complete"] else 2


def export(destination):
    # Explicit selection excludes .env, model weights and raw datasets.
    with tarfile.open(destination, "w:gz") as archive:
        for name in ("outputs", "cache/api", "cache/compress2", "configs", "reproduction", "scripts", "docs", "manifests", "vendor", "logs"):
            path = ROOT / name
            if path.exists(): archive.add(path, arcname=name, filter=lambda info: None if "__pycache__" in info.name else info)
    print(destination)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("check", "seed", "run", "analyze", "export"))
    p.add_argument("--config", default="configs/cloud/main.json")
    p.add_argument("--limit", type=int)
    p.add_argument("--out", default="stage4-return.tar.gz")
    a = p.parse_args()
    if a.command == "check":
        e = environment(); common.atomic_json(ROOT / "outputs/cloud/environment.json", e)
        print(json.dumps(e, indent=2)); return 0 if e.get("npu_available") else 1
    if a.command == "seed": seed()
    elif a.command == "run": return run(a.config, a.limit)
    elif a.command == "analyze": return analyze(a.config)
    elif a.command == "export": export(Path(a.out).resolve())
    return 0


if __name__ == "__main__": sys.exit(main())
