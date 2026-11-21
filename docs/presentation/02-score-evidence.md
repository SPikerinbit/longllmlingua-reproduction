# 五项验收证据

课程原文见 <https://nlp.hltbit.top/2026/materials/w01/classroom/requirements.html> 第七节。论文项目五项各 8 分：论文理解与范围、数据与实现、对照指标与消融、错误分析与结论、交付与汇报答问。记分档是 0、3、6、8，结合证据说明原因。模型大小、年份、费用、网页是否好看、分数有没有超过论文，都不单独加分。

下面只做两件事：把仓库里已经能打开的文件对应到这五项，并列出还不能勾选的缺口。教师没有公布每一档的细分规则，这里不补写一套未发布的细则，也不把“文件齐了”说成一定会得到 8 分。8 分目标的意思是：被点到的人能用这些路径把该项的证据链讲完，而且缺口里的项已经按表做完并经过本人复核。

未经过本次或本人重新运行的历史结果，不能在自检表里勾成“本环境已复现”。离线重建和当年的真实运行要分开说。

## 已知环境差异

这些差异都有两个文件可以同时打开。在本人写出原因之前，相关验收项保持未勾选。

| 差异 | 文件 A | 文件 B | 后果 |
| --- | --- | --- | --- |
| tokenizers | `reports/stage4-ablation-efficiency/environment/environment-current.json` 为 0.21.4 | `environment/package-versions.json` 为 0.21.0 | 不能把两个版本说成同一次环境记录 |
| 阶段三硬件 | `reports/stage3-main/run.json` 的 `compressor.device` 只有 `cuda:0` | 论文写 V100-32G，见 `docs/stage2-parameter-map.md` | 不能补写 GPU 型号 |
| CANN | 阶段二 `reports/stage2-smoke/REPORT.md` 写 CANN 8.5.2 | `docs/experiments.md` 写阶段四 CANN 未登记；npu-smi 25.5.1 不等于 CANN | 不能把阶段二的 CANN 当成 910B 消融的版本 |
| 峰值显存 | 阶段二 REPORT 写峰值 16.67 GB | `efficiency.csv` 的 `longllmlingua_2x` 为 16.428089344 GB | 两次测量，不能写成同一个峰值 |
| 阶段二验收副本 | `main` 与四条推荐分支上的 `reports/smoke-stage2-acceptance.json` 是 396/400，`accepted_run` 为 `outputs/stage2/a1bd26fe3d82dea3f65d` | 只有兼容分支 `stage_3` 仍保留 394/400，`accepted_run` 为 `outputs/stage2/875ddf42e70e37db8455` | 推荐分支和 `main` 不再写成继承了 394 那一份。引用超标条数时要说明是哪一个分支 |
| 问答快照 | 配置期望 `DeepSeek-V4.1-Flash-1017` | 返回 fingerprint `bc19ba97cbe016479903222bb1578db6` | fingerprint 不能证明不可变模型快照 |

## 五项

### 1 论文理解与范围

8 分目标：能指出论文版本、要检验的结论、本组实际范围，以及哪些论文设置没有实现。

已有：

- 论文 arXiv:2310.06839v2，代码提交 `5a4c78ae18ab17a98cf997e8259354e546081d64`，见 `manifests/resources.json` 与 `AGENTS.md`。
- 课程范围是 pilot 100 题 × 五位置，500 题清单不作本轮结果，见 `docs/experiments.md` 与 `manifests/main.json`。
- 未实现或无效的设置：k=2、τ_ins、τ_que，见 `docs/stage2-parameter-map.md`。

未勾选：P 编号仍是 `Pxx`。登记表里的原文表号、要核对的论文行列，仓库没有抄进来。负责人是联系人，把教师确认的 P 编号写入包名后再由成员一改 P1 的占位。PPT 视觉本轮不改。

### 2 数据与实现

8 分目标：换一台机器时，能按写明的版本、校验和命令得到同一套输入，并分得清哪些步骤不调用 API。

已有：

- 五个数据文件的字节数和 sha256 在 `manifests/resources.json`。取得命令是 `python -m reproduction prepare`，不下载权重、不调用问答 API。说明在 `data/README.md`（只在 `stage1-foundation`）。
- 问题 ID 与嵌套划分在 `manifests/smoke.json`、`pilot.json`、`main.json`。`reproduction/data.py` 的 `question_id`。
- 压缩权重记录：`NousResearch/Llama-2-7b-chat-hf`，revision `351844e75ed0bcbbe3f10671b3c808d2b83894ee`，见 `docs/experiments.md`。权重本身不在 git 里。
- 问答：`configs/stage1.json` 与各阶段配置里的 deepseek-flash、temperature 0、max_tokens 512。密钥变量名是 `DEEPSEEK_API_KEY`，见 `.env.example`。`.gitignore` 忽略 `.env`。
- 阶段四实测环境：`environment-current.json`。Python 3.12.0，torch 2.7.1，torch_npu 2.7.1.post2，transformers 4.53.1，tokenizers 0.21.4，numpy 1.26.4，accelerate 1.0.1，Ascend910B4。

未勾选，必须本人在目标环境跑完才能勾：

| 缺口 | 负责人 | 命令 | 预期 | 验收 |
| --- | --- | --- | --- | --- |
| 新环境安装后的版本锁 | 成员四记录 910B；成员三记录 CUDA 机 | 在对应机器上执行 `python scripts/cloud910b.py check`，或成员三把自己的 `nvidia-smi` 与包版本写入 `results/stage3/environment.txt` | 输出含设备名和包版本 | 与将要引用的 json 逐项一致，不一致就并列两份，不合并成一句 |
| 数据校验 | 成员一 | `python -m reproduction prepare` 后对五个 gz 做 `sha256sum` | 与 `manifests/resources.json` 一致 | 把命令输出路径写进 `results/stage1/SOURCE.txt` |
| 组内全文的校验和 | 各阶段本人 | `sha256sum` 自己的 `results.jsonl` | 仓库里目前没有这些 sha256 | 没有文件就写“未取得”，不能留空 |

`data/` 下除 `README.md` 以外仍被忽略。四个推荐分支同步后的 `.gitignore` 都是 `/data/*` 加 `!/data/README.md`，并保留 `/data.tar.gz`。`stage_3` 的 `972aa1b` 也已经是这个规则。`data/README.md` 本身只在 `stage1-foundation`，不复制到其他分支。

### 3 对照指标与消融

8 分目标：同一指标、同一批题上比较基线和论文方法，消融一次只改一个因素，并给出区间和分母。

已有：

- 指标是首行 `best_subspan_em`，`reproduction/evaluation.py` 只把第一行送进 `vendor/lost_in_the_middle/metrics.py`。
- 主比较七行和区间在 `reports/stage3-main/summary.json`、`stats.json`。bootstrap 2000 次、seed 42、按问题配对并保留五位置，见 `stats.json` 文件头和 `docs/experiments.md`。
- 消融一次改一个开关，配置是 `configs/stage4-ablation.json`。重排序是额外打开，不是从已经关闭的主比较里再“移除”。数字在 `reports/stage4-ablation-efficiency/ablation.csv`。
- 单因素的行为变化记录在 `received-mechanism-checks.json`。
- 离线重建：`python scripts/analyze_stage4.py`。2026-11-21 在编写文档的机器上用时 0.337 秒，且会重写 csv。这是重建，不是新的真实推理。

未勾选：`configs/stage3.json` 的 split 仍是 `main`。100 题的实际快照在 `reports/stage3-main/run.json`。成员三要把该快照抽成 `configs/stage3-pilot-as-run.json` 再勾“配置与结果是同一份”。

### 4 错误分析与结论

8 分目标：至少 10 条真实逐样本案例，能说明失败或边界，结论不超过证据。

DeepSeek 侧已有 13 条可追溯槽，见 `reports/stage1-supplement/cases.md`。Cursor 对话侧是 0 条。

| 编号 | 位置 | 状态 |
| --- | --- | --- |
| S1-01 至 S1-13 | `reports/stage1-supplement/cases.md` | 来自阶段一 `predictions.jsonl`，含正确、BM25 失败和首行边界 |
| M4-01 至 M4-03 | `reports/stage4-ablation-efficiency/inputs/recovery-cases.json` 的 3 条 | 记录在结果文件里，尚未拆成 `results/cases/` |

未勾选：

| 缺口 | 负责人 | 命令 | 预期 | 验收 |
| --- | --- | --- | --- | --- |
| M2-01 至 M2-03 | 成员二 | 从组内 `outputs/stage2/a1bd26fe3d82dea3f65d/results.jsonl` 摘槽；超标槽也可对照 `reports/stage2-smoke/verification.json` | 一条目标 token 742 的超标，一条恢复改了回答，一条保留文档与 LLMLingua 不同 | 槽 ID 能在该 jsonl 或 verification 里找到 |
| M3-01 至 M3-03 | 成员三 | 从组内 run `e8f151b9c286648caf98` 的 `results.jsonl` 摘槽 | 每条有问题 ID、位置、方法、参考答案、输出、对错 | 不把 gold 写进“模型输入” |
| 案例目录 | 成员四汇编 | 把以上写成 `results/cases/M*.md` | 至少 10 条 | 每条都能回到一个 run_id |

结论句只能使用 `docs/presentation/01-number-registry.md` 里的数。CUDA 的 83.2% 和 910B 的 82.6% 不能写成一次实验。

### 5 交付与汇报答问

8 分目标：包内文件能对应到报告数字；老师点到谁，谁都能把自己的命令、配置、结果文件和失败案例讲清楚。

已有：四人任务书、数字登记、这份证据表、阶段一至四的轻量结果。离线测试 `tests/test_stage4_results.py`、`tests/test_cloud910b.py`、`tests/test_stage3.py`、`tests/test_stage4_recovery_analysis.py`、`tests/test_final_delivery.py` 在四条已同步分支上各 31 项通过。这些测试不加载权重、不调用 API。通过它们不等于当年的 3500 槽又跑了一遍。

报告文件已在 `docs/presentation/report/`。当前 slides 仍是 v4，在 `docs/presentation/final/`。v5 只改部分页上方绿色结论横幅的表达，数据、短标题和证据命令不动；v5 到达前不替换幻灯片，也不封课程 zip，也不出最终 bundle。未勾选：延河课堂提交、录屏、真人计时、P 编号、登记表四人信息、阶段二/三/四完整槽缓存。口播计时还没有用手机实讲。Cursor 受控对话没有回答。

## 真实运行和离线检查

| 动作 | 算什么 | 不能说成 |
| --- | --- | --- |
| `python -m reproduction.stage3 run` 且当时有密钥和权重 | 真实运行 | 在没有 `results.jsonl` 的机器上复述旧 EM |
| `python scripts/analyze_stage4.py` | 从 `inputs/metrics.jsonl` 重建表 | 新的压缩或问答 |
| `python -m pytest` 上表那 5 个文件 | 代码与轻量结果的离线检查 | 模型或 API 可用 |
| 打开 `verification.json` 里已有的 `passed: true` | 当时的核验记录 | 本次又重放了一遍，除非命令是这次执行的 |

密钥只放在环境变量或未入库的 `.env`。提交前对将要打包的目录搜 `DEEPSEEK_API_KEY=` 的值，而不是只相信 `.gitignore`。
