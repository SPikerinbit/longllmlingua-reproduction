# QA — edit / finish / PowerPoint target

Recorded 2026-11-21 23:43:59 Asia/Shanghai (UTC+8).

## Verified independently in this finish
- Input candidate SHA-256 and size match the exact supplied identity. Final `slides.pptx` is byte-identical. Candidate remains unmodified; no final clean/pack/repair/save (preserving the 79-part byte contract overrides routine repacking).
- Independent ZIP comparison to start.pptx: exactly 2 changed parts and 77 byte-identical parts, with no added/removed parts. P9 caption-only literal substitution assertion passes; timing and relationships unchanged.
- Embedded MP4 hash equals supplied source: `3192f268b4a9daf937678d4bd8c154bb7b380e9723858023cbbcc099862eb3d6`.
- Read-only office schema check: OK, 72 XML parts schema-checked, 1 without a schema. check-overlap: no findings. Fonts: Noto Sans CJK SC, Inconsolata, Noto Sans Mono installed; no visible-text-changing missing faces.
- New isolated poster-only copy: removed video/audio/media metadata, media actions/timing, hyperlinks/external relationships and MP4; retained current caption and static chart/poster. Only that derivative was packed/rendered.
- Fresh PDF: 9 pages; no embedded files; no URL results; JavaScript no. Raw PDF plus 154 zlib-decoded streams scanned for RichMedia, EmbeddedFile, Filespec, JavaScript, Launch, Movie, Sound, Rendition, MediaClip, Screen, FileAttachment, URI and GoToR: none found. Current caption confirmed using pdftotext. See evidence/static-pdf-audit.json.
- Own visual review: opened fresh contact then all 9 full-page images. No newly introduced clipping, overlap, contrast issue or template residue found. P9 current caption is readable; chart and poster retained. No must-fix found requiring mutation of concurrently tested bytes.

## Media evidence inherited from current build, not repeated GUI tests
ffprobe/header/decode evidence copied into evidence/: H.264 Constrained Baseline L3.1, 1280×720, yuv420p, 15 fps, 900 frames, B0/CABAC0/refs1; AAC-LC 44.1 kHz stereo; faststart; video 60.000 s, audio/container 60.010 s. Full source/extracted decode passed upstream. Existing 60000 ms autoplay timing retained; not extended for 10 ms tail. Smaller decode burden is not a compatibility guarantee.

## Defects/limits left
| Slide | Status | Detail |
|---|---|---|
| 1–9 | left, intentional preservation | Existing fine print, chart labels, source footnotes and screenshot/code detail remain small. Not guaranteed room-readable. No redesign authorized. |
| 9 | fixed in build, verified | Click-caption mismatch corrected to entry-autoplay caption. No further slide mutation in finish. |
| 8→9 / 9 | pending external GUI worker | Current exact-byte autoplay/full 60 s/re-entry/Shift+F5/pause-resume test not reported to this finish. No GUI pass claimed. |
| 9 | left | Audio hearing unverified; codec/decode success is not an audible narration test. |
| 8→9 / 9 | left | Actual Windows/Microsoft PowerPoint unavailable on box. No universal compatibility, hang/crash-resolution or PowerPoint-success claim. |

## Target-machine acceptance before claiming playback success
Record system/app version and the final PPTX hash. In actual Microsoft PowerPoint enter full-screen P8→P9 without clicking video; verify immediate playback, complete ~60 s picture and audible Chinese narration. Repeat 8↔9 at least 3 times; check exit/re-entry, Shift+F5, pause/resume, no hang/crash. Preserve exact file and logs if any failure. Do not replace this test with static images or old-media GUI records.

## Existing broader gaps unchanged
P-number/four-member registration, first-person member confirmations/contributions and live timing; complete stage 2/3/4 per-item outputs/compression/QA caches/checksums; CUDA model; stage-4 CANN; controlled Cursor results remain outside this mechanical finish. No facts or evidence invented. No git/release/source-code change or published-package overwrite.
