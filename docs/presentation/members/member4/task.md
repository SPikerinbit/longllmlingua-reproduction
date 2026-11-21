# 成员四：任务、证据和验收

口播 P6 的 60 秒，加运行证据后 30 秒。另外负责 11-22 16:00 把四份材料收成一份 pptx 和报告源稿，以及 22:30 之前把 zip 交给联系人上传。联系人若就是成员四，在贡献段写明；仓库没有写联系人是谁。

法定姓名待本人填写。不要把 CUDA 主比较的 83.2% 写成自己这次 910B 参照的 82.6%。

## 验收标准

- [ ] P6 第一句就区分 82.6（910B，n=500）和 83.2（CUDA 主比较）。
- [ ] 口播三个数：去掉粗粒度 45.0%，区间 [−47.2, −28.4]；去掉动态预算 78.0%，区间 [−8.6, −0.8]；去掉恢复 83.2%，并有 3 个槽由对变错。
- [ ] 效率说出完整 2x 端到端 p50/p95 为 6.45/7.49 秒，原始提示 1.12/1.54 秒，n=99。页上若写 16.43 GB，同时能指到 `efficiency.csv` 的 16.428089344。
- [ ] 右侧使用仓库里的 `ablation.png`，不覆盖该文件。图内 10 pt 不充当幻灯片正文。
- [ ] 30 秒内打开 `analyze_stage4.py` 的命令、`environment-current.json` 的 Ascend910B4、`coverage.json` 的 3500 和 1200。不加载模型。
- [ ] 说明 `analyze_stage4.py` 会重写 csv。2026-11-21 本机一次运行是 0.337 秒，随后已恢复文件。现场演示后不要提交覆盖。
- [ ] 报告第 7 节约 1.0 页，包含 3 个恢复案例的 question_id。
- [ ] `tokenizers` 0.21.4（`environment-current.json`）和 `package-versions.json` 里的 0.21.0 不一致。口播用 0.21.4，并承认另一个文件不同，不把它们说成笔误已经查清，除非本人查清并写进贡献段。
- [ ] 汇编时不改 P1/P2/P7 的数字。正文 PDF 4–6 页。
- [ ] QA 至少 5 题。贡献段已替换。

## (a) 实验证据清单

| 项 | 命令或入口 | 配置 | 记录 | 对应数字 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 云端包装 | `python scripts/cloud910b.py check` 只打印环境；`run` 才会跑 | 实际消融配置是 `configs/stage4-ablation.json`，split=pilot。效率是 `configs/stage4-efficiency.json` 与 `configs/cloud/efficiency-final.json`，split=smoke | 不要用 `cloud910b.py` 的默认 `--config configs/cloud/main.json`，那个默认文件在当前仓库里不存在 | 入口 | 命令已有。默认路径是历史写法，现场命令必须显式带 `--config` |
| 消融运行 | 组内 910B 上的 stage3 引擎，经 cloud 包装 | run `a9d2295195adde90484d` | `inputs/ablation-run.json`、`inputs/validation.json` | 3500/3500，EM 表 | 轻量记录已有。`results.jsonl` 在返回包 |
| 返回包路径 | `docs/experiments.md` 的重评分命令 | `--ablation data/final/outputs/stage3/a9d2295195adde90484d` | validation 写 run.json 与 results.jsonl 与已核验版本逐字节相同 | 可复用重放证据 | 路径已写。本工作区没有 `data/final/`。成员四补 sha256 |
| 效率运行 | 独立会话，不与消融拼接 | run `2a7f4accf6127178a76b`，`inputs/efficiency-run.json` | `coverage.json` 效率 1200/1200，failed 0 | n=99 的来源是先 100 再去掉每方法首个样本 | 已有 |
| 重建表 | `python scripts/analyze_stage4.py` | 读 `inputs/metrics.jsonl` | 写出 ablation.csv、efficiency.csv 等 | P6 全部数字 | 已有。命令会覆盖 csv。本机 0.337 秒 |
| 重建图 | `python scripts/plot_results.py` | 需要 matplotlib==3.10.0 | 已提交 png/pdf | P6 右图 | 已有。本机 1.413 秒，会覆盖图，演示用已提交的 png |
| 环境 | 打开即可 | — | `environment/environment-current.json`、`npu-smi.txt` | Ascend910B4；HBM 总量 32768 MB 写在 `docs/experiments.md` | 已有。CANN 版本未登记，不要补 |
| 恢复案例 | 打开即可 | 离线移除恢复，不新增问答 | `inputs/recovery-cases.json` 三条 | M4-01 到 M4-03 | 已有。缺的是“方法名”一句：它们来自完整方法同一回答，见 `docs/experiments.md` |
| 机制是否真的变了 | 打开即可 | — | `received-mechanism-checks.json` | 报告里“各变体提示有变化” | 已有 |
| 旧效率 | 不进主表 | run `6fa24e170b73981099fd` | HTTP 402，738 成功、1 失败、461 缺失 | 只在被问到时说排除 | 数字在 `docs/experiments.md`。原始日志在组内归档 |
| usage | 打开即可 | — | `usage.json` 效率块输入 1694940、输出 85588 | 只报 token | 已有。不要和消融块的 5762538 / 259603 相加 |

30 秒现场顺序在模板第 8 页右栏。备份录屏 TODO：`results/demo/member4-evidence.mp4`，内容是分析命令的终端加上 `environment-current.json`，不要加载 7B 模型。

独立核验：`inputs/validation.json` 的 `passed` 为 true；消融恢复重放 3000，效率恢复重放 700。要再跑时用实验说明里的 `validate_received.py`，tokenizers 0.21.4，输出写到 `outputs/`，不覆盖已提交的 validation。没有原始包就不要声称这次又重放了一遍。

## (b) 需制作材料明细

| 交付物 | zip 位置 | 格式和篇幅 | 截止（北京时间） | 核验人 | 验收 |
| --- | --- | --- | --- | --- | --- |
| P6 | `slides.pptx` 第 6 页 | 60 秒 | 11-22 12:00 定稿措辞 | 成员三看 82.6 与 83.2 分开 | 三个关键差值和区间都在 |
| 证据后 30 秒 | 运行证据页右栏，加 mp4 | 30 秒 | 11-22 18:00 | 成员三 | 能指到 Ascend910B4 和 1200 |
| 报告第 7 节 | `report.pdf` | 约 1.0 页 | 11-22 12:00 | 成员三 | 含 3 个 question_id |
| 案例 | `results/cases/M4-01.md` 起 | 直接整理 recovery-cases 的 3 条 | 11-22 12:00 | 成员一看 score 从 1 到 0 是否按首行口径解释 | 与 json 原文一致 |
| 环境与表 | `results/stage4/` | 复制 RESULTS.md、两份 csv、coverage、environment-current、validation、recovery-cases | 11-22 16:00 自己复制 | 成员三 | 复制后 EM 仍是 82.6 和 45.0 |
| 贡献段 | `contributions.md` | 替换占位 | 11-22 12:00 | 成员三 | 写明两台机器 |
| 汇编 | 最终 `report.pdf`、`slides.pptx`、`slides.pdf`、zip 根 `README.md` | 正文 4–6 页；pptx 与 pdf 一致 | 11-22 16:00 收口，18:00 后不改数字，22:30 交给联系人 | 四人各看自己的页 | 页数、字号、无密钥 |
| QA | 不进 zip | 至少 5 题 | 11-22 12:00 | 本人 | 见下 |

汇编 README 必须包含：环境版本（引用 environment-current，并注明 tokenizers 两个文件不一致）、`python -m reproduction prepare`、四条阶段入口、`analyze_stage4.py` 的耗时说明、预期输出路径。没有单价就不写金额。

## QA

Q1 为什么 910B 的完整方法是 82.6 不是 83.2？15 秒：83.2 是成员三 CUDA 主比较。82.6 是同一 100 题在 Ascend 910B4 上重新跑的同机参照，用来和消融比。两套都成功 500 槽，但是硬件记录不同。依据 README 和 `RESULTS.md`。

Q2 哪个组件影响最大？15 秒：去掉粗粒度后 45.0%，差 −37.6 pp，区间不跨 0。细粒度、restrict、重排序的区间跨 0。动态预算的区间也不跨 0，但是差值只有 −4.6 pp。不能说：只有粗粒度有用，把动态预算说成没有差别。

Q3 恢复为什么 EM 更高还算负面？15 秒：去掉恢复是 83.2%，相对 82.6 高 0.6 pp，区间 [0.0, 1.6]。同时 `recovery-cases.json` 有 3 个槽从 1 变成 0。主指标仍是首行 EM，案例保留。不能说：恢复提高了准确率所以应该默认打开，而不提这 3 条。

Q4 为什么压缩更慢？15 秒：完整 2x 端到端 p50 6.45 秒，其中压缩 p50 约 5.23 秒，原始提示端到端 p50 1.12 秒。问答时间差不多，压缩把时间加上去了。n=99，不是 100。不能说：服务端没有缓存。实验说明写 API 的 prompt cache 没有关。

Q5 峰值内存怎么读？15 秒：`efficiency.csv` 的 peak_allocated_GB 是 16.428089344，按 1e9 字节。HBM 总量 32768 MB 是设备容量，不是这次峰值。不要把阶段二 REPORT 的 16.67 GB 和这个 16.43 GB 当成同一次测量。

Q6 旧的 402 运行进表了吗？15 秒：没有。run `6fa24e170b73981099fd` 是 738 成功、1 失败、461 缺失，留在组内归档。最终表只用 `2a7f4accf6127178a76b`。

## 课程五项里由成员四讲解的证据

继续在 `stage4-ablation-efficiency` 上推进。对照 `docs/presentation/02-score-evidence.md`。被点名时按这个顺序打开文件。未勾选项不能说成已经复核。

| 项 | 打开什么 | 8 分目标下还缺的 |
| --- | --- | --- |
| 理解与范围 | `docs/experiments.md`：消融与效率分开登记，不拼接 CUDA 耗时 | 不能把 82.6 说成主比较的 83.2 |
| 数据与实现 | `environment/environment-current.json`；权重 revision 在 `docs/experiments.md` | `package-versions.json` 的 tokenizers 0.21.0 与 0.21.4 不一致，原因未写清前不能勾成单一环境 |
| 对照与消融 | `ablation.csv` 与 `configs/stage4-ablation.json`；一次只改一个开关 | 重排序是额外打开，不是再做一次“关闭重排序” |
| 错误分析 | `inputs/recovery-cases.json` 三条由对变错 | 还要拆成 M4-01 至 M4-03，并收齐别人的案例到至少 10 条 |
| 交付与答问 | `python scripts/analyze_stage4.py` 是离线重建，会改写 csv | 现场用已提交的 csv 和 png。录屏与终稿 PDF 未做 |

真实运行在 910B 上，run `a9d2295195adde90484d` 与 `2a7f4accf6127178a76b`。`python -m pytest tests/test_stage4_results.py tests/test_stage4_recovery_analysis.py tests/test_final_delivery.py` 不加载模型。CANN 版本未登记，不能补写。
