# G14 核心证据 60 秒成片（样式修正版）

生成时间：2026-11-21，时区 Asia/Shanghai（UTC+8）。
本阶段未改 PPT、未改仓库、未推送。

这是在既有 60 秒成片上的**最小样式修正**：去掉顶栏和字幕里的自我声明，GPU/NPU 简短标为「历史实验结果」。画面剪辑点、原片与补拍选用、60.000 秒时长均不变，实验数字不变。

旧顶栏版仅作内部历史，勿用于汇报：

- `/workspace/g14-core-demo/core-evidence-60s.mp4`
- `/workspace/g14-core-demo/history-old-banner/`

## 新成片

| 文件 | 说明 | SHA-256 |
| --- | --- | --- |
| `/workspace/g14-core-demo/final/core-evidence-60s.mp4` | 60.000s，1920×1080，H.264 High yuv420p 15 fps，900 帧；AAC-LC 48 kHz 立体声 | `e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e` |
| `/workspace/g14-core-demo/final/poster.png` | 海报，成片 29.900s（第 3 章 BM25 表） | `f0dcb9d32a98ee4822c44712450664f993b59d8a1553ddea65b8f5c86447b5a8` |
| `/workspace/g14-core-demo/final/core-evidence-60s.srt` | 中文字幕，已去掉自我声明 | `c5032092117b79f7e90428af2b7e5f5e10a89923410042f8004e22be770a51b7` |
| `/workspace/g14-core-demo/final/narration.wav` | 配音 60.000s，PCM s16le 48 kHz 立体声 | `29fe007d963cdd84a6a05684f71bd694ba7b00d6b10fc4e47459f59bcbfb0291` |
| `/workspace/g14-core-demo/final/narration.mp3` | 同一配音的 MP3 | `18f108ad1c9cb4fcfc8a12756d4d902461ff0514659741c5a41781638a35f9ec` |
| `/workspace/g14-core-demo/final/NARRATION.md` | 讲解文稿 | — |
| `/workspace/g14-core-demo/final/SHA256SUMS.txt` | 校验和 | — |

成片体积 11,550,287 字节。

版式与旧版相同：源 1920×1200 等比缩小为 1536×960，顶栏 40 px、底栏 80 px，右侧 384 px 边栏。顶栏现为简洁标题「LongLLMLingua 复现演示」，不再写合成、非真人、非现场或语速。字幕在底栏，不覆盖终端正文。第 5、6 章边栏标签为「历史实验结果」。第 3 章边栏仍标明 CPU 结果与 Long 代码仅展示、未执行。

## 本次相对旧版改了什么

- 删除开场自我声明（「中文合成讲解」「非现场真人」「画面已剪辑」），改为直接讲：CPU做压缩与评分，GPU、NPU为历史实验结果。
- 第 5 章「后两表是历史记录，不是新推理」改为「后两表是历史实验结果。」后一句数字不变。
- 第 1–4、6 章配音未重录，时间轴保持原样。开场与第 5 章重读后按原槽位补齐静音（开场 4.896s 补到 10.488s；第 5 章 5.952s 补到 6.456s）。
- 剪辑技术说明只写在本文件，不放在顶栏。

未改：60 秒结构、各章源片段与起止、样本补拍选用、实验结果数字、现场 CPU 压缩/评分与历史 GPU/NPU 的区分方式（只改了用词）。不要把本片说成真人原声、一镜到底，或本次现场重跑 GPU/NPU。

## 时间轴（与旧版相同）

| 成片时间 (s) | 段 | 源文件 | 源内时间 (s) | 速度 | 内容与配音 |
| --- | --- | --- | --- | --- | --- |
| 0.000–17.384 | V1 | G14-core-raw.mp4 | 26.333–43.717 | 1× | 第 1 章入口与锁定配置。开场新词 + 原第 1 章配音 |
| 17.384–24.775 | V2a | G14-core-sample-pickup.mp4 | 19.200–26.591 | 1× | 第 2 章样本：QID、问题、位置 1、20 篇文档 |
| 24.775–27.904 | V2b | G14-core-sample-pickup.mp4 | 8.000–11.129 | 1× | 字段隔离与 Kangla Palace 原文（源时间早于 V2a，为跟解说对齐） |
| 27.904–32.204 | V3a | G14-core-raw-part2.mp4 | 7.000–10.800 | 1× | BM25 表 3289→1644→822，4× 丢掉 gold |
| 32.204–37.888 | V3b | G14-core-raw-part2.mp4 | 10.800–14.750，随后短定格 | 1× | gold 丢失摘录；Long 源码仅展示、未执行 |
| 37.888–41.884 | V4a | G14-core-raw-part2.mp4 | 14.800–18.796 | 1× | 对已保存回答的现场评分 |
| 41.884–46.864 | V4b | G14-core-raw-part2.mp4 | 27.000–31.680 | 1× | S1-03 与 S1-08 边界例 |
| 46.864–53.520 | V5 | G14-core-raw-part2.mp4 | CUDA 主比较表及短定格 | 1× + 定格 | 历史实验结果：84.6% / 83.2% / −1.4pp，区间跨 0 |
| 53.520–60.000 | V6 | G14-core-raw-part2.mp4 | 49.533–55.461 | 1× | 历史实验结果：消融 82.6%→45.0%，压缩未加快端到端 |

更细的源时钟、不用的原片段和旧版制作说明见 `/workspace/g14-core-demo/history-old-banner/EDIT-MAP.md`。
