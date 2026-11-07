# 第二阶段答辩材料：LongLLMLingua 如何保留与问题相关的信息

本文件是第二阶段（成员二）的答辩底稿：机制解释、论文—代码对应、复用与自主边界，
以及可直接引用的本阶段证据。运行数字见 [smoke 报告](../reports/stage2-smoke/REPORT.md)，
逐项参数对照见 [参数映射与差异表](stage2-parameter-map.md)。

## 1. 一句话结论

LongLLMLingua 在 LLMLingua 的 token 级信息量压缩之外，额外用"问题"当条件：
先按问题相关度给 20 篇文档重新打分（问题感知粗粒度），再在 token 级用"有问题条件"
与"无问题条件"的困惑度差挑词（问题感知细粒度），把省下的预算动态分配给高分文档，
最后在问答之后用压缩提示做子序列恢复。第二阶段把这套机制拆成独立开关接进统一入口，
并用 trace 证明每个开关确实改变了对应环节。

## 2. 四个机制与代码落点

| 机制 | 论文 | 官方固定提交中的实现 | 本项目的开关 |
| --- | --- | --- | --- |
| 问题感知粗粒度 | 文档级相关度 `r_k = -(1/N_c) Σ log p(x_que,restrict | x_doc_k)`，按 `r_k` 排序 | `get_distance_longllmlingua` → `get_condition_ppl(doc, question + " " + restrict, condition_in_question)` | `rank_method="longllmlingua"`、`condition_in_question="after"`、`restrict` 布尔 |
| 问题感知细粒度 | token 级对比困惑度 `s_i = ppl(x_i|x_<i) − ppl(x_i|x_que,x_<i)` | `condition_compare=True` 让 `iterative_compress_prompt` 同时算条件/无条件 loss 并取差 | `condition_compare` |
| 动态预算 | `τ_k = max(min((1−2I(r_k)/K')·δτ + τ, 1), 0)` | `dynamic_context_compression_ratio=δτ`，`control_context_budget` 生成每篇文档的 `dynamic_ratio` | `dynamic_context_compression_ratio` |
| 子序列恢复 | 问答之后：回答中出现的片段，若来自压缩提示，则回填原提示中对应的最短原片段 | 官方 `recover()` 按空格切词、用 LLaMA 分词器；不进入压缩链路 | `recovery`（本项目自实现 token 级 Algorithm 1） |
| 重排序 | 按 `r_k` 重排文档 | `reorder_context="sort"` | `reorder_context`（主实验关闭，按 AGENTS §3） |

两个容易忽略的实现事实：

1. **restrict 语句不进入最终问答提示**。官方把它写死在文档级 ranker 里（拼在 question 后面
   只用于算 `r_k`），最终 `compressed_prompt` 只由 instruction、压缩后的文档、question 组成。
   所以我们的 trace 里 `restrict_enabled` 只影响文档排名，不改送给问答模型的文本；
   论文里 restrict 的语义正是"给问题加一句条件句再算相关度"，两者一致。
2. **文档级排名来自困惑度**。`r_k` 越大（文档越能降低加了 restrict 的问题的困惑度）越相关；
   `condition_in_question="after"` 让问题作为条件出现在文档之前。压缩器输出的
   `document_scores` 就是这次排名的分数（取自 `get_rank_results` 的返回值）。

## 3. token 级压缩与预算

官方 `compress_prompt(context, instruction, question, rate)` 的 `target_token` 只约束 context；
完整提示 ≈ `rate × origin`。我们做三件事把它变成可比较的实验口径：

- 计数器换成固定 DeepSeek 分词器（官方用 `tiktoken gpt-3.5`，对应论文的 GPT-3.5 目标模型）；
- `rate = 1/ratio`，`target = floor(origin/ratio)`，其中 `origin` 是阶段一模板下
  "instruction + 20 篇文档 + question" 的完整提示 token 数，与 BM25 2x/4x 同一口径；
- `budget_mode="hard"`：外层最多重试 3 轮，每轮把 `rate` 按 `target/full × 0.98` 收紧，
  直到实测完整提示 ≤ 目标；每轮结果都进 trace，第一条自然结果永远保留。
  smoke 实测没有出现 3 轮仍未达标的槽位（见报告）。

## 4. 子序列恢复（本项目自实现）

论文 Algorithm 1 作用在**回答**上，输入原提示 `x`、压缩提示 `x̃`、回答 `y`：

1. 用分词器把 `y` 切成 token；
2. 对每个位置找在 `x̃` 中连续出现的最长 token 子串 `ỹ_key`；
3. 若找到，回到原提示 `x` 中找到按序包含 `ỹ_key` 的最短连续片段 `x_i,j`，用 `x_i,j` 替换；
4. 找不到则原样保留。

实现 `reproduction/recovery.py:recover_answer()` 用 DeepSeek 分词器统一切分回答、原提示、压缩提示
（论文用 LLaMA-2 tokenizer，差异已登记）；逐槽保存 `answer`、`answer_before_recovery`、
`answer_after_recovery`、`recovery_stats`，恢复前后都评分。恢复是纯离线后处理，
不重新调用 API，因此阶段四的恢复消融可直接复用同一批原始回答。

## 5. 复用与自主边界

**复用（固定提交 `5a4c78ae18ab17a98cf997e8259354e546081d64`）**：`PromptCompressor` 的压缩算法、
迭代式 token 过滤、文档级排名、动态预算、`control_context_budget` 与 `iterative_compress_prompt`。
代码经 `reproduction/llmlingua_pkg.py` 从 `vendor/llmlingua_reference/` 取出并保留来源与许可证说明。

**自主实现**：统一入口与配置、DeepSeek 分词器适配、NPU 设备与 transformers 4.53 `Cache` 兼容层、
restrict 语义的开关化、硬预算外层重试、token 级恢复、逐槽 trace、缓存分层（压缩缓存与问答缓存分离）、
词表与模板口径、验收脚本。

**不属于自主实现**：压缩算法的核心（困惑度打分、迭代过滤、动态预算公式）、restrict 语句的语义
（论文给定）、恢复算法（论文 Algorithm 1）。

## 6. 证据清单（可现场演示）

1. `python -m reproduction.stage2 casebook outputs/stage2/<run_id>`：逐题展示文档分数、保留/丢弃、
   动态比率、压缩前后文本与恢复前后回答。
2. `scripts/npu_switch_probe.py`：同一题在 6 个开关设置下的对比表（排序、保留文档、token 数、
   动态比率、文本预览），直接证明开关改变对应机制。
3. `scripts/accept_stage2.py`：离线验收——矩阵完整、预算算术、开关痕迹、无评估字段泄漏、
   恢复重放一致；第三阶段可直接消费 `results.jsonl`。
4. 参数映射差异表：论文设置逐项对照固定提交是否暴露，未暴露项（τ_ins/τ_que、k=2）如实登记。
