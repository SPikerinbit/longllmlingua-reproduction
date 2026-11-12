"""Synthetic offline validation only; fixtures are not experiment results."""
from copy import deepcopy

import pytest

from scripts.stage4_recovery_analysis import analyze, paired_bootstrap


@pytest.fixture
def source():
    meta = {"split": "smoke", "question_ids": ["q1", "q2"], "config": {
        "positions": [1, 5, 10, 15, 20], "methods": {"longllmlingua_2x": {
            "recovery": True, "ratio": 2, "reorder_context": "original"}}}}
    rows = [{"question_id": qid, "position": position, "method": "longllmlingua_2x",
             "slot_id": f"{qid}:{position}:longllmlingua_2x", "status": "success",
             "recovery_enabled": True, "answers": ["Paris"],
             "answer_before_recovery": "Wrong\nParis", "answer_after_recovery": "PARIS!"}
            for qid in meta["question_ids"] for position in meta["config"]["positions"]]
    return meta, rows


def test_upstream_first_line_rescore_and_recovery_direction(source):
    meta, rows = source
    # Stored scores must not override scoring from actual answers.
    rows[0]["score_before_recovery"] = 1
    report = analyze(meta, rows, ["q1", "q2"])
    assert report["complete"]
    assert report["full_em"] == 1 and report["no_recovery_em"] == 0
    assert report["removing_recovery_minus_full"]["delta"] == -1
    assert report["removing_recovery_minus_full"]["ci95"] == [-1, -1]
    assert len(report["stored_score_mismatches"]) == 1
    assert report["recovery_helped_slots"] == 10
    assert report["new_api_requests"] == report["new_compression_calls"] == 0


def test_missing_position_excludes_whole_question_from_paired_statistics(source):
    meta, rows = source
    report = analyze(meta, rows[:-1], ["q1", "q2"])
    assert not report["complete"]
    assert report["success_slots"] == 9
    assert report["paired_question_denominator"] == 1
    assert report["paired_slot_denominator"] == 5
    assert report["paired_question_coverage"] == .5
    assert report["excluded_questions"] == ["q2"]
    assert all(p["denominator"] == 1 for p in report["positions"])


def test_latest_failed_record_is_not_counted_as_success(source):
    meta, rows = source
    failure = dict(rows[-1], status="failed", error="interrupted")
    report = analyze(meta, rows + [failure], ["q1", "q2"])
    assert report["success_slots"] == 9
    assert report["failed_or_skipped_slots"] == 1
    assert report["superseded_records"] == 1
    assert report["missing_slots"] == []


@pytest.mark.parametrize("mutation", ["unexpected", "slot", "gold", "answer", "recovery"])
def test_rejects_inconsistent_or_lightweight_source(source, mutation):
    meta, rows = deepcopy(source)
    if mutation == "unexpected":
        rows[0]["question_id"] = "unknown"
    elif mutation == "slot":
        rows[0]["slot_id"] = "other-slot"
    elif mutation == "gold":
        rows[1]["answers"] = ["Berlin"]
    elif mutation == "answer":
        rows[0].pop("answer_before_recovery")
    else:
        rows[0]["recovery_enabled"] = False
    with pytest.raises(ValueError):
        analyze(meta, rows, ["q1", "q2"])


def test_cluster_bootstrap_uses_questions_and_is_reproducible():
    report = paired_bootstrap([1, -1])
    assert report == paired_bootstrap([1, -1])
    assert report["question_denominator"] == 2
    assert report["repetitions"] == 2000 and report["seed"] == 42
    assert report["ci95"] == [-1, 1]
    assert paired_bootstrap([]) is None


def test_no_complete_questions_reports_no_estimate(source):
    meta, rows = source
    report = analyze(meta, [rows[0]], ["q1", "q2"])
    assert report["paired_question_denominator"] == 0
    assert report["full_em"] is None
    assert report["removing_recovery_minus_full"] is None
