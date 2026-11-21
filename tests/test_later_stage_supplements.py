"""Consistency checks for committed later-stage records. No weights and no API."""

from scripts.audit_stage2_offline import audit as audit_stage2
from scripts.audit_stage3_offline import audit as audit_stage3
from scripts.audit_stage4_offline import audit as audit_stage4


def test_stage2_records_agree():
    report = audit_stage2()
    assert report["problems"] == []
    assert report["rows"] == 400
    assert report["budget_satisfied"] + len(report["budget_misses"]) == 400
    assert report["api_calls"] == 0 and report["compression_rerun"] is False


def test_stage3_records_agree():
    report = audit_stage3()
    assert report["problems"] == []
    assert report["questions"] == 100
    assert report["slots"] == 3500
    assert report["api_calls"] == 0


def test_stage4_records_agree():
    report = audit_stage4()
    assert report["problems"] == []
    assert report["ablation_slots"] == 3500
    assert report["efficiency_slots"] == 1200
    assert report["recovery_regressions"] == 3
    assert report["compression_rerun"] is False
