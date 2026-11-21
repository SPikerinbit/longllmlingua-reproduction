# 第一阶段接口、方法与验证说明

## 数据和接口

`reproduction/data.py` 下载固定上游数据，按 Git blob SHA-1 核对 GitHub 数据、模板与评估源码；为每个资源保存 SHA-256。prepare 验证全部 2,655 题 × 五位置的问题集合、文档集合和 gold 位置，随后将稳定 ID 排序、seed=42 打乱，取嵌套前 20/100/500 题。

问题 ID 来自 NFKC/casefold/空白归一化后的问题和答案集合摘要，不依赖文件行号。部分 gold 文档无 id，以标题与正文摘要补齐，不能使用 gold 标记生成身份。

第二阶段接手的最小接口：

```python
visible = visible_sample(upstream_row)
# {question: str, documents: [{id: str, title: str, text: str}]}
built = build_prompt(visible, method, config, counter)
# {prompt, origin_tokens, compressed_tokens, target_ratio,
#  target_tokens, actual_ratio, selected_doc_ids, ...}
```

runner.slots 在方法外附加问题 ID、位置与 answers；这些评估字段不能传给方法。问答请求只包含完整上游提示及模型生成设置。不得把位置编号写入提示。

成员二在配置验证、methods.build_prompt 及元数据中新增压缩适配，保留相同原始提示和评分。恢复在问答之后执行；当前记录 recovery_enabled=false，恢复前后回答相同，不表示已实现恢复。

## 方法与预算

原始提示直接使用上游 qa.prompt，文档格式为 `Document [i](Title: title) text`，不附加自定义系统消息。

BM25 使用 rank-bm25 0.2.2 的 BM25Okapi，k1=1.5、b=0.75；Unicode `\w+` 分词并 casefold，对标题和正文一起评分。同分按稳定文档 ID 排序。按相关性装入文档，最后一篇可截取词前缀，最终输出恢复原文档顺序。

2x/4x 预算为 `floor(原完整提示 token / 2或4)`，标题、编号、指令和问题均计入。每次评估完整提示，最后断言预算。固定部分放不下或无法保留非空文档时显式报错，不发送不合规提示。这是小组固定的基线策略，与论文未完全公开的 BM25 细节可能有差异。

使用官方公开 DeepSeek-V4.1-Flash 固定分词器，仅作文本预算；其 revision 与 API 模型版本不是同一标识，不能保证计费完全一致，在线 usage 单独保存并待真实调用核验。

## 问答、缓存和结果

- api.request_payload 构造官方 Chat Completions 请求：非思考、temperature=0、max_tokens=512。最初的 128 上限导致少量回答截断，旧轮次保留，正式验收使用统一 512 设置。
- api.cache_key 覆盖地址、完整消息、模型、预期版本和生成设置，不包含密钥。
- 缓存仅保存成功、非空、finish_reason=stop 的响应及 usage、model、fingerprint、时间与原配置摘要。
- 发生空回答或截断时，新版失败日志保存返回的 usage、部分回答、finish_reason 和模型信息以核算消耗，但不将它作为成功缓存或得分。
- runner 按配置、代码/模板摘要及数据清单派生运行 ID，追加结果，以单进程标记避免并发重复运行。
- 逐样本结果保留提示、回答、目标/实测预算、方法元数据、压缩/问答/恢复耗时、cache_hit、usage、版本、状态与评分所需答案。
- cache_hit 时 api_seconds 是原生成耗时，observed_seconds 是本次读取耗时，不能用读取耗时冒充推理加速。
- evaluation.summarize 从回答重新调用上游评分，按方法与位置汇总最新槽位结果；缺失/失败明确列出。

## 验证边界

离线测试覆盖真实数据对齐、评分边界、预算与文档顺序、输入字段隔离、请求格式、429 重试、鉴权/余额错误、失败不缓存、缓存失效、断点续跑和结果日志丢失后的缓存重建。模拟 API 数据仅在测试临时目录，不混入真实缓存。

已完成真实 API 鉴权、返回模型别名/fingerprint 与 usage 记录、300 槽位问答和离线重评分；本轮在线输入计数统一比本地文本计数多 4 token。费用按已记录 usage 与官方价格估算，平台账单才是实际扣费凭证。具体快照名称无法仅由返回别名单独证明。

本节描述阶段一的CPU/API实现边界，验收报告保留在reports/stage1-acceptance/。后续压缩模型加载、云端运行与各阶段离线核查已另行完成，当前整体进度和实际环境见[实验说明](experiments.md)，不将不同阶段环境混为一次实验。
