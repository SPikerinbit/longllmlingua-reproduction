# 报告初稿：成员一负责的节

目标排版是 A4、单栏、正文 11–12 磅。下面四节对应分工表的第 1、2、3、8 节。第 4–7 节留白给成员二、三、四。数字与 `docs/presentation/01-number-registry.md` 一致。

## 1 原文定位与复现类型

本组复现 Jiang 等人 LongLLMLingua（arXiv:2310.06839v2）在长上下文问答里的问题感知提示压缩，任务数据用 Liu 等人 Lost in the Middle 发布的 Natural Questions 20 文档设置。官方压缩代码锁定 microsoft/LLMLingua 提交 `5a4c78ae18ab17a98cf997e8259354e546081d64`，数据与模板锁定 lost-in-the-middle 提交 `29b8a6d042ce29abccee3db1a73171a107d7e6af`，见 `manifests/resources.json`。

复现类型是缩规模的方法级复现，不是论文数值复现。论文问答模型是 GPT-3.5-Turbo-0613。本组从阶段一起换成 deepseek-flash，temperature 为 0，最大输出 512 token，见 `configs/stage1.json`。因此后文的 EM 只在本组这套问答接口里比较，不和论文表格里的 GPT 历史分数横比。

课程范围在实验开始前已经固定为 pilot 100 题乘五个答案位置。`manifests/main.json` 里的 500 题是嵌套清单的扩展，不在本轮结果里。

## 2 任务、数据与划分

每题 20 篇检索文档，其中一篇是 Natural Questions 的 gold 段落。上游只提供 gold 位于索引 0、4、9、14、19 的五个文件，本组把它们记成位置 1、5、10、15、20。五个文件的字节数和 sha256 在 `manifests/resources.json`。取得方式是 `python -m reproduction prepare`，该命令下载数据和分词器，不下载压缩模型，不调用问答 API。

全库 2,655 题。问题 ID 不是行号，而是 NFKC、casefold 和空白归一化之后的问题与答案集合的 SHA-256，实现在 `reproduction/data.py`。固定 seed 42 打乱后取嵌套前缀：`manifests/smoke.json` 20 题，`pilot.json` 100 题，`main.json` 500 题。已核对 smoke 等于 pilot 的前 20 个 ID，pilot 等于 main 的前 100 个 ID。同一题在五个位置上的文档集合保持一致，变的是 gold 文档放在哪一篇。

提示模板是上游 `vendor/lost_in_the_middle/qa.prompt`：要求只用给定检索结果写答案。方法看得见的字段只有问题、文档 ID、标题和正文。答案、gold 标记和位置编号不进入 BM25、压缩或问答请求，见 `docs/stage1-implementation.md`。

## 3 基线、预算与评价指标

阶段一基线有三条：不压缩的原始提示，以及 BM25 的 2 倍和 4 倍硬预算。BM25 使用 rank-bm25 0.2.2 的 BM25Okapi，k1=1.5，b=0.75，对标题和正文做 Unicode 词法 casefold。文档按相关度装入，最后一篇可以只留词前缀，输出时恢复原来的文档顺序。这是本组写死的工程选择。论文没有公开足够的 BM25 细节，所以这里不称为论文等价实现。

预算是完整提示 token 的下取整：`floor(原提示 token / 2 或 4)`。指令、问题和文档编号都算进去。计数用 DeepSeek-V4.1-Flash 分词器，revision `314113f8a7dadb388215396ba5fbee2c610a04d6`。它和 API 返回的模型别名不是同一个标识。300 个 smoke 槽的在线 prompt token 都比本地文本计数多 4，见 `reports/stage1-acceptance/REPORT.md`。

指标沿用上游首行 `best_subspan_em`。只把回答第一行送进评分函数：规范化后，任一参考答案作为子串出现则记 1。案例 M1-03 说明这个规则会把否定句里顺带提到的答案字符串记成正确，报告保留这个口径，不另换主指标。

阶段一验收 run `d54b3118c61ea4930624` 在 smoke 20 题上跑了 300/300 槽。original、BM25 2x、BM25 4x 的 EM 是 92.0%、87.0%、64.0%，实测压缩比 1.000x、2.001x、4.007x。这是流程验收的小样本。100 题主比较里的 original 是 84.6%（500 槽），两个分母不同，后文主表用 84.6%。

## 8 结论、局限与贡献

100 题主比较里，LongLLMLingua 2x 的 EM 是 83.2%，比原始提示 84.6% 低 1.4 个百分点，问题级配对 bootstrap 的 95% 区间是 [−6.2, 3.0]，跨过 0（`reports/stage3-main/stats.json`）。4x 是 79.0%，区间不跨 0。同一 100 题在 910B 上的完整方法是 82.6%，去掉粗粒度问题感知后是 45.0%。这两台机器的耗时不能相加。效率测量里，完整 2x 的端到端 p50 约 6.45 秒，原始提示约 1.12 秒，压缩没有带来更低的端到端延迟。

局限有四条，都已经写在参数映射或实验说明里：问答模型不是 GPT-3.5；k=2 在当前 LongLLMLingua 路径无效；指令和问题的预压缩没有实现；阶段三的硬件记录只到 `cuda:0`，没有可核验的 GPU 型号。首行子串 EM 还会把 M1-03 这种否定句记成对。

贡献按阶段分开，每人约四分之一，压缩算法本身来自上述微软提交，不是本组原创。成员一负责数据、模板、缓存、评分、原始提示和 BM25，验收见 `reports/stage1-acceptance/`。成员二、三、四的两句由本人贴到这里，成员一只保留他们写明的路径，不改写他们的 run_id。

成员二：（待本人写入：适配、开关、恢复、参数映射，以及 smoke 400/400。）

成员三：（待本人写入：pilot 3500/3500 与配对区间。）

成员四：（待本人写入：910B 消融 3500/3500、效率 1200/1200，以及恢复的 3 个负面槽。）
