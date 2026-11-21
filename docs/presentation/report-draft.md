# LongLLMLingua 复现报告

正式报告是 `docs/presentation/report/report.pdf`，可编辑源是同目录 `report.docx`、`report.md`、`SOURCES.md`。正文 5 页，参考文献 1 页，13 条案例附录 5 页。本文件保留为更早的源稿索引，数字以正式报告和 `docs/presentation/01-number-registry.md` 为准。

P 编号和登记表上的四人信息待补。课程提交规范写的是四人信息与实际贡献，没有单独要求“法定姓名”。没有把未跑完的 Cursor 对话或不可用的压缩模型写成已完成实验。原有 DeepSeek 结果没有改。占位包 `NLP2026_G14_Pxx.zip` 还不能直接提交。

## 1 范围

复现对象是 LongLLMLingua（arXiv:2310.06839v2）。压缩代码锁定 microsoft/LLMLingua 提交 `5a4c78ae18ab17a98cf997e8259354e546081d64`。数据、模板和 `best_subspan_em` 锁定 lost-in-the-middle 提交 `29b8a6d042ce29abccee3db1a73171a107d7e6af`。

课程比较用已经固定的 pilot 100 题、每题 20 篇文档、答案位置 1/5/10/15/20。`manifests/smoke.json` 的 20 题是 `pilot.json` 的前 20 个，pilot 是 `main.json` 前 100 个。seed=42，总体 2655 题。500 题清单不是本轮结果。

问答的已完成运行使用 deepseek-flash、temperature 0、max_tokens 512。这是方法级复现。fingerprint 不能证明模型快照，分数不能写成论文里 GPT-3.5 的历史数字。k=2 在当前路径无效，指令和问题预压缩没有实现，见 `docs/stage2-parameter-map.md`。

## 2 数据与阶段一基线

可见输入只有问题和文档的 id、标题、正文。答案、gold 和位置不进入 BM25 或问答提示，见 `reproduction/data.py` 的 `visible_sample`。

2026-11-21 用 `scripts/audit_stage1_offline.py` 核对了五个公开 gz。sha256 与 `manifests/resources.json` 一致。20 个 smoke 题在五个位置上的文档集合一致，gold 只在指定位置，失败 0。审计耗时 2.055 秒，API 调用数为 0。输入 `predictions.jsonl` 的 sha256 是 `cac37c9e84678f2f591af8c4f6ccdb7a69d010cf71eae5678b85109bcb27bd62`。

阶段一 run `d54b3118c61ea4930624` 有 300/300 槽。重评分与已存 score 不一致 0 条。官方均值仍是 original 92.0%、BM25 2x 87.0%、BM25 4x 64.0%。300 槽都满足 `compressed_tokens <= target_tokens`，目标等于原始 token 整除 1、2 或 4。在线 prompt token 全部比本地文本多 4。完整提示和 cache 仍在组内目录，不在 git 里。

主指标只看回答第一行。把换行拼成空格后再用同一函数评分，有 2 槽会从 0 变成 1，都是同一题 original 的位置 5 和 20。另有 4 槽首行在否认歌名的同时带出 “Los Lonely Boys”，官方分数为 1。这两类是诊断，不替换 `best_subspan_em`。13 条槽写在 `reports/stage1-supplement/cases.md`。

## 3 压缩、主比较和消融

LLMLingua 与 LongLLMLingua 共用 LLaMA-2-7B-Chat，revision `351844e75ed0bcbbe3f10671b3c808d2b83894ee`。本环境没有这份权重，也没有 Ascend/CUDA。因此没有新的压缩、没有用对话模拟压缩后的文本。

已经完成并保留的记录是：

- 阶段二 smoke 的公开验收文件在 `main` 和四条推荐分支上是 run `outputs/stage2/a1bd26fe3d82dea3f65d`，400 槽，硬预算 396/400。只有兼容分支 `stage_3` 仍保留 394/400 和 `outputs/stage2/875ddf42e70e37db8455`。引用时要分开，不能把旧副本写成推荐结果。
- 阶段三 CUDA run `e8f151b9c286648caf98`：pilot 100 题，3500/3500。LongLLMLingua 2x EM 83.2%，原始提示 84.6%，差 −1.4 个百分点，95% 区间 [−6.2, 3.0]。4x 为 79.0%，18/500 未达硬预算。设备只记到 `cuda:0`。
- 阶段四 910B run `a9d2295195adde90484d`：同机完整方法 82.6%，去掉粗粒度后 45.0%。效率 run `2a7f4accf6127178a76b`：每方法 99 槽，完整 2x 端到端 p50/p95 为 6.45/7.49 秒，原始提示 1.12/1.54 秒。这不是 API 账单，也不是 Cursor 会话时间。

这些数字来自 `docs/presentation/01-number-registry.md`。CUDA 和 910B 的耗时不能相加。

## 4 Cursor 对话为什么还没有结果

课程如果改用 Cursor 会话作问答，它必须是新的设置。本机没有 Cursor CLI。公开文档里的 `agent -p` 和 `--mode=ask` 仍能使用搜索、读文件或 shell。Cloud Agent 子代理也会看到本仓库。没有开关可以同时关掉工具、固定采样并记录不可变模型版本。

所以关卡未通过。仓库里只有协议、300 个槽的 ID 清单，以及 3 条盲提示。这 3 条提示的 token 与同一 DeepSeek 槽一致，但没有 Cursor 回答，也没有分数。评分脚本在缺少回复文件时退出码为 2。

在产品不能禁止工具和仓库访问之前，不跑 300 槽，也不把任何会话时间写进效率表。

## 5 其余阶段只做了记录核对

`scripts/audit_stage2_offline.py`、`audit_stage3_offline.py`、`audit_stage4_offline.py` 只读已提交表格。阶段二是 400 槽、预算 396 加 4 条超标。阶段三是 3500 槽，统计均值和 summary 一致。阶段四消融 3500、效率 1200，csv 与统计文件一致，恢复负面案例仍是 3 条。三个脚本都没有调用 API，也没有改原文件。

这些核对不是成员二、三、四的亲自运行记录。新的压缩、新的配对问答和新的消融仍然缺权重或受控会话。

## 6 当前演示稿

9 页文件在 `docs/presentation/final/`。演讲顺序是物理页 1、2、3、4、5、8、6、9、7。四人各 90 秒，提问和换人另计。这不是已经计时的现场记录，也不是课程 zip。

物理第 8 页写了 `configs/stage3-pilot-as-run.json`。该文件不在仓库里。演示时改打开 `reports/stage3-main/run.json`。幻灯片字节没有为了这条路径被改写。

## 7 尚未完成

正式 `report.pdf` 已入库。延河课堂还没有提交。P 编号、登记表四人信息、录屏和真人计时仍缺。阶段二/三/四的完整问答与压缩缓存不在 git 里，不能编造。阶段四 CANN 未登记；阶段二报告里的 CANN 8.5.2 只属于那次 smoke。CUDA 只记到 `cuda:0`。压缩权重上的新消融没有做。离线测试只复核代码和已提交记录，本轮没有新的模型调用。本文不把本轮写成满分完成。

## 参考文献

Jiang, Huiqiang, Qianhui Wu, Xufang Luo, Dongsheng Li, Chin-Yew Lin, Yuqing Yang, and Lili Qiu. 2024. LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression. arXiv:2310.06839v2. ACL 2024 long paper 2024.acl-long.91.

Liu, Nelson，及 lost-in-the-middle 仓库中的 Lost in the Middle 数据与模板。本仓库只核对到版权人 Nelson Liu，2023，见 `vendor/lost_in_the_middle/LICENSE`。数据与模板锁定提交 `29b8a6d042ce29abccee3db1a73171a107d7e6af`，见 `manifests/resources.json`。合著者名单待从该提交的论文页补全，这里不另写。

压缩实现锁定 microsoft/LLMLingua 提交 `5a4c78ae18ab17a98cf997e8259354e546081d64`。

## 包内清单

| 路径 | 状态 |
| --- | --- |
| `docs/presentation/report/report.pdf` | 正式报告。同目录 `report.docx`、`report.md`、`SOURCES.md` 是可编辑源 |
| `docs/presentation/final/slides.pptx` 与 `slides.pdf` | 当前 9 页演示稿。旧骨架 `docs/presentation/slides/G14-LongLLMLingua-template.pptx` 不是这份 slides |
| `README.md` | 已指向 `docs/presentation/final/` |
| `data/README.md` | 已有来源、sha256 和划分。五个 gz 不进包 |
| `contributions.md` | 成员一有记录。其他三人的亲历段仍待本人填写 |
| `code/` 与 `configs/` | 仓库已有。打包时不要带 `.env`、权重和 `outputs/` |
| `results/` 轻量汇总 | 阶段一至四的 json/csv 已在 `reports/` |
| 逐条全文 | 组内存储，缺 sha256 |
| 至少 10 条案例 | DeepSeek 侧已有 13 槽。Cursor 侧为 0 |
| 运行证据 | `scripts/run_stage1_evidence.sh`。备份是打开已有 json，不是现场训练 |
