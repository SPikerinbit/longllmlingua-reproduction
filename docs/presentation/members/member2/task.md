# 成员二：任务、证据和验收

当前演示稿里，成员二讲物理页 3（P3，45 秒）和页 4（P4，45 秒），合计 90 秒。讲稿在 `docs/presentation/final/member2-script.md`。法定姓名待本人填写。这 90 秒还没有用秒表核过。

## 验收标准

- [ ] P3 口播不超过 45 秒，并说出：同一 Llama-2-7B-Chat 权重、粗粒度 / 细粒度 / 动态比率 0.3、主比较 `reorder_context=original`、k=2 无效、τ_ins 与 τ_que 未实现。
- [ ] P3 保留“100/100 个样本的保留文档不同于 LLMLingua”，来源 `reports/stage2-smoke/REPORT.md` 第 4 节。
- [ ] P4 表保留五行对照：deepseek-flash、硬预算加 DeepSeek tokenizer、恢复用 DeepSeek tokenizer、cuda:0 无型号、Ascend 910B4 与 HBM 32768 MB。来源 `docs/stage2-parameter-map.md` 与 `docs/experiments.md`。
- [ ] P4 说出 4 条超标：目标 742，实测 749、751、754、753，slot 前缀 `23707ea62773`，文件 `reports/stage2-smoke/verification.json`。
- [ ] 同时说出阶段三另有 18/500，满足率 0.964，避免听众以为只有 smoke 超标。
- [ ] 标题 ≥28 磅，正文 ≥20 磅，表 ≥18 磅。不改模板配色。
- [ ] 报告第 4、5 节约 1.4 页，使用 `templates/report-section.md`。
- [ ] 案例 M2-01 到 M2-03 已从真实槽选出，其中一条必须是上面的超标槽。
- [ ] QA 至少 5 题，答案能指到文件。
- [ ] `contributions.md` 的成员二段已替换“待本人填写”。
- [ ] 没有把阶段一的 92% 或阶段三的 83.2% 说成自己 smoke 的结论。smoke 的 LongLLMLingua 2x 是 0.940，只代表 20 题。

## (a) 实验证据清单

| 项 | 命令或入口 | 配置 | 记录 | 对应数字 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 压缩计划 | `python -m reproduction.stage2 plan` | `configs/stage2.json`，split=smoke | 应得到 20×5×4=400 槽 | 矩阵大小 | 命令已有。本环境无权重，未重跑 |
| 正式运行 | `python -m reproduction.stage2 run` | 同上 | `outputs/stage2/a1bd26fe3d82dea3f65d` | 400/400 | 目录不在 git。`REPORT.md` 写开始 2026-11-07 02:04:10，结束 02:51:19 |
| 汇总 | `python -m reproduction.stage2 summarize <run_dir>` | — | `reports/stage2-smoke/summary.json` | 四行 EM 0.62、0.46、0.94、0.88 | 汇总已有。重跑汇总需要组内 results |
| 验收 | `python scripts/accept_stage2.py <run_dir>` | — | `verification.json` 的 `passed: true` | 396/400；恢复重放 200 槽 | 结果已有。脚本重跑需要组内全文 |
| 案例簿 | `python -m reproduction.stage2 casebook <run_dir>` | — | 仓库有 `casebook.md` | 选 M2 案例 | 已有一份。确认它是否含超标题；若没有，从 verification 的 slot 去组内 results 补 |
| 开关探针 | `python scripts/npu_switch_probe.py` | 输出路径在 REPORT 里写成 `data/scratch/npu/switch_probe.json` | 同一题 origin 3289 token 的六行对照 | P3 的机制说明 | 缺失。REPORT 写明该 json 未入库。要么补路径和 sha256，要么幻灯片只保留已经入库的 100/100 |
| 权重 | 不在仓库 | revision `351844e75ed0bcbbe3f10671b3c808d2b83894ee` | `docs/experiments.md` | P3 | 已有记录。权重文件不进 zip |
| 硬件 | 阶段二历史环境与阶段四不同 | REPORT 写 CANN 8.5.2、910B4、加载 1.94 秒、上卡 5.88 秒、峰值 16.67 GB | 只在讲阶段二 smoke 时使用 | 不要把 16.67 GB 说成阶段四效率表的 16.43 GB | 已有于 REPORT。阶段四以 `environment-current.json` 为准 |
| 逐条全文 | 组内 `results.jsonl` | — | REPORT 写约 8.6 MB，不入库 | 案例原文 | 缺失。成员二补路径和 sha256 |
| 轻量样本 | 打开即可 | — | `accepted-sample.jsonl` 目前是 4 行示例，不是 400 行 | 不能把它说成全量逐条输出 | 已有，但是样本 |

现场 1 分钟不是成员二的。提问备用，20 秒内打开：

1. `verification.json` 的 `budget_misses`。
2. `docs/stage2-parameter-map.md` 里 k=2 那一行“未暴露”。
3. `REPORT.md` 第 4 节的 100/100。

独立核验：读 `verification.json` 的 `budget_satisfied` 396 和 4 条 `tokens`。不要在没有权重的机器上重新压缩。`scripts/verify_member2_handoff.py` 是成员四一侧的核查入口，成员二要知道它的存在，但不把别人的核查说成自己又跑了一遍，除非自己真的执行并保留输出。

## (b) 需制作材料明细

| 交付物 | zip 位置 | 格式和篇幅 | 截止（北京时间） | 核验人 | 验收 |
| --- | --- | --- | --- | --- | --- |
| P3、P4 | `slides.pptx` 第 3–4 页 | 合计 90 秒；表 ≥18 磅 | 11-22 12:00 推送讲稿；16:00 前确认数字没被汇编改掉 | 成员一核“答案不进提示”，成员四核硬件两行 | 与 parameter-map 逐行对 |
| 讲稿 | 不进 zip | 按 `templates/slide-page.md` 写到秒 | 11-22 12:00 | 成员四在 20:00 计时 | ≤90 秒 |
| 报告第 4、5 节 | `report.pdf` | 约 0.8+0.6 页 | 11-22 12:00 | 成员一 | 出现 100/100、4 条超标、τ 未实现 |
| 案例 3 条 | `results/cases/M2-01.md` 起 | 每条含 slot_id、问题 ID、score、是否超预算 | 11-22 12:00 | 成员四 | M2-01 的 token 是 749、751、754 或 753 之一 |
| QA | 不进 zip | 至少下面 5 题 | 11-22 12:00 | 本人读一遍 | 答案路径存在 |
| 贡献段 | `contributions.md` | 替换成员二占位 | 11-22 12:00 | 成员四 | 含 run_id `a1bd26fe3d82dea3f65d` |
| 阶段二结果 | `results/stage2/` | 复制 REPORT、summary、verification、run.json 的可公开字段 | 11-22 16:00 由成员四复制，成员二确认 | 成员四 | 复制件里没有密钥 |
| 组内全文 | `results/stage2/SOURCE.txt` | 路径和 sha256 | 11-22 12:00 | 成员四 | 没有就写未取得 |
| 录屏 | 可选 | 提问备用，≤20 秒 | 11-22 18:00 | 成员四 | 60 秒主证据不靠这条 |

## QA

Q1 为什么 k=2 不做消融？15 秒：固定提交的 `compress_prompt` 没有 k 参数，传入的 `context_level_target_token` 在当前 LongLLMLingua 路径没有被使用。`stage2-parameter-map.md` 写明不能称为等价。不能说：我们用 2 倍 target 近似了 k。

Q2 restrict 有没有进问答提示？15 秒：没有。它只加在文档级条件困惑度的问题上。开关是本组加的，官方不可配。依据同一份映射表的 restrict 行。

Q3 恢复用什么分词器？15 秒：DeepSeek tokenizer，不是论文的 LLaMA-2 tokenizer。smoke 上 2x 恢复前后 EM 都是 0.940，改变了 9 条回答。依据 `verification.json` 的 `changed_answers`。

Q4 4 条超标怎么处理？15 秒：保留 `budget_satisfied=false`，不改分数。目标 742，实测 749、751、754、753。不能说：四舍五入后算满足。

Q5 阶段二的 0.940 能不能当主结果？15 秒：不能。那是 20 题。100 题主比较的 LongLLMLingua 2x 是 83.2%，而且机器记录不同。依据 README 和 `summary.json`。

Q6 动态比率 0.3 是否等于论文的 δτ？15 秒：参数值是 0.3，但映射表写库实现是按排名线性分配，和论文对整体预算的描述不完全相同。要在报告第 5 节说这句。不能说：完全一致。

## 课程五项里由成员二讲解的证据

继续在 `stage2-compression` 上推进。对照 `docs/presentation/02-score-evidence.md`。被点名时按这个顺序打开文件。未勾选项不能说成已经复核。

| 项 | 打开什么 | 8 分目标下还缺的 |
| --- | --- | --- |
| 理解与范围 | `docs/stage2-parameter-map.md` 中 k=2、τ_ins、τ_que 三行 | 不能把未暴露参数说成已复现 |
| 数据与实现 | `reports/stage2-smoke/REPORT.md` 的模型、revision 记录在 `docs/experiments.md`；硬件 CANN 8.5.2 只属于这次 smoke | 权重不在 git 中。`data/scratch/npu/switch_probe.json` 未入库，P3 只能使用已入库的 100/100 |
| 对照与消融 | `verification.json`：400 槽，硬预算 396，4 条目标 742 | 这是 20 题。100 题主比较不由本页的 0.940 代替 |
| 错误分析 | 4 条超标的 slot 前缀 `23707ea62773` | M2-01 至 M2-03 还没有从组内 results.jsonl 摘出 |
| 交付与答问 | 入口 `python -m reproduction.stage2` | 在没有权重的机器上不能勾“本次重新压缩通过” |

离线记录是打开 `reports/stage2-smoke/verification.json`。真实运行是 `python -m reproduction.stage2 run`。二者不要混称。密钥不写入 REPORT 或案例。
