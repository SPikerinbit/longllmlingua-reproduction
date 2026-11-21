# 成员一的三条案例

这三条占 12 条案例里的 M1-01 到 M1-03。分数、token 和首行输出来自 `reports/stage1-acceptance/predictions.jsonl`。问题和参考答案不在这份 jsonl 里。它们来自与 `manifests/resources.json` 中 sha256 `69a8dd87a45f07fb3ed9b804917a89db975cd6e488682fc838edca029cc3881f` 一致的 `nq-open-20_total_documents_gold_at_0.jsonl.gz`，用 `reproduction/data.py` 的 `question_id` 对齐。20 个 smoke ID 全部对上，没有对不上的题。原始 gz 不入库。

评分函数是 `reproduction/evaluation.py`：只把回答第一行送进 `vendor/lost_in_the_middle/metrics.py` 的 `best_subspan_em`。三条的 `finish_reason` 都是 `stop`，fingerprint 都是 `bc19ba97cbe016479903222bb1578db6`。

## M1-01 四倍压缩把答案名称丢掉

- 问题 ID：`ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc`
- 位置：1
- 问题：who was the first coronated king of manipur at kangla
- 参考答案：Pakhangba；Pamheiba
- 来源槽：同 ID 加 `:1:original`、`:1:bm25_2x`、`:1:bm25_4x`

| 方法 | score | 原始 / 压缩 / 目标 token | 实测比 | API 输入 / 输出 | 时间（UTC） |
| --- | ---: | --- | ---: | --- | --- |
| original | 1.0 | 3289 / 3289 / 3289 | 1.0 | 3293 / 98 | 2026-11-06T10:10:59 |
| bm25_2x | 1.0 | 3289 / 1644 / 1644 | 2.0006082725060828 | 1648 / 119 | 2026-11-06T10:11:00 |
| bm25_4x | 0.0 | 3289 / 822 / 822 | 4.0012165450121655 | 826 / 90 | 2026-11-06T10:11:02 |

原始提示首行含 Pakhangba，score 为 1。BM25 2x 首行仍有 Pakhangba，score 为 1。BM25 4x 首行写“the specific name … is not explicitly stated”，后面出现的是 Pakhangpa，不是 Pakhangba 或 Pamheiba，所以 score 为 0。4 倍预算是 `floor(3289/4)=822`，实测刚好 822。这一条说明词法截断可以在满足预算的同时丢掉被评分的名称。它是 20 题里的 1 题，不能代替主比较里 BM25 4x 的 55.8%。

## M1-02 四倍仍然留住 Banquo

- 问题 ID：`0b6dde118f5c85bc3f4d120a9bd287bf2fbdda405bda05bf3d8587c10efc9be7`
- 位置：1
- 问题：character in macbeth who is murdered and appears as a ghost
- 参考答案：Lord Banquo；Banquo
- 来源槽：同 ID 加 `:1:original`、`:1:bm25_2x`、`:1:bm25_4x`

| 方法 | score | 原始 / 压缩 / 目标 token | 实测比 | API 输入 / 输出 |
| --- | ---: | --- | ---: | --- |
| original | 1.0 | 2898 / 2898 / 2898 | 1.0 | 2902 / 106 |
| bm25_2x | 1.0 | 2898 / 1449 / 1449 | 2.0 | 1453 / 98 |
| bm25_4x | 1.0 | 2898 / 724 / 724 | 4.002762430939226 | 728 / 74 |

三种方法的首行都写出 Banquo，且都在讲他被谋杀后以鬼魂出现。2x 的目标 token 是 1449，压缩后也是 1449，比值正好 2.0。4x 目标 724，压缩后 724。这一条说明 BM25 不是一律失败：同一套 k1=1.5、b=0.75 的实现，在这道题上把提示压到约 4 倍后仍保住了评分子串。

## M1-03 首行子串把否定句判成对

- 问题 ID：`64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5`
- 位置：10
- 问题：who sang the song how far is heaven
- 参考答案：Los Lonely Boys
- 来源槽：同 ID 加 `:10:original`、`:10:bm25_2x`、`:10:bm25_4x`

| 方法 | score | 原始 / 压缩 / 目标 token | 实测比 | 行数 | API 输入 / 输出 |
| --- | ---: | --- | ---: | ---: | --- |
| original | 0.0 | 2928 / 2928 / 2928 | 1.0 | 8 | 2932 / 200 |
| bm25_2x | 1.0 | 2928 / 1463 / 1464 | 2.001367053998633 | 1 | 1467 / 116 |
| bm25_4x | 1.0 | 2928 / 732 / 732 | 4.0 | 1 | 736 / 87 |

原始提示的第一行是：“Based on the provided search results, I cannot definitively answer who sang a song titled "How Far Is Heaven." None of the documents mention a song with that exact title.” 全文 8 行里也没有 Los Lonely Boys，score 为 0，和“模型拒绝回答”一致。

BM25 2x 的第一行在否认这个歌名的同时，提到了另一首歌 “Heaven” (by Los Lonely Boys and by Warrant)。规范化后的参考答案 `los lonely boys` 出现在这一行里，所以上游函数记 1.0。BM25 4x 同样在否定句里写出 “Heaven” by Los Lonely Boys，score 也是 1.0。这不是人工改分。`metrics.py` 只检查子串，不判断句子是不是在否定。阶段一沿用这个口径，主比较也沿用，所以报告里要说明 EM 会把这种提及算作对。

同一题在位置 5 上三种方法的 score 都是 0（predictions.jsonl）。位置一变，gold 文档的位置就变，BM25 保留下来的句子也会变。案例只把位置 10 这一组当作 M1-03。
