# 第二阶段 smoke 验收报告

结论：**通过**。smoke 20 题 × 5 位置 × 4 方法 = 400 个槽位全部真实完成，
LLMLingua 与 LongLLMLingua 在 2x/4x 均可运行；硬预算满足 396/400（99.0%），
其余 4 条为如实记录的轻微超标；开关行为有探针对比证据；离线验收脚本通过；
完整方法输出可直接交给第三阶段。

## 1. 运行与环境

| 项 | 值 |
| --- | --- |
| 运行目录 | `outputs/stage2/a1bd26fe3d82dea3f65d` |
| 配置哈希 / 实现哈希 | `bbaa854bd830f8e1…` / `b9de0421e01d1439…` |
| 开始 / 结束 | 2026-11-07 02:04:10 / 02:51:19（约 47 分钟） |
| 集合 | smoke：20 题 × 位置 1/5/10/15/20 × 4 方法 |
| 压缩模型 | `NousResearch/Llama-2-7b-chat-hf`（LLaMA-2-7B-Chat 的无门槛镜像，13.48GB fp16） |
| 压缩硬件 | ModelArts Ascend 910B4（32GB HBM），CANN 8.5.2，torch 2.7.1 + torch_npu 2.7.1.post2 |
| 加载 / 上卡 / 峰值显存 | 1.94s / 5.88s / 16.67GB |
| 问答模型 | deepseek-flash（非思考，temperature=0，max_tokens=512），与阶段一相同 |
| 预算模式 | hard（`max_budget_passes=3`，每轮按实测收紧 rate） |
| 分词器 | 固定 DeepSeek 分词器，完整提示口径（含 instruction 与 question） |
| API 用量 | 输入 437,149 token，输出 30,655 token（400 槽中 386 条新请求，14 条提示内容与更早槽位相同而命中问答缓存） |

模型完整性由独立复核确认：两个 shard 共 13.48GB，sha256 与 HF LFS 逐字节一致，
323 个 tensor、index header 校验 match=True；3072-token 前向 0.95s，HBM 峰值 16.67GB。
NPU 上的适配要点：`device_map="cpu"` 加载后 `.to("npu:0")`（库只认 cuda/cpu/mps 子串）、
`attn_implementation="eager"`、以及必需的 legacy KV → `DynamicCache` 桥接
（transformers 4.53.1 拒绝 legacy tuple；CPU/GPU 上同样会失败，非 NPU 特有问题）。

## 2. 主结果（smoke，EM 为上游 best_subspan_em）

| 方法 | 位置 1 | 5 | 10 | 15 | 20 | 平均 EM | 平均实际比值 | 平均压缩耗时 | 预算满足率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| llmlingua_2x | 0.55 | 0.70 | 0.65 | 0.55 | 0.65 | 0.620 | 2.05x | 6.7s | 100% |
| llmlingua_4x | 0.45 | 0.45 | 0.45 | 0.45 | 0.50 | 0.460 | 4.17x | 5.3s | 100% |
| longllmlingua_2x | 0.90 | 0.90 | 0.90 | 1.00 | 1.00 | 0.940 | 2.09x | 4.9s | 100% |
| longllmlingua_4x | 0.90 | 0.90 | 0.90 | 0.80 | 0.90 | 0.880 | 4.10x | 6.0s | 96% |

参照：同一 smoke 上阶段一 original 平均 EM 92%、BM25 2x 87%、BM25 4x 64%
（`reports/stage1-acceptance/REPORT.md`）。这里的 LongLLMLingua 与 LLMLingua 差距
主要是问题感知机制带来的，符合方法预期；smoke 只有 20 题，不能当作论文级结论。

## 3. 预算与实际比值

- 2x：LongLLMLingua 实测 2.08–2.09x、LLMLingua 2.05x；4x：LongLLMLingua 4.09–4.12x、
  LLMLingua 4.16–4.18x。均按"原始完整提示 token / 压缩后完整提示 token"实测，不取库自报 ratio。
- 全部 400 槽中 386 条为本轮新请求（14 条内容相同、复用已保存回答，未重复计费）；
  其中 396 条满足 `prompt_tokens ≤ floor(origin/ratio)`；4 条未满足，全部来自同一题的
  `longllmlingua_4x`（目标 742，实测 749/751/753/754，超标 0.9%–1.6%，3 轮重试后停止）。
  这 4 条已如实记录（`budget_satisfied=false`、`attempts` 完整保留），不隐藏、不改写分数。
- 自然压缩结果（库的首次单轮结果）也保留在 `trace.attempts[0]`，用于对照"不强制预算"时的比值。

## 4. 开关行为证据（同一题、20 文档、origin 3289 token）

来源：`scripts/npu_switch_probe.py`（压缩-only，不调 API），结果见
`data/scratch/npu/switch_probe.json`（本地未入库）。

| 变体 | 压缩后 token | 实际比值 | 保留文档顺序 | 动态偏移 | 现象 |
| --- | ---: | ---: | --- | --- | --- |
| longllmlingua_2x（主配置） | 1583 | 2.08x | 0,1,2,4,5,6,7,8,9,12,15 | 如 0.24/−0.30/0.30/−0.18 | 基准 |
| 关闭 restrict | 1567 | 2.10x | 0,1,2,5,6,7,8,9,12,14,15 | 变为另一组 | 文档分数重排（首位由文档 2 变 0）、保留集合变化 |
| 关闭问题感知细粒度 | 1589 | 2.07x | 同基准 | 同基准 | 压缩文本与 token 数变化，耗时 4.7s→2.7s |
| 关闭动态预算 | 1600 | 2.06x | 同基准 | 全 0 | 逐文档偏移消失、总预算改变 |
| 重排序 `sort` | 1638 | 2.01x | 2,0,12,5,7,8,15,6,4,9,1 | 按新序 | 最终提示中文档顺序改变 |
| llmlingua_2x | 1572 | 2.09x | 0,1,3,4,5,6,7,9,11,12,18 | 全 0 | 无 restrict、文档分数与保留集合不同 |

矩阵层面：问题感知排名使保留文档在 **100/100** 个样本上与 LLMLingua 不同
（验收脚本逐样本比较 `used_doc_ids`），这是粗粒度机制在真实样本上生效的直接证据。

## 5. 子序列恢复

- 恢复在问答之后执行，只处理回答文本；逐槽保存 `answer`、`answer_before_recovery`、
  `answer_after_recovery`，恢复前后都评分。
- 主矩阵中 LongLLMLingua 恢复改变回答的比例为 2x 9%、4x 12%；LLMLingua 关闭恢复（0%）。
- 本 smoke 上恢复前后 EM 完全相同（平均 0.940/0.880），说明 20 题规模下恢复没有可见收益，
  但也未带来损失；需要主实验更大样本判断。
- 离线重放一致：验收脚本对 10 条已存回答重新执行 Algorithm 1，恢复文本与
  `matched_spans`/`matched_response_tokens`/`changed` 全部一致。

## 6. 离线验收（`scripts/accept_stage2.py`）

通过 400 槽完整验收，7 项检查全过（`reports/smoke-stage2-acceptance.json`）：

1. run 元数据可复现（配置哈希、实现哈希、上游提交、压缩模型元数据）；
2. 矩阵完整 400 槽，方法 × 位置单元格齐全；
3. `summary.json` 可由 `results.jsonl` 离线重建且完全一致；
4. 恢复在 10 条已存样本上离线重放一致；
5. 硬预算满足率 99.0%，4 条超标已登记；
6. 问题感知排名在 100/100 样本改变保留文档；
7. 每条槽位的提示哈希、完整提示 token、目标预算、实际比值、评分、缓存条目均可独立核对。

无 gold 泄漏：压缩与问答入口只接收 `visible_sample`（问题、标题、正文、普通文档 ID）；
`answers` 只在评分阶段使用；trace 与 `run.json` 不含评估字段。

## 7. 已知差异与局限

- 论文压缩模型 LLaMA-2-7B-Chat、问答模型 GPT-3.5-Turbo-0613；本项目用镜像权重 + deepseek-flash，
  属方法级复现，分数不能与论文数值直接比较。
- `restrict` 在固定提交里写死在文档级 ranker 内、不进入最终问答提示；本项目开关化后语义一致。
- `τ_ins=0.85`、`τ_que=0.9` 在固定提交 `compress_prompt` 路径未暴露，如实登记未实现；
  `k=2` 用 `context_level_target_token=2×target_tokens` 近似（见参数映射表）。
- 恢复分词器按用户决定改用 DeepSeek 分词器（论文用 LLaMA-2 tokenizer）。
- 单卡 910B4、单进程；压缩耗时含硬预算重试，不等于论文效率表口径（阶段四单独测）。
- 4x 深度压缩出现 13 组跨位置提示完全相同（27 槽中 14 槽复用同一缓存回答）：这些槽位压缩后
  保留 6 篇文档且 gold 文档不在其中；由于数据构造中只有 gold 文档换位、其余 19 篇相对顺序不变，
  保留集合相同时渲染出的提示逐字节相同，位置差异因此被压缩抹平。第三阶段解读位置曲线时应按
  `prompt_hash` 识别这些退化槽位，不能把它们当作独立的位置敏感样本。
- 4 条轻微超标槽位来自 `longllmlingua_4x` 的极端预算；阶段三可评估改进（向库显式传
  context 目标 token，减少重试）后再冻结正式配置。

## 8. 复现命令（在装有压缩模型的主机上）

```bash
PYTHONPATH=. python -m reproduction.stage2 plan
PYTHONPATH=. python -m reproduction.stage2 run
PYTHONPATH=. python -m reproduction.stage2 summarize outputs/stage2/<run_id>
PYTHONPATH=. python -m reproduction.stage2 casebook outputs/stage2/<run_id>
PYTHONPATH=. python scripts/accept_stage2.py outputs/stage2/<run_id>
PYTHONPATH=. python scripts/npu_switch_probe.py --out data/scratch/npu/switch_probe.json
```

轻量产物：`summary.md`、`summary.json`、`casebook.md`、`run.json`、`accepted-sample.jsonl`。
完整逐样本记录（约 8.6MB）留在运行机器 `outputs/stage2/<run_id>/results.jsonl`，
按仓库约定不入库；可由缓存与配置重建。
