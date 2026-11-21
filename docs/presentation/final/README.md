# G14 LongLLMLingua v7

当前提交用的演示稿是本目录 `slides.pptx` 与 `slides.pdf`（v7，9 页，16:9）。

- `slides.pptx` SHA-256 `28d542c996917dde26cffea912a2b2d9bd9af4175a4580b4175766317267957e`。P1–P7 正文未改；P8 为历史 CUDA 运行记录；P9 左侧为历史 NPU 图，右侧真正内嵌唯一的 60 秒核心实录（内部媒体 SHA-256 `e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e`）及对应 poster。放映时点击右上播放，不自动播放，无须旁置 evidence 目录。
- `slides.pdf` SHA-256 `bf86724c9843b7d744ecb364f5b0da318514e10bd8fe8ddaffd1fcac9f265d74`。静态 poster 版，不含 `file:///workspace` 链接，也无活动视频动作。要播放请用 PPTX。

演讲顺序与推荐分工见 `primary-two-speakers.md`、`speaker-map.md` 和仓库 `docs/presentation/04-speaker-map.md`。推荐为两位主讲（P1–4 约 150 秒、P5–7 约 150 秒），第三人操作 60 秒证据，第四人控时与 QA；尚未获得成员本人认可。静态备选顺序仍是 1、2、3、4、5、8、6、9、7。两条证据路线二选一，不叠加。本目录 `evidence/` 指向仓库根 `evidence/`，其中旁置的 `core-evidence-60s.mp4` 只为独立播放。

本机离线验收：完整 pytest 77 项通过，退出码 0，Python 3.13.5，tokenizers 0.22.1，提交 `bdb11d3`，原始记录时间 2026-11-21 17:46:58–17:47:02（Asia/Shanghai），见 `reports/local-verification/`。这不是新的模型推理，也不是视频里新跑出的成绩。历史分数、主比较和消融表未改。Windows / PowerPoint 实播和音频听验尚未做。标题约 30pt、主要正文 20pt 以上、结果表 18pt 以上；原论文图、代码或 JSON 样本、图轴和来源页脚仍有既有小字，不把整页都说成 20pt。

同日较早的 50 秒测试实录 `evidence/local-offline-evidence.mp4` 与 v6 校验清单仍保留为历史材料，不再作为最新入口。v6 当时的说明见 `README-local-acceptance-v6.md` 和 `SHA256SUMS-v6.txt`。

仍缺：阶段二/三/四完整缓存与 sha256、CUDA 具体型号、阶段四 CANN、受控 Cursor 结果、P 编号、登记表四人信息、本人确认、真人讲述计时，以及 Windows 实播。占位课程包不能直接提交。
