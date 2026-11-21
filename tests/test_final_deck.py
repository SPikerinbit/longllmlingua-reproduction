"""Current deck and formal report stay byte-identifiable."""

import hashlib
import re
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PPTX_SHA = "bbaf7e1fe3603b8cb74ec09b96ac6a32772918ac10c338651a2e2de1d38c4bf5"
PDF_SHA = "3c72d76f506ffcc3fca13bca08db95371079032de5e6e901a79036172b65ddfe"


def test_final_deck_has_nine_slides_and_is_not_the_old_template():
    deck = ROOT / "docs/presentation/final/slides.pptx"
    slides_pdf = ROOT / "docs/presentation/final/slides.pdf"
    template = ROOT / "docs/presentation/slides/G14-LongLLMLingua-template.pptx"
    assert hashlib.sha256(deck.read_bytes()).hexdigest() == PPTX_SHA
    assert hashlib.sha256(slides_pdf.read_bytes()).hexdigest() == PDF_SHA
    assert deck.read_bytes() != template.read_bytes()
    with ZipFile(deck) as archive:
        slides = [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
        blob = b"\n".join(archive.read(name) for name in archive.namelist() if name.endswith(".xml"))
    assert len(slides) == 9
    assert b"python -m json.tool reports/stage3-main/run.json" in blob
    assert b"stage3-pilot-as-run" not in blob


def test_saved_pilot_snapshot_is_readable_and_split_is_pilot():
    assert not (ROOT / "configs/stage3-pilot-as-run.json").exists()
    text = (ROOT / "reports/stage3-main/run.json").read_text()
    assert '"split": "pilot"' in text
    order = (ROOT / "docs/presentation/04-speaker-map.md").read_text()
    assert "1、2、3、4、5、8、6、9、7" in order


def test_formal_report_is_present_with_eleven_pages():
    report = ROOT / "docs/presentation/report/report.pdf"
    assert report.is_file()
    assert (ROOT / "docs/presentation/report/report.docx").is_file()
    assert (ROOT / "docs/presentation/report/report.md").is_file()
    assert (ROOT / "docs/presentation/report/SOURCES.md").is_file()
    info = (ROOT / "docs/presentation/report/pdfinfo.txt").read_text()
    assert "Pages:           11" in info
