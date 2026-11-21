# 课程验收矩阵

这不是终稿，也不是满分承诺。状态只有三种：通过、未完成、资源阻塞。通过只表示仓库里的检查已经跑过，不表示该成员已经亲自核验。代做的补充不能替本人勾选自检。

页数还没有最终批准。这里的 P1–P7 是功能占位，不是已经确定的页码。

| 提交项 | 证据 | 阶段 | 命令或结果 | 状态 |
| --- | --- | --- | --- | --- |
| 报告正文 | `docs/presentation/report-draft.md` | 全部 | 源稿，尚未导出 report.pdf | 未完成 |
| slides.pptx / slides.pdf | `docs/presentation/final/slides.pptx` 与同目录 `slides.pdf` | 全部 | 9 页演示稿已入库。课程终包 zip 未打，投影和真人计时未做 | 未完成（终包） |
| README 结果入口 | `README.md` | 全部 | 指向已有 DeepSeek 结果和阶段一离线审计 | 通过（入口）；终稿包装未完成 |
| code/ 与 configs/ | `reproduction/`、`scripts/`、`configs/` | 全部 | 离线测试可导入这些模块 | 通过（代码在库内）；zip 未打 |
| data/README.md | `data/README.md`、`manifests/resources.json` | 一 | 五个 gz 的 sha256 已在清单中 | 通过（说明）；gz 本身不进包 |
| 阶段一轻量结果 | `reports/stage1-acceptance/` | 一 | 300/300，EM 0.92/0.87/0.64 | 通过 |
| 阶段一离线复核 | `reports/stage1-supplement/offline-audit.json` | 一 | `scripts/audit_stage1_offline.py`，2.055 秒，API 0 | 通过 |
| 阶段二记录一致性 | `reports/stage2-supplement/offline-audit.json` | 二 | 400 行、预算 396+4，没有重新压缩 | 通过（核对）；新压缩运行资源阻塞 |
| 阶段三记录一致性 | `reports/stage3-supplement/offline-audit.json` | 三 | 3500 槽，统计均值与 summary 一致 | 通过（核对）；新的 Cursor 配对比较资源阻塞 |
| 阶段四记录一致性 | `reports/stage4-supplement/offline-audit.json` | 四 | 消融 3500、效率 1200、恢复负面 3，没有重写原表 | 通过（核对）；新消融资源阻塞 |
| Cursor 问答 | `reports/cursor_dialogue/PROTOCOL.md` | 问答设置 | 无关卡通过的回答；评分脚本无回复时退出码 2 | 资源阻塞 |
| 至少 10 条真实案例 | `reports/stage1-supplement/cases.md` 的 13 槽 | 一 | 来自既有 predictions.jsonl | 通过（DeepSeek） |
| 阶段二/三逐条案例 | 组内 results.jsonl 不在 git | 二、三 | 不能用对话补写 | 资源阻塞 |
| 阶段四恢复案例 | `inputs/recovery-cases.json` 3 条 | 四 | 由对变错，尚未拆进 results/cases | 未完成（整理） |
| contributions 本人段 | `contributions.md` | 全部 | 成员二至四的亲历段仍是待填；代做部分已标明 | 未完成 |
| 最终 zip | 无 | 全部 | PPT 与逐条全文都未收齐 | 未完成 |

| 评分项 | 已有证据 | 负责阶段 | 状态 |
| --- | --- | --- | --- |
| 论文理解与范围 | 论文版本、100 题范围、未实现的 k=2 与 τ | 一、二 | 通过（范围说明）；P 编号未完成 |
| 数据与实现 | 清单 sha256、可见字段隔离、阶段一重评分 0 不一致 | 一 | 通过（离线）；新环境亲跑资源阻塞 |
| 对照指标与消融 | 阶段三 3500 槽与阶段四单因素表互相一致 | 三、四 | 通过（既有记录）；新跑资源阻塞 |
| 错误分析与结论 | 13 条阶段一槽；4 条否认仍得 1 分只作诊断 | 一、四 | 通过（DeepSeek 案例）；Cursor 案例未完成 |
| 交付与答问 | 命令和文件路径已写；本人答问未做 | 全部 | 未完成 |

个人熟悉任务、现场口播和自检表都不因这次代做而勾选。
