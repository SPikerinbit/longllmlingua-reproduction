# 第二阶段：论文参数与固定官方版本的逐项对照

对照对象是本地 `arXiv-2310.06839v2` 与固定提交 `5a4c78ae18ab17a98cf997e8259354e546081d64`
（`vendor/llmlingua_reference/`）。表里只记录**核验过的事实**：论文写了什么、该提交是否暴露对应
参数、我们实际怎么设置、以及差异对结论的影响。未暴露的参数不拿默认值冒充等价。

| 论文设置 | 论文位置 | 固定提交是否暴露 | 本项目设置 | 差异与影响 |
| --- | --- | --- | --- | --- |
| 压缩模型 LLaMA-2-7B-Chat | §4 实验设置 | 暴露：`PromptCompressor(model_name=..., model_config=...)`；默认名 `NousResearch/Llama-2-7b-hf`（base，不是 chat） | `/cache/models/llama-2-7b-chat`（`NousResearch/Llama-2-7b-chat-hf` 权重，`meta-llama` gated 库的无门槛镜像） | 与论文同为 7B chat 权重；镜像仓库需在交接中说明来源与 revision。LLMLingua 与 LongLLMLingua 共用同一权重 |
| 迭代段长 200 | 附录 | 暴露：`iterative_size=200` 即默认值 | `compressor.iterative_size=200` | 一致 |
| 粗细粒度控制系数 k=2 | 附录 | **未暴露**：`compress_prompt` 无 k 参数；适配层传入 `context_level_target_token`，但固定版本的 LongLLMLingua `control_context_budget` 路径未使用它 | 历史代码仍传入 `context_level_target_token = 2 × target_token`，未改写既有运行 | 后续源码核验确认该近似映射在当前 LongLLMLingua 路径无效，不能称为近似等价或作为 k 消融；粗粒度筛选仍运行，但未严格复现论文 k=2 设置 |
| 指令预定义压缩 τ_ins=0.85 | 附录 | **未暴露**：该提交 `compress_prompt` 路径不压缩 instruction，最终提示原样拼回；旧版 budget controller 才有此类参数 | 不设置；instruction 走问答模板、不压缩 | 未实现，登记为差异；会让压缩后提示略长于论文 |
| 问题预定义压缩 τ_que=0.9 | 附录 | **未暴露**：同上，question 原样拼回（`concate_question=False` 时不进待压缩上下文） | 不设置；question 不压缩 | 未实现，登记为差异 |
| restrict 提示 `We can get the answer to this question in the given documents.` | §3.2 | **半暴露**：不是参数；硬编码在 `get_distance_longllmlingua` 内，只追加到文档级 condition perplexity 的 question，**不进入最终给问答模型的提示** | 默认打开（与官方行为一致）；`restrict` 开关关闭时，适配器在 `get_condition_ppl` 中精确剥离该后缀 | 语义与论文 r_k 的 `x^que,restrict` 一致；开关是我们自实现的（官方不可配置），用于阶段四 restrict 消融 |
| 问题感知粗粒度评分 r_k | §3.2 | 暴露：`rank_method="longllmlingua"` 走 `get_distance_longllmlingua`（condition perplexity，升序） | 主矩阵 `rank_method="longllmlingua"` | 一致；逐文档分数写入 trace |
| 问题感知细粒度对比困惑度 | §3.2 | 暴露：`condition_compare=True`（token 级条件对比） | 主矩阵 `True` | 一致 |
| 文档重排序 | §3.2 | 暴露：`reorder_context="sort"` | 主矩阵 `"original"`（关闭），重排序另设实验 | 按 AGENTS §3：五位置主实验关闭重排序，避免与位置偏置混淆；阶段四单独做 |
| 动态预算 δτ=0.3 | 附录 | 暴露：`dynamic_context_compression_ratio=0.3` | 0.3 | 参数一致；需注意库实现是按排名给每篇文档线性分配比率，论文 δτ 描述的是整体预算控制，语义不完全相同，报告中说明 |
| 2x / 4x 压缩率 | AGENTS §3 | 只暴露软参数 `rate` / `target_token`（库内用 tiktoken 计数的比例，上下文另加 `context_budget="+100"` 余量） | 硬预算模式：外层按"阶段一完整提示 token / 目标比值"取整，用 DeepSeek 分词器实测整条提示，未达标则收紧 rate 重压（最多 `max_budget_passes`）；同时保留第一轮自然结果 | 主表与 BM25 同口径（硬 ≤ 预算），可公平比较；自然结果留档说明库的软目标行为 |
| 压缩率/预算计数分词器 | §3.1（论文目标 LLM 为 GPT-3.5） | 硬编码 `tiktoken.encoding_for_model("gpt-3.5-turbo")` | 注入官方 DeepSeek 分词器（`TokenCounterAdapter`） | 差异：论文按目标 LLM 计数，本项目按固定问答模型计（AGENTS §3 要求单一计数口径）；同一提示换分词器会有几个 token 的波动 |
| 子序列恢复的分词器 | §3.3 / 图注 | 论文用 LLaMA-2 tokenizer；库 `recover()` 按 LLaMA 词切分 | 用 DeepSeek 分词器（回答、原提示、压缩提示同一切分） | 用户已确认的差异：恢复粒度与论文略有不同；不引入提示外信息，恢复前后回答都保存并都评分 |
| 恢复作用位置 | §3.3 Algorithm 1 | 库 `recover()` 在问答后作用于回答 | 问答后执行；`answer_before_recovery` 与 `answer_after_recovery` 均入库 | 一致 |
| 问答模型 | §4 | 论文 GPT-3.5-Turbo-0613 / 16k | `deepseek-flash`（非思考、temperature=0、max_tokens=512） | 阶段一已登记的替代；属于方法级复现 |
| 生成参数 | §4 | greedy / temperature=0 | temperature=0，max_tokens=512 | 一致（API 无 greedy 开关，temperature=0 即等价意图） |
| 预算执行区间 | §3.2 | 软目标 + `context_budget="+100"` | 主表硬预算（含 `context_budget="+100"` 作为库内部余量） | 硬预算可能比论文压缩得更多；自然结果用于说明未强制执行时的偏差 |
| 训练/推理硬件 | §4 V100-32G、PyTorch 1.13.1 | — | Ascend 910B4（32GB HBM）、CANN 8.5.2、torch 2.7.1 + torch_npu 2.7.1.post2、transformers 4.53.1 | 推理框架不同；fp16 前向数值可能与 V100 略有差异，不影响方法级结论 |

## 开关清单（阶段四消融直接使用）

| 开关 | config 位置 | 关闭时行为 | 行为证据 |
| --- | --- | --- | --- |
| 问题感知粗粒度（文档筛选） | `methods.*.rank_method = "llmlingua"`（或阶段四用 bm25 序） | 文档按非问题条件困惑度排序 | trace 的 `document_scores` 与 `used_doc_ids` 改变 |
| restrict 提示 | `methods.*.restrict = false` | 文档级 condition perplexity 去掉 restrict 后缀 | trace `restrict_enabled=false`，同一样本排序分数改变 |
| 问题感知细粒度 | `methods.*.condition_compare = false` | token 级打分不减去问题条件项 | 压缩文本与压缩率改变 |
| 动态预算 | `methods.*.dynamic_context_compression_ratio = 0.0` | 不启用按排名的逐文档比率偏移 | trace `dynamic_ratios` 为空；开启时为 `±δτ` 偏移量列表（负值保留更多），长度等于保留文档数 |
| 子序列恢复 | `methods.*.recovery = false` | 回答不做后处理 | 行内 `recovery_stats.changed=false`，`answer_after_recovery == answer_before_recovery` |
| 重排序 | `methods.*.reorder_context = "sort"` 开；`"original"` 关 | 主矩阵关闭 | trace `used_doc_indices` 保持原顺序与置乱顺序对比 |

`k=2`、`τ_ins`、`τ_que` 不是有效开关，不用于消融；分别属于当前路径无效映射或未实现。表中硬件行记录成员二历史环境；成员三/四的实际环境和课程范围见[实验说明](experiments.md)。
