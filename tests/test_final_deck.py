"""Current deck and formal report stay byte-identifiable."""

import hashlib
import re
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PPTX_SHA = "28d542c996917dde26cffea912a2b2d9bd9af4175a4580b4175766317267957e"
PDF_SHA = "bf86724c9843b7d744ecb364f5b0da318514e10bd8fe8ddaffd1fcac9f265d74"
REPORT_PDF_SHA = "c22fdba0788021c922433eec6bdad154f52e564c7ee0dabd0a2d2fd36bde4c3e"
VIDEO_SHA = "e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e"
POSTER_SHA = "f0dcb9d32a98ee4822c44712450664f993b59d8a1553ddea65b8f5c86447b5a8"
EMBEDDED_MP4_PART = "ppt/media/core-evidence-60s.mp4"
EMBEDDED_POSTER_PART = "ppt/media/core-evidence-poster.png"


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
    assert hashlib.sha256(report.read_bytes()).hexdigest() == REPORT_PDF_SHA
    info = (ROOT / "docs/presentation/report/pdfinfo.txt").read_text()
    assert "Pages:           11" in info


def test_pptx_embeds_unique_core_video_without_external_media():
    deck = ROOT / "docs/presentation/final/slides.pptx"
    evidence = ROOT / "evidence/core-evidence-60s.mp4"
    assert hashlib.sha256(evidence.read_bytes()).hexdigest() == VIDEO_SHA
    with ZipFile(deck) as archive:
        names = archive.namelist()
        mp4_parts = [name for name in names if name.lower().endswith(".mp4")]
        assert mp4_parts == [EMBEDDED_MP4_PART]
        embedded = archive.read(EMBEDDED_MP4_PART)
        assert hashlib.sha256(embedded).hexdigest() == VIDEO_SHA
        assert hashlib.sha256(archive.read(EMBEDDED_POSTER_PART)).hexdigest() == POSTER_SHA
        xml_parts = [name for name in names if name.endswith(".xml") or name.endswith(".rels")]
        video_targets = []
        for name in xml_parts:
            data = archive.read(name)
            assert b"file:///workspace" not in data
            for rel in re.finditer(rb"<Relationship\b[^>]*>", data):
                tag = rel.group(0)
                if b'TargetMode="External"' in tag and (
                    b"/video" in tag or b"/media" in tag or b".mp4" in tag
                ):
                    raise AssertionError(f"external media relationship in {name}: {tag!r}")
                if b"/relationships/video" in tag or b"/relationships/media" in tag:
                    assert b'TargetMode="External"' not in tag
                    match = re.search(rb'Target="([^"]+)"', tag)
                    assert match is not None
                    video_targets.append(match.group(1).decode("utf-8"))
        assert video_targets, "expected internal video or media relationships"
        # Targets are written as ../media/core-evidence-60s.mp4 from slide rels.
        assert all(target.endswith("media/core-evidence-60s.mp4") for target in video_targets)
        assert len(set(video_targets)) == 1


def test_slides_pdf_is_static_and_has_no_workspace_video_links():
    data = (ROOT / "docs/presentation/final/slides.pdf").read_bytes()
    assert hashlib.sha256(data).hexdigest() == PDF_SHA
    assert b"file:///workspace" not in data
    assert b"file://" not in data
    assert b"/Movie" not in data
    assert b"/RichMedia" not in data
    assert b".mp4" not in data
