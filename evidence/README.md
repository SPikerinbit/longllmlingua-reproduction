# 演示与验收媒体

时区：Asia/Shanghai（UTC+8）。

## 当前核心实录（2026-11-21）

- `core-evidence-60s.mp4`：60.000 秒，1920×1080，H.264 yuv420p、15 fps，AAC 音轨，11,550,287 字节，SHA-256 `e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e`。
- `core-evidence-60s.srt`：与成片同步的中文字幕。
- `poster.png`：同片海报。
- `voice/NARRATION.md`：解说文稿。
- `EDIT-MAP.md`：剪辑对照（素材来源、章节时间轴、样本补拍与后期处理）。技术剪辑信息写在这里，不叠在画面顶栏。
- `core-evidence-narration.mp3`：与成片同步的解说音轨副本；wav 母带已封装进 mp4，未再入库。
- `core-evidence-SHA256SUMS.txt`、`core-evidence-verify.json`：校验清单与探测信息。

成片顶栏为普通标题，配中文解说和字幕。片中的 GPU / NPU 结果标为历史实验结果。内容覆盖入口与锁定配置、真实样本与字段隔离、CPU 现场 BM25 压缩与预算、对已保存回答的现场评分，以及历史 CUDA / NPU 表。这不是把全部实验再跑一遍，也没有新的 GPU / NPU 或 Long 推理。真人讲述计时与成员本人确认仍缺。

当前 `docs/presentation/final/slides.pptx`（v7）已真正内嵌本片，放映时点击播放即可，不依赖本目录文件。旁置 `core-evidence-60s.mp4` 只为独立播放。`slides.pdf` 是静态 poster 版，不能用来放视频。同日较早的 50 秒片不再作为提交演示。

可再次运行的终端演示入口在 `scripts/core-demo/`。

## 同日较早的 50 秒离线测试实录（历史材料）

- `local-offline-evidence.mp4`：50.000 秒，1920×1200，H.264，1,915,107 字节，SHA-256 `663ac1b50c588424dd401698dc046de9813986b39779d7edc662906941648b33`。
- `local-offline-evidence-result.webp`：实录结果截图（与运行目录原件同哈希）。
- `local-offline-evidence-result.png`：同截图的无损转存，不是另一次运行。

这是 2026-11-21 对本已推 `main` `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4` 的离线验收演示（约 7 秒脚本 + 屏幕停留，成片 50 秒）。不是重新做模型推理。现已不再作为提交演示视频。
