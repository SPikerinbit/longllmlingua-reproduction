# 第二阶段实现说明：压缩适配、机制开关与过程追踪

本文件写**已经实现并经本机/服务器实测**的接口与产物。论文参数逐项对照见
[参数映射与差异表](stage2-parameter-map.md)；阶段一接口见
[stage1-implementation.md](stage1-implementation.md)。

## 组件

| 文件 | 职责 |
| --- | --- |
| `reproduction/llmlingua_pkg.py` | 把 `vendor/llmlingua_reference/llmlingua/*.reference` 复制成可 import 的包（不修改官方文件内容），并生成最小的包 `__init__.py`（上游 `__init__` 依赖未 vendor 的 `version` 模块） |
| `reproduction/compression.py` | 压缩适配层：注入官方 DeepSeek 分词器、在 NPU 上加载 7B 权重、transformers Cache 兼容、restrict 开关、粗/细粒度过程追踪、硬预算重试 |
| `reproduction/recovery.py` | 子序列恢复（论文 Algorithm 1 的 token 级实现），问答之后作用于回答 |
| `reproduction/stage2.py` | 阶段二入口：`plan` / `run` / `summarize` / `casebook` |
| `configs/stage2.json` | 四种方法、压缩器、恢复与开关配置 |
| `tests/test_stage2.py` | 配置契约、预算重试、恢复、汇总的离线测试（不加载模型、不调 API） |

不修改官方 `prompt_compressor.py` 的逻辑；适配全部通过子类与注入完成，差异与原因写入参数表。

## 接口契约

```python
from reproduction import compression, recovery, methods

counter = methods.TokenCounter()
compressor, meta = compression.load_compressor(config, counter)
result = compression.compress_sample(compressor, config, "longllmlingua_2x", visible_sample, counter)
# result: prompt / origin_tokens / compressed_tokens / actual_ratio / target_tokens /
#         budget_satisfied / selected_doc_ids / ranking / compression_seconds / trace
answer = llm(prompt)                      # 阶段一的问答缓存与评分流程
recovered, stats = recovery.recover_answer(result["prompt"].replace(...), result["prompt"], answer, counter)
```

`compress_sample` 只接收 `visible_sample`（问题与文档），不接触答案、gold 或位置标签；
位置构造在阶段一的 `data.iter_samples` 中完成。

## 配置（`configs/stage2.json`）

- `compressor`：压缩模型路径/镜像名、`device`（如 `npu:0` 或 `cpu`）、`torch_dtype`、
  `attn_implementation`、`iterative_size=200`、`context_budget="+100"`、
  `budget_mode`（`hard`/`natural`）、`max_budget_passes`。
- `methods.<name>`：`kind`（llmlingua/longllmlingua）、`ratio`（2x/4x）、
  `rank_method`、`condition_in_question`、`condition_compare`、
  `dynamic_context_compression_ratio`、`reorder_context`、`restrict`、`recovery`。
- 主矩阵：`llmlingua_2x|4x`（无问题感知、无恢复）与 `longllmlingua_2x|4x`
  （问题感知粗粒度+restrict、细粒度对比、动态预算 0.3、恢复开启）；
  两种方法共用同一压缩模型；`reorder_context="original"`（按 AGENTS §3 关闭重排序）。
- 配置校验：阶段号、DeepSeek 端点、非思考、temperature=0、方法集合、比值 > 1、
  固定上游提交 `5a4c78ae…`、布尔开关类型等，违反即拒绝运行。

## 运行（Linux 服务器 / NPU 容器）

```bash
# 离线：只统计预算并检查资源校验值，不加载模型、不调 API
PYTHONPATH=. python -m reproduction.stage2 plan

# 真实运行：先限量 3 个新逻辑请求确认链路，再续跑整个矩阵
PYTHONPATH=. python -m reproduction.stage2 run --limit 3
PYTHONPATH=. python -m reproduction.stage2 run

# 离线重评分与案例导出（不调 API、不重跑压缩器）
PYTHONPATH=. python -m reproduction.stage2 summarize outputs/stage2/<运行ID>
PYTHONPATH=. python -m reproduction.stage2 casebook outputs/stage2/<运行ID>
```

同一运行目录不要并发跑两个进程；中断后会留下 `.running` 标记，确认无旧进程后删除再续跑。
压缩结果缓存于 `cache/compress2/<key>.json`，问答缓存于 `cache/api/<key>.json`；
两者独立，改恢复配置或改问答参数不会重复加载 7B 模型或重复计费。

## 逐槽位结果

`outputs/stage2/<运行ID>/results.jsonl` 每行至少包含：

- 标识与状态：`slot_id`（`问题ID:位置:方法`）、`question_id`、`position`、`split`、`method`、`status`、`error`；
- 提示与预算：`prompt`、`prompt_hash`、`prompt_tokens`、`origin_prompt_tokens`、
  `target_tokens`、`target_ratio`、`actual_ratio`、`budget_satisfied`；
- 机制追踪 `trace`：`document_scores`（逐文档条件分数与是否保留）、`used_doc_ids`、
  `dropped_doc_ids`、`dynamic_ratios`、`attempts`（每轮 rate 与新 token 数）、
  `compressed_context_tokens/chars/compressed_context_preview`、`restrict_enabled`、
  库自报 origin/compressed/ratio。`dynamic_ratios` 是每篇保留文档在基准 rate 上的偏移量
  （`±δτ`，可为负，负值表示保留更多），不是绝对压缩率；开关关闭时为空列表。
- 问答与恢复：`answer`、`answer_before_recovery`、`answer_after_recovery`、
  `recovery_enabled`、`recovery_stats`（匹配 span 数、token 数、是否改变）；
- 评分：`score`（主口径）、`score_before_recovery`、`score_after_recovery`；
- 计费与可复现：`usage`、`response_model`、`system_fingerprint`、`response_id`、
  `finish_reason`、`cache_key`、`cache_hit`、`config_hash`、`implementation_hash`、
  `method_version`、`compressor` 元数据（在 `run.json`）。

`run.json` 记录配置、实现哈希、问题 ID 列表、压缩模型加载信息与上游提交；
`summary.json` / `summary.md` 可从 `results.jsonl` 独立重建；`casebook.md` 给出每种方法
每个位置的追踪样例（文档分数、保留情况、压缩预览、恢复前后回答与分数）。

## 计数与预算口径

- 完整提示的 token 一律用阶段一固定的官方 DeepSeek 分词器计数；API 返回的 usage 另行记录。
- 2x/4x 指"原始完整提示 token / 压缩后完整提示 token"。主表使用硬预算：外层按实测 token
  收紧库的 `rate` 重压，首轮自然结果保存在 `trace.attempts[0]` 供差异说明。
- 压缩器内部计数已被替换为同一分词器（官方默认用 tiktoken/gpt-3.5 计数）。

## 环境

`requirements-stage2.txt` 记录服务器实测版本（torch 2.7.1 + torch_npu、transformers 4.53.1、
accelerate、tiktoken、nltk、sentencepiece 等）。模型权重不入库，路径由 `compressor.model_path`
指定；本地 CPU 仅运行离线测试与 `plan`，不需要 GPU 栈（torch 相关 import 延迟到加载压缩器时）。

## 已知实现差异（摘要）

1. `k=2` 用 `context_level_target_token=2×target_token` 近似（官方签名无 k）。
2. `τ_ins=0.85`、`τ_que=0.9` 在固定提交未暴露，instruction/question 不预压缩，登记为未实现。
3. restrict 语句在官方代码中是文档级 ranker 内写死的字符串；我们用子类开关控制（关闭时精确剥离）。
4. 子序列恢复使用 DeepSeek 分词器，而论文用 LLaMA-2 tokenizer（用户确认的差异）。
5. transformers ≥4.46 的 `Cache` 对象与固定版本代码的 legacy KV 格式不兼容，适配器在
   `get_ppl` 边界双向转换，未修改官方文件。
6. 主表硬预算与库的软目标不同；自然结果留档，报告分别说明。
