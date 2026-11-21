# v7 材料验收时间（不改写原 77 项记录）

时区：Asia/Shanghai（UTC+8）。

2026-11-21 21:55 之后，将已核验的 v7 演示稿与 60 秒核心实录、更新后的正式报告一并纳入仓库入口，并在本机再次跑完整测试与资源校验。这是材料整合与复查的时间记录，不是新的模型推理，也不改写下面这份原始离线全套测试：

- 原始 77 项记录时间仍是 2026-11-21 17:46:58–17:47:02（Asia/Shanghai）
- 提交 `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4`
- 环境 Python 3.13.5、`tokenizers==0.22.1`
- 完整 `python -m pytest` 收集 77、通过 77，退出码 0
- 原始产物仍是本目录 `pytest-full.stdout`、`junit-full.xml`、`timeline.txt` 等；`SHA256SUMS.txt` 仍只覆盖那些原始产物

新演示稿：`docs/presentation/final/slides.pptx` / `slides.pdf`（v7）。内嵌及旁置视频 SHA-256 `e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e`。Windows / PowerPoint 实播和音频听验仍未做。

## 本机复查（2026-11-21 22:00:16，Asia/Shanghai）

在纳入 v7 演示稿、正式报告和 60 秒核心实录之后，使用已有环境再次运行完整 `python -m pytest`：JUnit 记录 79 项、0 失败、0 错误、0 跳过，退出码 0。其中 2 项是本次新增的媒体钉扎（内嵌 MP4 唯一哈希、无外部媒体；PDF 无 `file:///workspace` 与活动视频动作），其余为原有检查。本次 JUnit 写在临时目录，没有改写本目录 `pytest-full.stdout` / `junit-full.xml`；那些原始 77 项文件的 SHA 仍与 `SHA256SUMS.txt` 一致。

仓库内 `reports/stage1-*`、`stage2-*`、`stage3-*`、`stage4-*` 以及 `configs/`、`manifests/` 的实验表与配置在本轮工作区中无改动。对当前工作树文本文件的凭证扫描未发现密钥或私钥。从 `slides.pptx` 抽出的 MP4 哈希与源一致，ffmpeg 完整解码退出码 0。Windows / PowerPoint 实播和音频听验仍未做。
