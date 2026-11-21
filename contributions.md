# 贡献

四人按阶段各约 25%。压缩算法来自 microsoft/LLMLingua 提交 `5a4c78ae18ab17a98cf997e8259354e546081d64`，不是本组原创。姓名以课程登记表为准。除成员一外，下面三段要由本人替换，不能由别人代填。

## 成员一（阶段一；登记表姓名待补）

阶段一，约 25%。负责固定数据、提示模板、问答缓存、`best_subspan_em`、原始提示和 BM25。不负责 3500 槽主比较，也不负责 910B 消融。

实际做了的路径：

- 数据与 ID：`reproduction/data.py`，清单 `manifests/smoke.json`、`pilot.json`、`main.json`，校验 `manifests/resources.json`。
- 模板和评分：`vendor/lost_in_the_middle/qa.prompt`、`metrics.py`，调用在 `reproduction/evaluation.py`。
- BM25 与预算：`reproduction/methods.py`，参数在 `configs/stage1.json`（k1=1.5，b=0.75）。
- 入口：`python -m reproduction`，说明在 `docs/stage1-implementation.md`。

个人运行：

- 配置 `configs/stage1.json`，split=smoke，seed 42，deepseek-flash，temperature 0，max_tokens 512。
- 验收 run `d54b3118c61ea4930624`，配置哈希 `621ac92b0374e28d2773616142ea7949288aea0f2d5571a812e93289b7364667`。
- 记录在 `reports/stage1-acceptance/`。300 槽成功，0 失败，0 缺失。EM 为 original 92.0%、BM25 2x 87.0%、BM25 4x 64.0%。
- 完整提示和 cache 在组内目录 `outputs/stage1/d54b3118c61ea4930624`。该目录不在 git 里，sha256 还没有写进仓库。

个人核验：

- 不调用 API，可由 `predictions.jsonl` 的 300 行重算三个 EM。2026-11-21 重算结果是 0.92、0.87、0.64。
- `acceptance.json` 记录当时 `offline_rescore_identical` 为 true，`prompts_and_budgets_rebuilt` 为 true。
- 这次不能重跑 `python scripts/accept_stage1.py <run_dir>`，因为仓库里没有完整 `results.jsonl` 和 `cache/api`。

提交包中由成员一写入的初稿：`data/README.md`，本文件的这一节，`docs/presentation/members/member1/` 下的幻灯片、讲稿、报告节、三条案例和 QA。

AI 使用：2026-11-21 用 Cursor 里的编码助手整理了上述汇报文档和幻灯片，数字要求来自仓库已有文件。助手没有新跑问答 API。`analyze_stage4.py` 和 `plot_results.py` 曾为了计时各跑一次，随后用 git 恢复了被改写的 csv 和 png。

不计入成员一的结果：阶段三 CUDA 主比较，阶段四 910B 消融和效率。

2026-11-21 把正式报告放进 `docs/presentation/report/`，随后把 9 页演示稿换成当前 `docs/presentation/final/` 文件。这是在用户授权下由编码助手做的离线汇编，没有新推理，没有 Cursor 受控对话结果，也没有替成员二至四勾选本人确认。课程规范要求贡献说明里有四人信息和实际贡献；原文没有单独要求“法定姓名”。姓名仍以登记表为准，仓库不编造。

2026-11-21 的补充工作只做了两件已经发生的事。一件是离线审计：`scripts/audit_stage1_offline.py` 重读了 `predictions.jsonl` 和五个已校验的 NQ 文件，没有调用 API，没有改 `reports/stage1-acceptance/`。另一件是确认 Cursor 对话不能作为受控问答：本机没有 Cursor CLI，公开文档中的 Ask/print 模式仍有工具。因此没有 cursor_dialogue 回答。三份盲提示和独立 gold 文件在 `reports/cursor_dialogue/trial/`。阶段二压缩、阶段三新的配对比较和阶段四新的消融都没有新跑，因为没有压缩权重，也不能用对话假装压缩。

同日稍后，在已推 `main` `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4` 上用 Python 3.13.5 与 `tokenizers==0.22.1` 执行官方 `python -m reproduction prepare`，公开下载五个 NQ gz 和上述 revision 的 `tokenizer.json`，哈希与 `manifests/resources.json` 一致。随后完整 `python -m pytest` 收集 77 项、全部通过，退出码 0（17:46:58–17:47:02，Asia/Shanghai）。配齐数据前同为 77 项收集，72 通过、5 失败。日志与命令的相对路径在 `reports/local-verification/`。四阶段离线审计的 API 调用为 0，已发表分数未改。这不是本机重新做模型推理，也不替成员二至四填写亲历段。

## 成员二（阶段二；待本人填写）

待替换。应写的路径至少包括 `python -m reproduction.stage2`、`configs/stage2.json`、run `a1bd26fe3d82dea3f65d`、`reports/stage2-smoke/`、`docs/stage2-parameter-map.md`。不要把阶段一的 300 槽或阶段三的 3500 槽算进自己的运行。

## 成员三（阶段三；待本人填写）

待替换。应写的路径至少包括 `python -m reproduction.stage3`、run `e8f151b9c286648caf98`、`reports/stage3-main/summary.json` 与 `stats.json`。要写明 `configs/stage3.json` 的 split 是 main，实际 100 题快照在 `run.json`，设备只记到 `cuda:0`。

## 成员四（阶段四；待本人填写）

待替换。应写的路径至少包括 `configs/stage4-ablation.json`、`configs/stage4-efficiency.json`、run `a9d2295195adde90484d` 与 `2a7f4accf6127178a76b`、`python scripts/analyze_stage4.py`、`environment-current.json`。要写明消融 EM 82.6% 不是主比较的 83.2%。
