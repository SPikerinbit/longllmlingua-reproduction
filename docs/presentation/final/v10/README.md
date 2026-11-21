# G14 v10 lite — preserved tested bytes

Prepared 2026-11-21 23:43:59 Asia/Shanghai (UTC+8).

## Files ready for publish worker
- `slides.pptx`: 9 slides; 7,687,902 bytes; exact copy of the concurrently GUI-tested candidate, not resaved/repacked/cleaned/repaired.
- PPTX SHA-256: `b2bb8abaa8fd8ea8e6d981a81b1def2d4dc4a67d0ff2d404a893636c1196182f`.
- `slides.pdf`: NEW 9-page static poster export, 973,217 bytes. Includes corrected P9 caption. It contains no embedded video, file attachment, URL/file-link action, JavaScript or PDF media artifact found by recorded checks.
- `contact.jpg`: fresh whole-deck static contact sheet from that export, not playback evidence.
- `SOURCES.md`, `QA.md`, `evidence/`: provenance and read-only checks.
- `SHA256SUMS.txt`, `FILE-LIST.txt`: integrity manifest.

## Exact change scope vs v9
79 ZIP parts: only `ppt/media/media1.mp4` and `ppt/slides/slide9.xml` changed; the other 77 parts are byte-identical. P9 XML is exactly the old XML with only “点击右上内嵌视频播放” replaced by “进入本页自动播放”. All timing, relationships, layouts, geometry, PNG chart/poster and P1–8 are unchanged. Static PDF came from an isolated poster-only derivative, never the media-bearing final PPTX, and does not reuse v9 PDF.

## Playback status — do not overclaim
New-media GUI test is concurrent/pending at this finish handoff. No actual Microsoft PowerPoint is installed on the box. Audible narration has not been heard/verified. Do not claim PowerPoint/Windows freeze resolution or universal compatibility. See QA.md; old-media GUI success is not current-media evidence.

No git/release/main/published-package overwrite or upload was performed. All original/work files are preserved. This is not a full course-project completion claim; pre-existing evidence/team/machine metadata gaps remain.
