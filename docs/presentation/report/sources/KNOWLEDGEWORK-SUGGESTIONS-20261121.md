# 交给 knowledgeWork 的报告/PPT 修改建议

本轮未编辑 `docs/presentation/report/report.md`、`report.docx`、`report.pdf`，也未编辑任何 pptx。下面是需要改的确切段落和建议页。视频完成后再把录屏来源和路径写进文档。不要新增 pytest（会改变 77 项收集数），也不要把幻灯片加到第 10 页（`tests/test_final_deck.py` 断言 9 页）。不要把本机 77 项通过写成重新推理或课程满分。

## 报告正文与附录（当前文件）

`docs/presentation/report/report.md` 第 156 行（§7 局限、代码与AI辅助披露）现为：

> 已有补充离线审计和43项离线测试通过属于代码/记录核验，不是新的3500槽推理；43项为仓库侧回传，本报告制作未重跑该测试集。

建议改为（保留 43 为历史口径并标明日期）：

> 已有补充离线审计属于代码/记录核验，不是新的3500槽推理。报告制作当时按仓库侧回传写“43项离线测试通过”，该口径保留为 2026-11-21 报告制作时的历史记录，当时未在该报告环境亲跑。同日稍后，在已推 main `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4` 上，使用 Python 3.13.5 与 tokenizers 0.22.1，官方 prepare 配齐公开 NQ 与 DeepSeek-V4.1-Flash revision `314113f8a7dadb388215396ba5fbee2c610a04d6` 的 tokenizer.json 后，完整 `python -m pytest` 收集 77 项、全部通过，退出码 0（17:46:58–17:47:02，Asia/Shanghai）。配齐数据前同为 77 项收集、72 通过、5 失败。命令与日志见 `reports/local-verification/`。这不是本机重新做模型推理，API 调用为 0，已发表分数未改。

同文件第 226 行附录 A.2 表格“离线测试数量”现为：

> 旧36项/31项是早期口径；按最新仓库侧回传43项，未冒称本报告制作亲跑

建议改为：

> 早期口径 36 项 / 31 项应保留日期说明；报告制作时按仓库侧回传写 43 项，当时未在该环境亲跑。更早过程回传还出现过 44 项，仓库正文未见该口径。当前验收入口统一为 2026-11-21 本机完整 pytest 77 项全部通过，见 `reports/local-verification/`，不是新推理。

`docs/presentation/report/README.md` 第 17 行现为：

> 43项离线测试通过是仓库侧回传，不冒称报告制作环境亲跑。

建议在保留该句为历史说明之后，补一句当前 77 项本机结果及 `reports/local-verification/` 路径，并写明不是新推理。

`docs/presentation/report/SOURCES.md` 第 28 行现为：

> 最新43项离线测试通过由父任务回传；本报告生成未执行该测试集，未新增推理。

建议改为：保留“报告制作时 43 项由父任务回传、当时未执行”为历史记录；另列 2026-11-21 本机 77/77 的来源目录 `reports/local-verification/`（提交 `bdb11d3`）。视频完成后再把录屏文件路径补进本清单。分支头如需同步，应改为当前已推 main `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4` 及四条成员分支头，不要继续只写更早的 `fba1b89` 等观测头而不加日期。

§7 第 154 行与附录 A.3 的缺口应保留：CUDA 具体型号、阶段四 CANN、阶段二/三/四完整缓存及 sha256、受控 Cursor 结果、P 编号与四人登记信息、本人确认、录屏与计时。不要删。

## 幻灯片建议（9 页，不要加页）

当前提交稿是 `docs/presentation/final/slides.pptx` / `slides.pdf`（物理顺序 P1–P7、B1、B2）。主结果数字不必改（84.6 / 83.2、396/400、82.6 / 45.0、效率 1.12 / 6.45 秒等）。

- P1 / P7：不要写成课程包已可提交或“全部完成”。占位 zip 已生成，仍缺 P 编号和登记表四人信息。
- 若任何页或讲稿仍写“43 项离线测试”或“zip 未打”：把当前口径改为 77 项全过，并保留 43 为报告制作时的历史回传；zip 改为“占位包已生成，尚缺登记信息”。不要用 77 替换一页上的 EM。
- B1（物理第 8 页）：命令仍用 `python -m json.tool reports/stage3-main/run.json`。可在讲稿（不必改命令本身）加一句：本机离线核验记录在 `reports/local-verification/`，77 项通过不是现场推理。
- B2（物理第 9 页）：命令仍用 `python scripts/analyze_stage4.py --out /tmp/g14-stage4-audit`。同样可在讲稿注明本机重建图在 `reports/local-verification/figures/`，未覆盖已发表图。
- 成员讲稿 `docs/presentation/final/member*.md` 与 `docs/presentation/members/member3/task.md` 第 17 行仍写“离线测试 31 项通过”，建议加日期并指向当前 77 项入口，不要删 31 项子集说明。
- 口播不要把 Python 3.13.5 / tokenizers 0.22.1 与阶段四的 3.12.0 / 0.21.4 说成同一个环境。

录屏完成后再把视频文件的相对路径和时长写入 `SOURCES.md` 与验收矩阵，不在本轮重封 `NLP2026_G14_Pxx.zip`。
