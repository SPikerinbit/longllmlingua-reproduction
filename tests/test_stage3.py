"""Offline tests for the stage-three orchestration, coverage and statistics.

These tests never load the compressor, never call the API and never need the
tokenizer: they exercise the pure record/aggregation paths and the config contract.

Scratch directories live under ``tests/.scratch`` instead of ``tempfile`` because
the Windows sandbox used for development denies writes inside freshly created
``mkdtemp`` directories; a normal repository directory behaves the same on Linux.
"""

from __future__ import annotations

import json
import unittest
import uuid
from pathlib import Path

from reproduction import stage3

SCRATCH = Path(__file__).resolve().parent / ".scratch"


def scratch():
    path = SCRATCH / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def record(question_id, position, method, score, status="success", ratio=2.0):
    return {
        "slot_id": f"{question_id}:{position}:{method}",
        "question_id": question_id,
        "position": position,
        "method": method,
        "status": status,
        "score": score,
        "actual_ratio": ratio,
        "budget_satisfied": True,
        "prompt_tokens": 100,
        "origin_prompt_tokens": 200,
        "usage": {"prompt_tokens": 110, "completion_tokens": 5},
        "cache_hit": False,
        "error": None if status == "success" else "boom",
    }


def meta(question_ids=("q1", "q2"), positions=(1, 5)):
    return {
        "run_id": "test",
        "split": "pilot",
        "question_ids": list(question_ids),
        "config": {
            "split": "pilot",
            "positions": list(positions),
            "methods": {
                "original": {"kind": "original", "ratio": 1.0},
                "bm25_2x": {"kind": "bm25", "ratio": 2.0},
            },
            "baseline": "original",
            "statistics": {"bootstrap_samples": 200, "seed": 42, "confidence": 0.95},
        },
    }


def all_records(question_ids=("q1", "q2"), positions=(1, 5)):
    rows = {}
    for qid in question_ids:
        for position in positions:
            rows[f"{qid}:{position}:original"] = record(qid, position, "original", 1.0, ratio=1.0)
            rows[f"{qid}:{position}:bm25_2x"] = record(qid, position, "bm25_2x", 0.5)
    return rows


class ConfigTests(unittest.TestCase):
    def test_rejects_stage_two(self):
        config = json.loads((stage3.common.ROOT / "configs/stage3.json").read_text(encoding="utf-8"))
        config["stage"] = 2
        path = scratch() / "stage3.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaises(ValueError):
            stage3.load_stage3_config(path)

    def test_ratio_must_exceed_one(self):
        config = {"methods": {"bm25_2x": {"kind": "bm25", "ratio": 1.0}}}
        with self.assertRaises(ValueError):
            stage3.method_spec(config, "bm25_2x")

    def test_original_ratio_is_one(self):
        config = {"methods": {"original": {"kind": "original"}}}
        self.assertEqual(stage3.method_spec(config, "original")["ratio"], 1.0)

    def test_expected_slots(self):
        ids = stage3.expected_slot_ids(meta())
        self.assertEqual(len(ids), 2 * 2 * 2)
        self.assertIn("q1:1:original", ids)

    def test_shipped_config_is_valid(self):
        config = stage3.load_stage3_config()
        self.assertEqual(config["split"], "main")
        self.assertEqual(len(config["positions"]), 5)
        self.assertEqual(config["baseline"], "original")


class SummarizeTests(unittest.TestCase):
    def test_complete_matrix(self):
        report = stage3.summarize_records(meta(), all_records())
        self.assertTrue(report["complete"])
        original = next(row for row in report["methods"] if row["method"] == "original")
        self.assertAlmostEqual(original["mean_em"], 1.0)
        bm25 = next(row for row in report["methods"] if row["method"] == "bm25_2x")
        self.assertAlmostEqual(bm25["mean_em"], 0.5)
        self.assertEqual(len(report["groups"]), 2 * 2)

    def test_missing_cell_breaks_complete(self):
        rows = all_records()
        del rows["q2:5:bm25_2x"]
        report = stage3.summarize_records(meta(), rows)
        self.assertFalse(report["complete"])
        cell = next(group for group in report["groups"]
                    if group["method"] == "bm25_2x" and group["position"] == 5)
        self.assertEqual(cell["missing"], 1)
        self.assertEqual(cell["success"], 1)

    def test_failed_row_is_counted_as_failed(self):
        rows = all_records()
        rows["q1:1:bm25_2x"] = record("q1", 1, "bm25_2x", None, status="failed")
        report = stage3.summarize_records(meta(), rows)
        cell = next(group for group in report["groups"]
                    if group["method"] == "bm25_2x" and group["position"] == 1)
        self.assertEqual(cell["failed"], 1)
        self.assertEqual(cell["success"], 1)


class CoverageTests(unittest.TestCase):
    def test_missing_and_failed(self):
        rows = all_records()
        del rows["q1:5:original"]
        rows["q2:1:bm25_2x"] = record("q2", 1, "bm25_2x", None, status="failed")
        coverage = stage3.coverage_from_records(meta(), rows)
        self.assertEqual(coverage["expected_slots"], 8)
        self.assertEqual(coverage["missing"], 1)
        self.assertEqual(coverage["failed"], 1)
        self.assertIn("q1:5:original", coverage["missing_slot_ids"])

    def test_latest_record_wins(self):
        path = scratch() / "results.jsonl"
        rows = [
            {"slot_id": "q1:1:original", "question_id": "q1", "position": 1,
             "method": "original", "status": "failed", "score": 0.0},
            {"slot_id": "q1:1:original", "question_id": "q1", "position": 1,
             "method": "original", "status": "success", "score": 1.0},
        ]
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
        records = stage3.load_records(path)
        self.assertEqual(records["q1:1:original"]["status"], "success")
        self.assertEqual(records["q1:1:original"]["score"], 1.0)


class StatisticsTests(unittest.TestCase):
    def test_bootstrap_constant_difference(self):
        result = stage3.paired_bootstrap([0.1] * 20, samples=200, seed=42)
        self.assertEqual(result["n"], 20)
        self.assertAlmostEqual(result["mean"], 0.1)
        self.assertAlmostEqual(result["ci_low"], 0.1)
        self.assertAlmostEqual(result["ci_high"], 0.1)

    def test_paired_comparison_uses_common_questions(self):
        rows = all_records()
        # q2 bm25 has a missing position, so it must be dropped from the pairing.
        del rows["q2:5:bm25_2x"]
        comparisons = stage3.paired_comparisons(meta(), rows)
        bm25 = next(row for row in comparisons if row["method"] == "bm25_2x")
        self.assertEqual(bm25["n_questions"], 1)
        self.assertAlmostEqual(bm25["mean"], -0.5)

    def test_empty_comparison(self):
        comparisons = stage3.paired_comparisons(meta(), {})
        bm25 = next(row for row in comparisons if row["method"] == "bm25_2x")
        self.assertEqual(bm25["n_questions"], 0)
        self.assertIsNone(bm25["mean"])


class RunDirTests(unittest.TestCase):
    def test_summarize_writes_files(self):
        run_dir = scratch()
        (run_dir / "run.json").write_text(json.dumps(meta()), encoding="utf-8")
        rows = list(all_records().values())
        (run_dir / "results.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
        report = stage3.summarize(run_dir)
        self.assertTrue(report["complete"])
        self.assertTrue((run_dir / "summary.json").exists())
        self.assertTrue((run_dir / "summary.md").exists())
        self.assertTrue((run_dir / "coverage.json").exists())
        coverage = json.loads((run_dir / "coverage.json").read_text(encoding="utf-8"))
        self.assertEqual(coverage["missing"], 0)


if __name__ == "__main__":
    unittest.main()
