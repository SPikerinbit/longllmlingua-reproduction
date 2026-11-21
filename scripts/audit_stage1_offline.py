#!/usr/bin/env python3
"""Offline audit of the existing stage-one DeepSeek predictions.

This script does not call a model or an API. It checks the committed
predictions against the pinned public NQ files and the upstream scorer.
Diagnostic counts are not a replacement for best_subspan_em.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import platform
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reproduction.data import document_set, normalized, question_id, visible_sample
from reproduction.evaluation import score

POSITIONS = (1, 5, 10, 15, 20)
METHODS = ("original", "bm25_2x", "bm25_4x")
RATIO = {"original": 1, "bm25_2x": 2, "bm25_4x": 4}
STRONG_DENIAL = re.compile(
    r"(cannot definitively|is not explicitly stated|none of the documents contain|"
    r"do not contain the answer|do not provide an answer|no information about)",
    re.I,
)
CASE_SLOTS = (
    "ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:1:original",
    "ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:1:bm25_2x",
    "ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:1:bm25_4x",
    "0b6dde118f5c85bc3f4d120a9bd287bf2fbdda405bda05bf3d8587c10efc9be7:1:original",
    "0b6dde118f5c85bc3f4d120a9bd287bf2fbdda405bda05bf3d8587c10efc9be7:1:bm25_2x",
    "0b6dde118f5c85bc3f4d120a9bd287bf2fbdda405bda05bf3d8587c10efc9be7:1:bm25_4x",
    "64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:10:original",
    "64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:10:bm25_2x",
    "64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:10:bm25_4x",
    "64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:5:original",
    "64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:20:original",
    "eea8ae864c0ece22a4ce2d354c1df5d58e295152b12ccfb69ced409696fd971d:1:original",
    "eea8ae864c0ece22a4ce2d354c1df5d58e295152b12ccfb69ced409696fd971d:1:bm25_4x",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_position_file(path: Path) -> dict[str, dict]:
    rows = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            qid = question_id(item)
            if qid in rows:
                raise ValueError(f"duplicate question id in {path.name}")
            rows[qid] = item
    return rows


def budget_violation(row: dict) -> str | None:
    ratio = RATIO[row["method"]]
    if row["compressed_tokens"] > row["target_tokens"]:
        return "compressed_tokens exceed target_tokens"
    expected_target = row["origin_tokens"] // ratio
    if row["target_tokens"] != expected_target:
        return f"target_tokens {row['target_tokens']} != origin//ratio {expected_target}"
    if row["compressed_tokens"] <= 0:
        return "non-positive compressed_tokens"
    actual = row["origin_tokens"] / row["compressed_tokens"]
    if abs(row["actual_ratio"] - actual) > 1e-9:
        return "actual_ratio does not equal origin/compressed"
    if row["method"] == "original" and not (
        row["origin_tokens"] == row["compressed_tokens"] == row["target_tokens"]
    ):
        return "original prompt was altered"
    return None


def audit(predictions_path: Path, raw_dir: Path, resources_path: Path) -> dict:
    started = time.perf_counter()
    resources = json.loads(resources_path.read_text(encoding="utf-8"))
    smoke = json.loads((ROOT / "manifests/smoke.json").read_text(encoding="utf-8"))
    pilot = json.loads((ROOT / "manifests/pilot.json").read_text(encoding="utf-8"))
    main = json.loads((ROOT / "manifests/main.json").read_text(encoding="utf-8"))
    predictions = load_jsonl(predictions_path)
    file_records = []
    by_position = {}
    for position in POSITIONS:
        name = f"nq-open-20_total_documents_gold_at_{position - 1}.jsonl.gz"
        path = raw_dir / name
        meta = resources["files"][str(Path("data/raw") / name).replace("/", "\\")]
        digest = sha256_file(path)
        if digest != meta["sha256"] or path.stat().st_size != meta["bytes"]:
            raise ValueError(f"checksum mismatch for {name}")
        file_records.append({"name": name, "bytes": path.stat().st_size, "sha256": digest})
        by_position[position] = load_position_file(path)

    isolation_failures = []
    witnesses = []
    for qid in smoke["question_ids"]:
        docsets = []
        answer_sets = []
        golds = {}
        for position in POSITIONS:
            item = by_position[position][qid]
            gold = [index + 1 for index, doc in enumerate(item["ctxs"]) if doc.get("isgold")]
            golds[str(position)] = gold
            if gold != [position] or len(item["ctxs"]) != 20:
                isolation_failures.append({"question_id": qid, "position": position, "gold": gold})
            visible = visible_sample(item)
            if set(visible) != {"question", "documents"} or any(
                set(doc) != {"id", "title", "text"} for doc in visible["documents"]
            ):
                isolation_failures.append({"question_id": qid, "position": position, "error": "visible fields"})
            docsets.append(tuple(document_set(item)))
            answer_sets.append(tuple(sorted({normalized(answer) for answer in item["answers"]})))
        if len(set(docsets)) != 1 or len(set(answer_sets)) != 1:
            isolation_failures.append({"question_id": qid, "error": "cross-position mismatch"})
        witnesses.append({
            "question_id": qid,
            "document_set_sha256": docsets[0][0] and hashlib.sha256(
                "\n".join(docsets[0]).encode()
            ).hexdigest(),
            "gold": golds,
        })

    labels = {}
    for qid in smoke["question_ids"]:
        item = by_position[1][qid]
        labels[qid] = {"question": item["question"], "answers": list(item["answers"])}

    violations = []
    mismatches = []
    plus4 = 0
    hidden_by_newline = []
    denial_credit = []
    by_method = defaultdict(list)
    for row in predictions:
        problem = budget_violation(row)
        if problem:
            violations.append({"slot_id": row["slot_id"], "problem": problem})
        if row["usage"]["prompt_tokens"] == row["compressed_tokens"] + 4:
            plus4 += 1
        answers = labels[row["question_id"]]["answers"]
        official = score(row["answer"], answers)
        if official != row["score"]:
            mismatches.append({"slot_id": row["slot_id"], "stored": row["score"], "recomputed": official})
        full = score(row["answer"].replace("\n", " "), answers)
        if official == 0.0 and full == 1.0:
            hidden_by_newline.append(row["slot_id"])
        first = row["answer"].split("\n", 1)[0]
        if row["score"] == 1.0 and STRONG_DENIAL.search(first):
            denial_credit.append(row["slot_id"])
        by_method[row["method"]].append(row["score"])

    missing_slots = sorted(set(CASE_SLOTS) - {row["slot_id"] for row in predictions})
    if missing_slots:
        raise ValueError(f"case slots missing from predictions: {missing_slots}")
    elapsed = time.perf_counter() - started
    return {
        "kind": "stage1-offline-audit",
        "api_calls": 0,
        "elapsed_seconds": elapsed,
        "python": sys.version,
        "platform": platform.platform(),
        "predictions_sha256": sha256_file(predictions_path),
        "prediction_rows": len(predictions),
        "inputs": file_records,
        "manifests": {
            "smoke": len(smoke["question_ids"]),
            "pilot": len(pilot["question_ids"]),
            "main": len(main["question_ids"]),
            "smoke_prefix_of_pilot": smoke["question_ids"] == pilot["question_ids"][:20],
            "pilot_prefix_of_main": pilot["question_ids"] == main["question_ids"][:100],
            "seed": smoke["seed"],
            "population": smoke["population"],
            "source_commit": smoke["source_commit"],
        },
        "isolation": {
            "smoke_questions": len(smoke["question_ids"]),
            "population_per_position": {str(position): len(by_position[position]) for position in POSITIONS},
            "failures": isolation_failures,
        },
        "budget": {"violations": violations, "usage_prompt_equals_local_plus_4": plus4},
        "rescore": {
            "mismatches": mismatches,
            "official_mean_score": {method: sum(values) / len(values) for method, values in by_method.items()},
        },
        "diagnostic_not_official_metric": {
            "rule": "same best_subspan_em; full-text variant joins newlines with spaces before scoring",
            "strong_denial_regex": STRONG_DENIAL.pattern,
            "first_line_zero_but_joined_text_one": hidden_by_newline,
            "strong_denial_and_official_score_one": denial_credit,
        },
        "labels": [
            {"question_id": qid, "question": labels[qid]["question"], "answers": labels[qid]["answers"]}
            for qid in smoke["question_ids"]
        ],
        "witnesses": witnesses,
    }


def write_cases(report: dict, predictions_path: Path, destination: Path) -> None:
    labels = {row["question_id"]: row for row in report["labels"]}
    predictions = {row["slot_id"]: row for row in load_jsonl(predictions_path)}
    hidden = set(report["diagnostic_not_official_metric"]["first_line_zero_but_joined_text_one"])
    denial = set(report["diagnostic_not_official_metric"]["strong_denial_and_official_score_one"])
    lines = [
        "# 阶段一补充案例（既有 DeepSeek 预测）",
        "",
        "这些槽来自 `reports/stage1-acceptance/predictions.jsonl`，不是 Cursor 对话。",
        "官方分数仍是首行 `best_subspan_em`。诊断标记不替换该分数。",
        "这里不收录文档正文。",
        "",
    ]
    for index, slot_id in enumerate(CASE_SLOTS, start=1):
        row = predictions[slot_id]
        label = labels[row["question_id"]]
        flags = []
        if slot_id in hidden:
            flags.append("参考答案不在首行、拼成一行后才会被同一评分函数记为 1")
        if slot_id in denial:
            flags.append("首行有明确否认，但官方分数为 1")
        flag = "；".join(flags) if flags else "无诊断标记"
        lines.extend([
            f"## S1-{index:02d}",
            "",
            f"- slot_id：`{slot_id}`",
            f"- 问题：{label['question']}",
            f"- 参考答案：{'；'.join(label['answers'])}",
            f"- 方法 / 位置：{row['method']} / {row['position']}",
            f"- 官方 score：{row['score']}",
            f"- token：原始 {row['origin_tokens']}，压缩 {row['compressed_tokens']}，目标 {row['target_tokens']}，实测比 {row['actual_ratio']}",
            f"- API usage：输入 {row['usage']['prompt_tokens']}，输出 {row['usage']['completion_tokens']}；finish_reason={row['finish_reason']}",
            f"- 时间：{row['generation_created_at']}",
            f"- 诊断：{flag}",
            "",
            "首行：",
            "",
            "> " + row["answer"].split("\n", 1)[0],
            "",
        ])
    destination.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, default=ROOT / "reports/stage1-acceptance/predictions.jsonl")
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--resources", type=Path, default=ROOT / "manifests/resources.json")
    parser.add_argument("--out", type=Path, default=ROOT / "reports/stage1-supplement")
    args = parser.parse_args()
    report = audit(args.predictions, args.raw_dir, args.resources)
    args.out.mkdir(parents=True, exist_ok=True)
    labels = report.pop("labels")
    witnesses = report.pop("witnesses")
    (args.out / "offline-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.out / "smoke-labels.json").write_text(
        json.dumps(labels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.out / "isolation-witness.json").write_text(
        json.dumps(witnesses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_cases({**report, "labels": labels}, args.predictions, args.out / "cases.md")
    failures = (
        report["isolation"]["failures"]
        or report["budget"]["violations"]
        or report["rescore"]["mismatches"]
    )
    print(json.dumps({
        "elapsed_seconds": report["elapsed_seconds"],
        "rows": report["prediction_rows"],
        "isolation_failures": len(report["isolation"]["failures"]),
        "budget_violations": len(report["budget"]["violations"]),
        "rescore_mismatches": len(report["rescore"]["mismatches"]),
        "newline_boundary": len(report["diagnostic_not_official_metric"]["first_line_zero_but_joined_text_one"]),
        "denial_credit": len(report["diagnostic_not_official_metric"]["strong_denial_and_official_score_one"]),
        "means": report["rescore"]["official_mean_score"],
    }, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
