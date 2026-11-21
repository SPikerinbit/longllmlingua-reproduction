"""The recommended branches must describe the canonical stage-two acceptance file.

The compatibility branch stage_3 may still contain the older 394/400 copy.
This test does not rewrite that history. It fails when current docs say the
recommended branch still uses the old copy.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RUN = "outputs/stage2/a1bd26fe3d82dea3f65d"
HISTORICAL_RUN = "outputs/stage2/875ddf42e70e37db8455"


def test_acceptance_file_matches_verification_when_canonical():
    acceptance = json.loads((ROOT / "reports/smoke-stage2-acceptance.json").read_text())
    verification = json.loads((ROOT / "reports/stage2-smoke/verification.json").read_text())
    if acceptance["budget_satisfied"] != 396:
        return
    assert acceptance["accepted_run"] == CANONICAL_RUN
    assert acceptance["slots"] == 400
    assert acceptance["accepted_run"].endswith("/" + verification["run_id"])
    assert verification["budget_satisfied"] == 396
    assert verification["rows"] == 400
    assert len(verification["budget_misses"]) == 4


def test_current_docs_do_not_assign_the_old_copy_to_the_recommended_branch():
    acceptance = json.loads((ROOT / "reports/smoke-stage2-acceptance.json").read_text())
    if acceptance["budget_satisfied"] != 396:
        return
    evidence = (ROOT / "docs/presentation/02-score-evidence.md").read_text()
    report = (ROOT / "docs/presentation/report-draft.md").read_text()
    assert "stage3-main-comparison` 继承的是 `stage_3` 这份" not in evidence
    assert CANONICAL_RUN in evidence
    assert "只有兼容分支 `stage_3`" in evidence
    assert HISTORICAL_RUN in evidence
    assert CANONICAL_RUN in report
    assert "只有兼容分支 `stage_3`" in report
    task = ROOT / "docs/presentation/members/member3/task.md"
    if task.exists():
        text = task.read_text()
        assert "本分支继承了 `stage_3`" not in text
        assert CANONICAL_RUN in text
        assert "只有兼容分支 `stage_3`" in text
        assert HISTORICAL_RUN in text
