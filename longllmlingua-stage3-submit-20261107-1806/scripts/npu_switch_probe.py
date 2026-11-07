"""Mechanism probe: compress one smoke sample under each switch setting.

Runs on the GPU/NPU host that holds the Llama-2 weights; it never sends API
requests and never writes tracked files. Each variant flips exactly one switch
relative to the main-matrix LongLLMLingua configuration, so the resulting trace
(doc ranking, retained documents, dynamic ratios, text preview) is direct
behavioural evidence for that switch.

Usage (on the ModelArts host, code at /home/ma-user/work/cp):
    PYTHONPATH=. python scripts/npu_switch_probe.py --out data/scratch/npu/switch_probe.json
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reproduction import common, compression, data, methods
from reproduction.stage2 import load_stage2_config, _questions

VARIANTS = (
    # (probe name, source method in config, one-switch override)
    ("longllmlingua_2x", "longllmlingua_2x", {}),
    ("longllmlingua_no_restrict", "longllmlingua_2x", {"restrict": False}),
    ("longllmlingua_no_condition_compare", "longllmlingua_2x", {"condition_compare": False}),
    ("longllmlingua_no_dynamic", "longllmlingua_2x",
     {"dynamic_context_compression_ratio": 0.0}),
    ("longllmlingua_reorder_sort", "longllmlingua_2x", {"reorder_context": "sort"}),
    ("llmlingua_2x", "llmlingua_2x", {}),
)


def summarize_result(name, result):
    trace = result["trace"]
    return {
        "variant": name,
        "restrict": trace.get("restrict_enabled"),
        "prompt_tokens": result["compressed_tokens"],
        "origin_tokens": result["origin_tokens"],
        "actual_ratio": result["actual_ratio"],
        "budget_satisfied": result["budget_satisfied"],
        "attempts": trace.get("attempts"),
        "used_doc_indices": trace.get("used_doc_indices"),
        "dropped_doc_indices": [index for index, doc in enumerate(trace.get("document_scores", []))
                                if not doc.get("retained")],
        "document_scores": trace.get("document_scores"),
        "dynamic_ratios": trace.get("dynamic_ratios"),
        "preview": trace.get("compressed_context_preview"),
        "library_origin_tokens": trace.get("library_origin_tokens"),
        "library_compressed_tokens": trace.get("library_compressed_tokens"),
        "library_ratio_label": trace.get("library_ratio_label"),
        "compression_seconds": result["compression_seconds"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=ROOT / "data/scratch/npu/switch_probe.json")
    parser.add_argument("--question-index", type=int, default=0)
    args = parser.parse_args(argv)

    config = load_stage2_config()
    counter = methods.TokenCounter()
    compressor, compressor_meta = compression.load_compressor(config, counter)
    questions = _questions(config)
    question_id, position, row = questions[args.question_index]
    sample = data.visible_sample(row)

    probe = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "compressor": compressor_meta,
        "sample": {"question_id": question_id, "position": position,
                   "question": sample["question"],
                   "documents": len(sample["documents"]),
                   "original_prompt_tokens": counter.count(
                       methods.prompt(sample["question"], sample["documents"]))},
        "base_config": {name: config["methods"][name]
                        for name in ("llmlingua_2x", "longllmlingua_2x")},
        "runs": [],
    }
    for name, source, override in VARIANTS:
        variant_config = copy.deepcopy(config)
        spec = dict(variant_config["methods"][source])
        spec.update(override)
        variant_config["methods"] = {name: spec}
        started = time.perf_counter()
        result = compression.compress_sample(compressor, variant_config, name, sample, counter)
        record = summarize_result(name, result)
        record["wall_seconds"] = time.perf_counter() - started
        record["spec"] = spec
        probe["runs"].append(record)
        print(f"{name}: {record['prompt_tokens']} tokens ratio={record['actual_ratio']:.2f} "
              f"used={record['used_doc_indices']} in {record['compression_seconds']:.1f}s",
              flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    common.atomic_json(args.out, probe)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
