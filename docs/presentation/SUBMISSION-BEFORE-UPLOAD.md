# 提交前待补

占位包名是 `NLP2026_G14_Pxx.zip`。课程规范要求 `NLP2026_G编号_P编号.zip`，P 编号要用教师确认的编号。仓库没有这个编号，也没有登记表上的四人信息。包可以供核验，不能直接上传，也没有代交延河课堂或登记表。

当前 slides 是 `docs/presentation/final/slides.pptx`（v7）。P1、P2、P7 保留结论横幅，P1–P7 正文未改。第 8 页仍是历史 CUDA 与命令 `python -m json.tool reports/stage3-main/run.json`。第 9 页为历史 NPU 记录，并真正内嵌 `evidence/core-evidence-60s.mp4`（点击播放，不自动播放）。PDF 为静态 poster 版，无 `file:///workspace`，不能用来放视频。旁置 mp4 只为独立播放。Windows 实播尚未验证。

课程原文（<https://nlp.hltbit.top/2026/materials/w01/classroom/requirements.html>）写的是包内 `contributions.md` 包含四名成员的实际贡献，选题记录写“四人信息、联系人”。没有单独要求“法定姓名”。姓名仍只来自登记表，这里不编造。

本包没有代交延河课堂，也没有填腾讯登记表。

## 包内已经放进的

| 课程路径 | 来源 |
| --- | --- |
| `report.pdf` | `docs/presentation/report/report.pdf` |
| `slides.pptx` / `slides.pdf` | `docs/presentation/final/`。早期 template 不是这份 slides |
| `README.md` | 仓库根 `README.md` |
| `code/` | `reproduction/`、`scripts/`、`vendor/` |
| `configs/` | `configs/` |
| `results/` | `reports/` 里已提交的轻量结果、13 条阶段一案例、阶段四 `metrics.jsonl` |
| `data/README.md` | `data/README.md` |
| `contributions.md` | 仓库根文件。成员二至四的亲历段仍待本人填写 |

## 还不能当作已齐

- P 编号，以及登记表上的四人信息和联系人。
- 阶段二、三、四的完整逐条输出、问答缓存、压缩缓存和它们的 sha256。这些不在 git 里，包内没有补写。
- 阶段一完整提示缓存同样在组内目录，不在本包。已入库的是 `reports/stage1-acceptance/predictions.jsonl` 和 13 条案例。
- CUDA 具体型号。阶段四 CANN 版本。阶段二 smoke 记录里的 CANN 8.5.2 不能写成阶段四的版本。
- 成员本人确认、自检勾选、真人讲述计时、延河课堂回执、Windows / PowerPoint 实播与音频听验。60 秒核心实录已完成并内嵌进 v7 演示稿，同日 50 秒测试实录仍作历史材料保留，但都不等于上述本人确认或真人讲述计时。
- Cursor 受控对话没有回答，不能写成已经替代 DeepSeek API。

`results/` 不包含中期报告 PDF，避免和根上的 `report.pdf` 混成两份正式报告。
