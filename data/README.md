# 数据说明

提交包只放这份说明。五个 jsonl.gz、分词器大文件和完整预测不放进 zip。

## 来源

问答数据、提示模板和 `best_subspan_em` 来自 nelson-liu/lost-in-the-middle 提交 `29b8a6d042ce29abccee3db1a73171a107d7e6af`。上游 README 写明：20 文档文件由 Natural Questions 的 gold 段落和 Contriever 检索结果构成，gold 索引为 0、4、9、14、19。本组把这五个索引记成答案位置 1、5、10、15、20。

固定文件在 `manifests/resources.json`：

| 文件 | 字节 | sha256 |
| --- | ---: | --- |
| `nq-open-20_total_documents_gold_at_0.jsonl.gz` | 15151873 | `69a8dd87a45f07fb3ed9b804917a89db975cd6e488682fc838edca029cc3881f` |
| `nq-open-20_total_documents_gold_at_4.jsonl.gz` | 15163003 | `c5e44700c4db24536f139f7383e3dd002413515ee889aeadc72767dd7f289682` |
| `nq-open-20_total_documents_gold_at_9.jsonl.gz` | 15155756 | `cbada411f70235afc47d9b5407e9358ad72eb021742402ff032c8b65076ffb2f` |
| `nq-open-20_total_documents_gold_at_14.jsonl.gz` | 15152418 | `86c1a25093615baefdd1ee4db7a993548b3bef24ca02eb9bd8db43fbedf517f2` |
| `nq-open-20_total_documents_gold_at_19.jsonl.gz` | 15114700 | `d79b715e1b8c8301335e93cb01659f68c24f0253a808c3190b06d21896506c6c` |

URL 形如 `https://raw.githubusercontent.com/nelson-liu/lost-in-the-middle/29b8a6d042ce29abccee3db1a73171a107d7e6af/qa_data/20_total_documents/<文件名>`。

模板和评分也锁定在同一提交，并已放在 `vendor/lost_in_the_middle/`：`qa.prompt`、`metrics.py`、`prompting.py.reference`、`evaluate_qa_responses.py.reference`。它们的 sha256 同样在 `resources.json`。

DeepSeek 分词器是 `deepseek-ai/DeepSeek-V4.1-Flash` revision `314113f8a7dadb388215396ba5fbee2c610a04d6` 的 `tokenizer.json`，sha256 `c90dfa01249db1be4245780a052ede752e1361c612ac6d08e2bdada7d599476b`。它只用于本地预算计数，不是问答模型权重。

## 许可

`vendor/lost_in_the_middle/LICENSE` 是 MIT，版权人 Nelson Liu，2023。`vendor/llmlingua_reference/LICENSE` 是 MIT，版权人 Microsoft Corporation。`vendor/deepseek_tokenizer/LICENSE` 是 MIT，版权人 DeepSeek，2023。

上游该提交的 README 没有单独附上 Natural Questions 数据的许可证文件。本说明不填写仓库里没有出现的许可证名称。打包前由成员一打开 Google Research 的 Natural Questions 发布页，把那一句许可补进行文；补上之前，zip 里不要再分发那五个 gz。

## 取得方式

在仓库根目录执行：

```bash
python -m reproduction prepare
```

这条命令按 `reproduction/data.py` 下载上述文件并用 git blob SHA-1 核对，不调用问答 API，不下载 LLaMA 权重。下载完成后，五个 gz 的 sha256 应与上表一致。

2026-11-21 17:46:00–17:46:07（Asia/Shanghai）已在提交 `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4`、Python 3.13.5、`tokenizers==0.22.1` 的本机环境执行该命令，退出码 0。五个 gz 与 `tokenizer.json` 的 sha256 均与上表及 `manifests/resources.json` 一致，见 `reports/local-verification/data-tokenizer-sha256.txt`。这些二进制文件仍不入库、不进课程 zip。已提交清单里 DeepSeek LICENSE 记录的是 CRLF（1084 字节）摘要；本机检出为 LF（1064 字节），`verify_resources` 按设计接受这种换行等价。

## 固定划分和样本 ID

`prepare` 检查 2,655 题在五个位置上的问题集合、文档集合和 gold 位置，然后按问题 ID 排序，用 `random.Random(42)` 打乱，取嵌套前缀。

| 清单 | 题数 | 文件 |
| --- | ---: | --- |
| smoke | 20 | `manifests/smoke.json` |
| pilot | 100 | `manifests/pilot.json` |
| main | 500 | `manifests/main.json` |

2026-11-21 已在本仓库核对：三个清单的 ID 都唯一，smoke 是 pilot 的前 20 个，pilot 是 main 的前 100 个。课程主比较和消融用 pilot。smoke 用于阶段一基线、阶段二压缩验收和阶段四效率。main 只保留清单，不表示已经跑完 500 题。

阶段一验收的 20 题就是 `smoke.json` 里的这 20 个 ID。案例 M1-01 的 ID `ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc` 是其中第一个。

## 不进入方法的字段

每行 json 含 `question`、`answers`、`ctxs`。`ctxs` 里有 `hasanswer` 和 `isgold`。这些标记只用于检查 gold 是否在指定位置，以及评分。`reproduction/data.py` 的可见样本只保留问题、文档 ID、标题和正文。没有上游 id 的 gold 文档用标题和正文的摘要当 ID，不用 gold 标记来生成身份。

## 本包不包含的数据

`data/raw/*.jsonl.gz`、`data/tokenizer/tokenizer.json`、`outputs/` 和 `cache/` 留在组内。取得原始返回包之后，重评分命令见 `docs/experiments.md`，不要把那份包打进课程 zip。
