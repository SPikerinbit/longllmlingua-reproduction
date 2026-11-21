# G14 LongLLMLingua v10 轻量兼容版

当前提交用的演示稿是本目录 `slides.pptx` 与 `slides.pdf`（v10，9 页，16:9）。v6/v7 清单与说明仍保留为历史材料。

- `slides.pptx` SHA-256 `b2bb8abaa8fd8ea8e6d981a81b1def2d4dc4a67d0ff2d404a893636c1196182f`（7,687,902 字节）。相对已测 v9，仅更换内嵌视频为轻量兼容编码，并把第 9 页「点击右上内嵌视频播放」改为「进入本页自动播放」；其余 ZIP 部件字节未改。进入第 9 页后自动播放。内嵌部件为 `ppt/media/media1.mp4`，SHA-256 `3192f268b4a9daf937678d4bd8c154bb7b380e9723858023cbbcc099862eb3d6`，与仓库根 `evidence/core-evidence-60s.mp4` 相同。
- `slides.pdf` SHA-256 `f66aece4f5cf68b120aa14af0570f448fe9e00dda57d490b0e3d39bccdc294bd`（973,217 字节）。按 v10 画面新导出的静态海报，不含活动视频。要播放请用 PPTX。
- 轻量视频：1280×720，H.264 Constrained Baseline Level 3.1，15 fps，900 帧，无 B 帧；视频流 60.000 秒，容器 60.010 秒。先前 1080p 或 Main@L4.0 的较大文件不再作为当前旁置文件。

演讲顺序与推荐分工见 `primary-two-speakers.md`、`speaker-map.md` 和仓库 `docs/presentation/04-speaker-map.md`。推荐为两位主讲（P1–4 约 150 秒、P5–7 约 150 秒），第三人展示 60 秒自动播放证据，第四人控时与 QA；尚未获得成员本人认可。静态备选顺序仍是 1、2、3、4、5、8、6、9、7。两条证据路线二选一，不叠加。本目录 `evidence/` 指向仓库根 `evidence/`，其中旁置的 `core-evidence-60s.mp4` 只为独立播放。

LibreOffice 25.2.3.2 对上述同一 PPTX 的视觉观察（2026-11-21，Asia/Shanghai）：全屏 8→9 无需点击；约 65 秒内 25/55 秒检查点画面有变化，未见明显卡住或崩溃；约 65 秒时视频区域发黑，结束帧不能确认；返回再进入第 9 页会重新自动开始。不是 Microsoft PowerPoint 实测，声音未听验。不能声称已解决 Windows 卡死/崩溃，也不能声称逐帧连续播放或结束帧已确认。标题约 30pt、主要正文 20pt 以上、结果表 18pt 以上；原论文图、代码或 JSON 样本、图轴和来源脚注仍有既有小字，不把整页都说成 20pt。

同日较早的 50 秒测试实录 `evidence/local-offline-evidence.mp4` 与 v6/v7 校验清单仍保留为历史材料，不再作为最新入口。v7 当时的说明见 `README-v7-deliverable.md` 和 `SHA256SUMS-v7.txt`。v10 交付说明与只读核验见 `v10/`。

课程编号为 G14 / P15。仍缺：阶段二/三/四完整缓存与 sha256、CUDA 具体型号、阶段四 CANN、受控 Cursor 结果、登记表四人姓名、本人确认、真人讲述计时，以及 Windows / PowerPoint 实播与听验。
