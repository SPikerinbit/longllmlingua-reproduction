# 本机离线验收实录

时区：Asia/Shanghai（UTC+8）。

- `local-offline-evidence.mp4`：50.000 秒，1920×1200，H.264，1,915,107 字节，sha256 `663ac1b50c588424dd401698dc046de9813986b39779d7edc662906941648b33`。
- `local-offline-evidence-result.webp`：实录结果截图（与运行目录原件同哈希）。
- `local-offline-evidence-result.png`：同截图的无损转存，供幻灯片内嵌预览，不是另一次运行。

这是 2026-11-21 对本已推 `main` `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4` 的离线验收演示（约 7 秒脚本 + 屏幕停留，成片 50 秒）。videoReview 核验为连续运行、定向测试通过、全套进度至 100%、脚本退出码 0、未见密钥。不是重新做模型推理，也不等于真人讲述计时或成员本人确认。

仓库入口与课程包根目录的 `slides.pptx` 都使用相对路径 `evidence/local-offline-evidence.mp4`。请从该目录或 PPTX 打开视频。导出的 `slides.pdf` 里若出现 `file:///workspace/...` 绝对路径，在其他机器上不可移植，不要指望 PDF 一键播放；请直接打开本目录中的 mp4。
