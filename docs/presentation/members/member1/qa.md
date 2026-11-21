# 成员一 QA 卡

十题。15 秒答案按口播写，依据都在仓库或本次用锁定 sha256 对齐过的上游文件里。

## Q1 为什么只做五个位置？

15 秒：上游 20 文档数据只发布了 gold 在索引 0、4、9、14、19 的五个文件，对应位置 1、5、10、15、20。`manifests/resources.json` 里只有这五个 gz。

不能说：我们抽过其他位置但没跑。

## Q2 问题 ID 为什么不用行号？

15 秒：`reproduction/data.py` 的 `question_id` 是归一化问题和答案集合的 SHA-256。五个文件的行号不一定指同一题。smoke 的 20 个 ID 是 pilot 的前 20 个，pilot 是 main 清单的前 100 个，都在 `manifests/`。

不能说：ID 是题号或 Wikipedia id。

## Q3 best_subspan_em 怎么算？

15 秒：`evaluation.py` 只取回答第一行，再调用 `vendor/lost_in_the_middle/metrics.py`。规范化后，任一参考答案作为子串出现就记 1，否则 0。M1-03 里 BM25 的否定句因为含有 Los Lonely Boys 而被记成 1。

不能说：它等于完全匹配或人工判断。

## Q4 BM25 的参数是什么？和论文一样吗？

15 秒：`configs/stage1.json` 写 k1=1.5、b=0.75，分词是 `unicode-word-lower-v1`。`docs/stage1-implementation.md` 写明这是小组固定的工程选择，论文没有把 BM25 细节完全公开，所以不说成论文等价实现。

不能说：这就是论文附录里的 BM25。

## Q5 为什么用 DeepSeek 不用 GPT-3.5？

15 秒：阶段一验收报告写明用现有 DeepSeek 代替历史 GPT-3.5。配置是 deepseek-flash、temperature 0、max_tokens 512。返回的 fingerprint 不能证明模型快照。分数因此不能和论文的 GPT 历史数字比较。

不能说：deepseek-flash 等于 GPT-3.5-Turbo-0613。

## Q6 为什么是 100 题不是 500 题？

15 秒：`docs/experiments.md` 和根目录 README 写的课程范围是已经固定的 pilot 100 题乘五个位置。500 题清单留在 `manifests/main.json`，不作本轮验收。没有按分数重新抽样。

不能说：500 题已经跑完，只是没放进仓库。

## Q7 缓存怎么保证可复现？

15 秒：`docs/stage1-implementation.md` 写 cache key 覆盖地址、完整消息、模型、预期版本和生成设置，不含密钥。只有非空且 `finish_reason=stop` 的成功响应才进成功缓存。失败不进。续跑按运行 ID 追加，同一目录不要开两个进程。

不能说：缓存命中的读取时间就是模型变快了。`api_seconds` 在命中时仍是原来的生成耗时。

## Q8 smoke 的 92% 和主比较的 84.6% 为什么不同？

15 秒：92.0% 是 20 题、100 槽的 original，见 `acceptance.json`。84.6% 是 100 题、500 槽的 original，见 `reports/stage3-main/summary.json`。样本量和后续实验都不同，P2 上已经分开写了。

不能说：模型退步了 7.4 个百分点。这两个数的分母不一样。

## Q9 答案会不会漏进提示？

15 秒：`docs/stage1-implementation.md` 写 `visible_sample` 只有问题、标题、正文和普通文档 ID。`answers`、gold 和位置由 runner 加在方法外面，不传给 BM25 或问答。问答用的是 `vendor/lost_in_the_middle/qa.prompt`，没有自定义系统消息。

不能说：我检查过每一条完整提示，因为完整提示在组内运行目录，不在当前仓库。能说的是代码路径和验收报告里“无 gold 泄漏”的设计，完整逐条重放要等组内 `results.jsonl`。

## Q10 在线 token 为什么比本地多 4？

15 秒：`reports/stage1-acceptance/REPORT.md` 写，300 槽的在线输入计数减本地文本计数，分布是 `{4: 300}`。配置里的计数说明是 prompt 文本，不含 API 的对话包装。计费以 usage 为准。

不能说：本地 token 就是账单。
