import json
from pathlib import Path
from scripts.analyze_stage4 import build

ROOT = Path(__file__).resolve().parents[1]


def test_rebuild_uses_the_complete_final_session(tmp_path):
    build(ROOT / "reports/stage4-ablation-efficiency/inputs", tmp_path)
    coverage = json.loads((tmp_path / "coverage.json").read_text())
    assert coverage["ablation"]["success"] == 3500
    assert coverage["efficiency"]["success"] == 1200
    assert coverage["efficiency"]["failed"] == 0
    assert coverage["efficiency"]["missing"] == 0
    assert coverage["overall_planned_efficiency_complete"] is True
    efficiency = json.loads((tmp_path / "efficiency.json").read_text())
    assert efficiency["n_per_method"] == 99
    assert "20" in efficiency["positions"]


def test_final_measurement_does_not_expand_or_change_methods():
    old = json.loads((ROOT / "configs/cloud/efficiency.json").read_text())
    new = json.loads((ROOT / "configs/cloud/efficiency-final.json").read_text())
    for key in ("methods", "compressor", "split", "positions", "tokenizer", "upstream"):
        assert new[key] == old[key]
    assert new["split"] == "smoke"
    assert len(new["methods"]) * len(new["positions"]) * 20 == 1200
    assert new["benchmark_no_cache"] and new["max_requests_per_run"] == 1500
