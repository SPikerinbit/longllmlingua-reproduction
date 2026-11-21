"""Offline checks for the stage-one supplement. No API and no compressor."""

import json
from pathlib import Path

from reproduction.data import visible_sample
from reproduction.evaluation import score
from scripts.audit_stage1_offline import CASE_SLOTS, budget_violation

ROOT = Path(__file__).resolve().parents[1]


def test_visible_sample_drops_gold_and_answers():
    row = {"question": "q", "answers": ["secret"], "ctxs": [
        {"id": "1", "title": "t", "text": "body", "isgold": True, "hasanswer": True, "score": "9"}]}
    visible = visible_sample(row)
    assert set(visible) == {"question", "documents"}
    assert visible["documents"] == [{"id": "1", "title": "t", "text": "body"}]


def test_budget_rule_rejects_over_target():
    assert budget_violation({
        "method": "bm25_2x", "origin_tokens": 100, "compressed_tokens": 60,
        "target_tokens": 50, "actual_ratio": 100 / 60,
    }) == "compressed_tokens exceed target_tokens"


def test_committed_audit_matches_predictions_and_labels():
    audit = json.loads((ROOT / "reports/stage1-supplement/offline-audit.json").read_text())
    labels = {row["question_id"]: row["answers"]
              for row in json.loads((ROOT / "reports/stage1-supplement/smoke-labels.json").read_text())}
    predictions = [json.loads(line) for line in
                   (ROOT / "reports/stage1-acceptance/predictions.jsonl").read_text().splitlines() if line.strip()]
    assert audit["api_calls"] == 0
    assert audit["prediction_rows"] == 300
    assert audit["isolation"]["failures"] == []
    assert audit["budget"]["violations"] == []
    assert audit["budget"]["usage_prompt_equals_local_plus_4"] == 300
    assert audit["rescore"]["mismatches"] == []
    assert audit["rescore"]["official_mean_score"] == {
        "original": 0.92, "bm25_2x": 0.87, "bm25_4x": 0.64}
    assert len(audit["diagnostic_not_official_metric"]["first_line_zero_but_joined_text_one"]) == 2
    assert len(audit["diagnostic_not_official_metric"]["strong_denial_and_official_score_one"]) == 4
    mismatches = [
        row["slot_id"] for row in predictions
        if score(row["answer"], labels[row["question_id"]]) != row["score"]
    ]
    assert mismatches == []
    assert all(budget_violation(row) is None for row in predictions)


def test_thirteen_real_slots_are_listed():
    text = (ROOT / "reports/stage1-supplement/cases.md").read_text()
    assert text.count("\n## S1-") == 13
    for slot_id in CASE_SLOTS:
        assert slot_id in text
    assert "Cursor 对话" in text


def test_cursor_dialogue_has_inputs_but_no_replies():
    root = ROOT / "reports/cursor_dialogue"
    manifest = json.loads((root / "trial/manifest.json").read_text())
    assert manifest["contains_gold"] is False
    assert len(manifest["slots"]) == 3
    design = json.loads((root / "design-slots.json").read_text())
    assert design["slots"] == 300
    for row in manifest["slots"]:
        body = (root / row["prompt_file"]).read_bytes()
        import hashlib
        assert hashlib.sha256(body).hexdigest() == row["prompt_sha256"]
        assert b"\nanswers\n" not in body
    gold = json.loads((root / "trial/gold/labels.json").read_text())
    assert gold["do_not_send_to_answerer"] is True
    assert not (root / "trial/replies.jsonl").exists()
    assert not (root / "trial/scored.json").exists()
