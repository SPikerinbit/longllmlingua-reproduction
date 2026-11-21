#!/usr/bin/env python3
"""Score cursor_dialogue replies after the sessions have finished.

There is no result file yet. This script exits with an error if the reply
file is missing. It never invents an answer. Official score is first-line
best_subspan_em, computed only here, not inside the answering session.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reproduction.evaluation import score


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replies", type=Path, required=True)
    parser.add_argument("--gold", type=Path,
                        default=ROOT / "reports/cursor_dialogue/trial/gold/labels.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not args.replies.is_file():
        print(f"No cursor_dialogue replies at {args.replies}. Nothing was scored.", file=sys.stderr)
        return 2
    gold = {row["slot_id"]: row for row in json.loads(args.gold.read_text(encoding="utf-8"))["slots"]}
    scored = []
    for line in args.replies.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        reply = json.loads(line)
        label = gold[reply["slot_id"]]
        answer = reply.get("answer")
        scored.append({
            "slot_id": reply["slot_id"],
            "status": reply.get("status", "unknown"),
            "model": reply.get("model", "unknown"),
            "session_id": reply.get("session_id", "unknown"),
            "tools_used": reply.get("tools_used", "unknown"),
            "elapsed_seconds": reply.get("elapsed_seconds"),
            "official_score": None if answer is None else score(answer, label["answers"]),
        })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({
        "experiment": "cursor_dialogue",
        "comparable_to_deepseek": False,
        "slots": scored,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"scored {len(scored)} replies into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
