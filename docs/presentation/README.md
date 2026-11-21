# G14 终稿汇报材料

这里是 2026-11-22 24:00（北京时间）延河课堂提交和 8 分钟汇报用的共享稿。实验数字只引用仓库里已经写明的结果。P 编号仓库里没有，包名暂时写 `NLP2026_G14_Pxx.zip`。

课程要求的原文在 <https://nlp.hltbit.top/2026/materials/w01/classroom/requirements.html>。

| 文件 | 用途 |
| --- | --- |
| [00-division-of-labor.md](00-division-of-labor.md) | 时间、页码、报告章节、案例份额、总表、整合流程 |
| [01-number-registry.md](01-number-registry.md) | 可以上台的数字和它们的文件 |
| [02-score-evidence.md](02-score-evidence.md) | 课程五项各 8 分的已有证据、缺口和未勾选阻塞项 |
| [templates/](templates/) | 幻灯片、报告、QA、贡献、自检的空表 |
| [slides/pptx-usage.md](slides/pptx-usage.md) | 配色、字体、字号和怎么改模板 |
| [slides/G14-LongLLMLingua-template.pptx](slides/G14-LongLLMLingua-template.pptx) | 9 页：P1–P7、运行证据、备份 |
| [slides/previews/](slides/previews/) | LibreOffice 渲染的 PDF 和 PNG |
| [members/member1/](members/member1/) | 成员一的定稿页、讲稿、报告小节、案例、QA、自检 |
| [members/member2/task.md](members/member2/task.md) | 成员二的证据清单、材料清单和验收 |
| [members/member3/task.md](members/member3/task.md) | 成员三的证据清单、材料清单和验收 |
| [members/member4/task.md](members/member4/task.md) | 成员四的证据清单、材料清单和验收 |

P1、P2、P7 已由成员一定稿。P3–P6 和运行证据页填的是仓库数字和建议句，负责人可以改措辞，不能改数字，也不能改配色。

继续推进用这四条分支，都已经包含 `main` 的 `87a70d1e4b4343eb6a2c4173a651949bf66321b9`：

| 成员 | 推荐分支 |
| --- | --- |
| 一 | `stage1-foundation` |
| 二 | `stage2-compression` |
| 三 | `stage3-main-comparison` |
| 四 | `stage4-ablation-efficiency` |

`stage_3` 仍保留，不删除。它停在已并入 `main` 的旧提交上，只为已经 checkout 过的人兼容，不再往上推新工作。文档里的 `reports/stage3-main/` 是结果目录，不是分支名。

各分支只放共享文档、模板和本人的 `members/memberN/task.md`。成员一的定稿幻灯片、讲稿、报告初稿、案例、QA、自检、`data/README.md` 和 `contributions.md` 在 `stage1-foundation`。这些材料没有合入 `main`。
