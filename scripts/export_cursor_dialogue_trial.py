#!/usr/bin/env python3
"""Write the minimal cursor_dialogue blind trial. No model is called.

The blind directory must not contain gold answers. Scoring labels are written
only under trial/gold/.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reproduction.common import read_json
from reproduction.data import question_id, visible_sample
from reproduction.methods import TokenCounter, build_prompt

TRIAL = (
    ("ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc", 1, "original"),
    ("ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc", 1, "bm25_2x"),
    ("ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc", 1, "bm25_4x"),
)


def load_position(path: Path) -> dict[str, dict]:
    rows = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            rows[question_id(item)] = item
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "reports/cursor_dialogue")
    args = parser.parse_args()
    config = read_json(ROOT / "configs/stage1.json")
    smoke = read_json(ROOT / "manifests/smoke.json")
    counter = TokenCounter(args.tokenizer)
    position_rows = load_position(args.raw_dir / "nq-open-20_total_documents_gold_at_0.jsonl.gz")
    blind_dir = args.out / "trial/blind"
    gold_dir = args.out / "trial/gold"
    blind_dir.mkdir(parents=True, exist_ok=True)
    gold_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    gold = []
    for qid, position, method in TRIAL:
        if qid not in smoke["question_ids"]:
            raise ValueError("trial question is not in the fixed smoke list")
        item = position_rows[qid]
        built = build_prompt(visible_sample(item), method, config, counter)
        slot_id = f"{qid}:{position}:{method}"
        filename = slot_id.replace(":", "__") + ".txt"
        prompt_path = blind_dir / filename
        prompt_path.write_text(built["prompt"], encoding="utf-8")
        prompt_sha = hashlib.sha256(built["prompt"].encode()).hexdigest()
        manifest.append({
            "slot_id": slot_id,
            "question_id": qid,
            "position": position,
            "method": method,
            "prompt_sha256": prompt_sha,
            "prompt_file": f"trial/blind/{filename}",
            "origin_tokens": built["origin_tokens"],
            "prompt_tokens": built["compressed_tokens"],
            "target_tokens": built["target_tokens"],
        })
        gold.append({
            "slot_id": slot_id,
            "question_id": qid,
            "position": position,
            "method": method,
            "question": item["question"],
            "answers": item["answers"],
        })
    design = [
        {"question_id": qid, "position": position, "method": method,
         "slot_id": f"{qid}:{position}:{method}"}
        for qid in smoke["question_ids"]
        for position in config["positions"]
        for method in config["methods"]
    ]
    (args.out / "design-slots.json").write_text(
        json.dumps({"split": "smoke", "slots": len(design), "items": design}, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.out / "trial/manifest.json").write_text(
        json.dumps({"experiment": "cursor_dialogue", "contains_gold": False, "slots": manifest},
                   indent=2) + "\n",
        encoding="utf-8",
    )
    (gold_dir / "labels.json").write_text(
        json.dumps({"contains_gold": True, "do_not_send_to_answerer": True, "slots": gold},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"trial_slots": len(manifest), "design_slots": len(design),
                      "prompt_sha256": [row["prompt_sha256"] for row in manifest]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
