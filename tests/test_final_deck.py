"""The current deck is present, and the known missing config stays missing."""

import re
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def test_final_deck_has_nine_slides_and_is_not_the_old_template():
    deck = ROOT / "docs/presentation/final/slides.pptx"
    template = ROOT / "docs/presentation/slides/G14-LongLLMLingua-template.pptx"
    assert deck.is_file() and (ROOT / "docs/presentation/final/slides.pdf").is_file()
    assert deck.read_bytes() != template.read_bytes()
    with ZipFile(deck) as archive:
        slides = [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
    assert len(slides) == 9


def test_pilot_run_config_named_on_the_evidence_slide_is_not_in_the_repo():
    assert not (ROOT / "configs/stage3-pilot-as-run.json").exists()
    text = (ROOT / "docs/presentation/01-number-registry.md").read_text()
    assert "configs/stage3-pilot-as-run.json" in text
    order = (ROOT / "docs/presentation/04-speaker-map.md").read_text()
    assert "1、2、3、4、5、8、6、9、7" in order
