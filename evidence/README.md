# 演示与验收媒体

时区：Asia/Shanghai（UTC+8）。

## 当前核心实录（v10 轻量兼容编码，2026-11-21）

- `core-evidence-60s.mp4`：由原 15 fps 成片缩小为 1280×720，H.264 Constrained Baseline Level 3.1，yuv420p 8 bit，15 fps，900 帧，无 B 帧，CABAC 关闭，refs=1，GOP=30，CRF 20，视频上限约 2 Mbps，faststart；音频为 AAC-LC、44.1 kHz 立体声（编码目标 128 kbps，ffprobe 实测约 103 kbps）。视频流时长 60.000 秒，容器时长 60.010 秒。6,954,031 字节，SHA-256 `3192f268b4a9daf937678d4bd8c154bb7b380e9723858023cbbcc099862eb3d6`。
- 此前入库的 1920×1080 High / Main 档成片（11,550,287 字节，SHA-256 `e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e`）以及后来用于 PowerPoint 的 12.38 MB Main@L4.0 30 fps 编码，均不再作为当前旁置文件。字幕、海报与解说母带未改。
- `core-evidence-60s.srt`：与成片同步的中文字幕（哈希未变）。
- `poster.png`：同片海报（哈希未变）。
- `voice/NARRATION.md`：解说文稿。
- `EDIT-MAP.md`：剪辑对照（素材来源、章节时间轴、样本补拍与后期处理）。技术剪辑信息写在这里，不叠在画面顶栏。
- `core-evidence-narration.mp3`：与成片同步的解说音轨副本；wav 母带已封装进 mp4，未再入库。
- `core-evidence-SHA256SUMS.txt`、`core-evidence-verify.json`：当前旁置文件的校验清单与探测信息。

成片顶栏为普通标题，配中文解说和字幕。片中的 GPU / NPU 结果标为历史实验结果。内容覆盖入口与锁定配置、真实样本与字段隔离、CPU 现场 BM25 压缩与预算、对已保存回答的现场评分，以及历史 CUDA / NPU 表。这不是把全部实验再跑一遍，也没有新的 GPU / NPU 或 Long 推理。真人讲述计时与成员本人确认仍缺。

当前 `docs/presentation/final/slides.pptx`（v10）真正内嵌同一轻量 MP4（ZIP 部件名为 `ppt/media/media1.mp4`，字节与本目录文件相同）。进入第 9 页后自动播放，不依赖旁置文件。画面说明已改为「进入本页自动播放」。`slides.pdf` 是按 v10 画面新导出的静态海报，不能用来放视频。

ffmpeg 与 GStreamer 对轻量 MP4 的完整解码已通过。2026-11-21（Asia/Shanghai）在 LibreOffice 25.2.3.2 上，对哈希为 `b2bb8abaa8fd8ea8e6d981a81b1def2d4dc4a67d0ff2d404a893636c1196182f` 的同一 PPTX：全屏从第 8 页进入第 9 页后无需点击；目视约 65 秒，25 秒与 55 秒检查点画面有变化，未见明显卡住或崩溃；约 65 秒时视频区域发黑，结束帧不能确认。返回第 8 页再进入第 9 页会重新自动开始，约 10 秒后画面继续推进。辅助截图在 `v10-gui/`。这只是 LibreOffice 视觉观察，不是 Microsoft PowerPoint 实测，也未听验声音；不能声称已解决 Windows 卡死/崩溃，也不能声称逐帧连续播放或结束帧已确认。

可再次运行的终端演示入口在 `scripts/core-demo/`。

## 同日较早的 50 秒离线测试实录（历史材料）

- `local-offline-evidence.mp4`：50.000 秒，1920×1200，H.264，1,915,107 字节，SHA-256 `663ac1b50c588424dd401698dc046de9813986b39779d7edc662906941648b33`。
- `local-offline-evidence-result.webp`：实录结果截图（与运行目录原件同哈希）。
- `local-offline-evidence-result.png`：同截图的无损转存，不是另一次运行。

这是 2026-11-21 对本已推 `main` `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4` 的离线验收演示（约 7 秒脚本 + 屏幕停留，成片 50 秒）。不是重新做模型推理。现已不再作为提交演示视频。
