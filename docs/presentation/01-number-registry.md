# 可引用数字

幻灯片和报告只使用下表。百分数和压缩比若与 README 的舍入一致，页上用 README 的写法，并在来源里同时写出未舍入文件。不要把阶段一 smoke 的 92.0% 写成主结果，也不要把 CUDA 的 83.2% 和 910B 的 82.6% 当成同一次实验。

## 阶段一 smoke，20 题 × 5 位置 × 3 方法

run `d54b3118c61ea4930624`。`reports/stage1-acceptance/acceptance.json`：success 300，failed 0，missing 0。

| 方法 | EM | 实测压缩比 | 来源 |
| --- | ---: | ---: | --- |
| original | 92.0% | 1.000x | `REPORT.md` 与 `acceptance.json` 的 `em_percent` / `mean_actual_ratio` 1.0 |
| bm25_2x | 87.0% | 2.001x | 同上，未舍入比值 2.001444482441135 |
| bm25_4x | 64.0% | 4.007x | 同上，未舍入比值 4.006806278428931 |

`summary.md` 把每个位置的比值印成两位小数（4.01），和上表的 4.007x 不是两个实验。位置 1/5/10/15/20 的 original EM 是 95、95、90、90、90，每格 20 题。

问答：`configs/stage1.json`，deepseek-flash，temperature 0，max_tokens 512，非思考。fingerprint `bc19ba97cbe016479903222bb1578db6` 只说明返回别名，不能证明模型快照。

## 阶段二 smoke，20 题 × 5 位置 × 4 方法

run `a1bd26fe3d82dea3f65d`。`reports/stage2-smoke/verification.json`：400 槽，硬预算满足 396，超标 4。

| 方法 | EM | 来源 |
| --- | ---: | --- |
| llmlingua_2x | 0.620 | `REPORT.md` 主表；verification `em_after` 0.62 |
| llmlingua_4x | 0.460 | 同上 |
| longllmlingua_2x | 0.940 | 同上；恢复改变 9/100 条回答，EM 不变 |
| longllmlingua_4x | 0.880 | 同上；四个位置的预算满足率 0.95，见 `summary.json` |

4 条超标的 slot 前缀都是 `23707ea627731d1e8786f6a2d21e325e8c4d0d6c8c741752da1b2d91d0e8048e`，方法 `longllmlingua_4x`，目标 742，实测 749、751、754、753。问题感知排名改变保留文档：`REPORT.md` 第 4 节写 100/100。

## 阶段三主比较，pilot 100 题 × 5 位置 × 7 方法

run `e8f151b9c286648caf98`，split=pilot，设备只记到 `cuda:0`。`coverage.json`：3500/3500，failed 0，missing 0。下表 EM 与 README 主比较表一致，未舍入值在 `summary.json` 的 `mean_em`。

| 方法 | EM | README 压缩比 | 未舍入 `mean_actual_ratio` | 预算满足 |
| --- | ---: | ---: | ---: | ---: |
| original | 84.6% | 1.00x | 1.0 | 1.0 |
| bm25_2x | 72.4% | 2.00x | 2.001659249299371 | 1.0 |
| bm25_4x | 55.8% | 4.01x | 4.006014731935584 | 1.0 |
| llmlingua_2x | 46.8% | 2.04x | 2.043583184994991 | 1.0 |
| llmlingua_4x | 35.6% | 4.17x | 4.172981157130074 | 1.0 |
| longllmlingua_2x | 83.2% | 2.08x | 2.0799542177673707 | 1.0 |
| longllmlingua_4x | 79.0% | 4.09x | 4.089871205331284 | 0.964 |

`stats.json` 相对 original，100 题，bootstrap 2000，seed 42，95%：

| 方法 | 差 | 区间 |
| --- | ---: | --- |
| bm25_2x | −0.122 | [−0.192, −0.058] |
| bm25_4x | −0.288 | [−0.376, −0.194] |
| llmlingua_2x | −0.378 | [−0.468, −0.292] |
| llmlingua_4x | −0.490 | [−0.576, −0.400] |
| longllmlingua_2x | −0.014 | [−0.062, 0.030] |
| longllmlingua_4x | −0.056 | [−0.116, −0.004] |

页上把 2x 写成 −1.4 个百分点、区间 [−6.2, 3.0]，与 README 第 48 行一致。4x 区间不跨 0。0.964 × 500 = 482，所以 18/500 未达硬预算，成功槽仍是 500。

五位置 EM（每格 100 题，`summary.json` 的 `groups`）：LongLLMLingua 2x 为 83、83、82、84、84。原始提示为 84、84、84、85、86。

`configs/stage3.json` 的 `split` 是 `main`。它不是这次 3500 槽的配置。现场打开 `run.json`。

## 阶段四消融，910B，同一 100 题

run `a9d2295195adde90484d`。`RESULTS.md` / `ablation.csv`，每行 n=500。差值相对同机 `longllmlingua_2x` 的 82.6%，不是相对 CUDA 的 83.2%。

| 方法 | EM | 差值（pp） | 95% 区间（pp） |
| --- | ---: | ---: | --- |
| original | 84.6 | +2.0 | [−2.2, 7.0] |
| longllmlingua_2x | 82.6 | 0 | 参照 |
| 去掉粗粒度 | 45.0 | −37.6 | [−47.2, −28.4] |
| 去掉细粒度 | 81.2 | −1.4 | [−4.2, 1.2] |
| 去掉动态预算 | 78.0 | −4.6 | [−8.6, −0.8] |
| 去掉 restrict | 83.2 | +0.6 | [−2.2, 3.6] |
| 打开重排序 | 79.6 | −3.0 | [−7.2, 0.8] |
| 去掉恢复 | 83.2 | +0.6 | [0.0, 1.6] |

`inputs/recovery-cases.json` 有 3 条，恢复前 score 1.0、恢复后 0.0。细粒度、restrict、重排序的区间跨 0。

## 阶段四效率，另一批 smoke

run `2a7f4accf6127178a76b`。`coverage.json`：1200/1200。`efficiency.csv` 每方法 n=99。位置分布 19/20/20/20/20，见 `RESULTS.md`。

| 方法 | 端到端 p50 | 端到端 p95 | 峰值 allocated GB |
| --- | ---: | ---: | ---: |
| original | 1.120468680979684 | 1.5420867950422685 | 空 |
| longllmlingua_2x | 6.449125320883468 | 7.4866623027483 | 16.428089344 |

页上按 README 写成 1.12/1.54 秒、6.45/7.49 秒、约 16.43 GB。GB 是十进制 1e9 字节。阶段中位数相加不等于端到端中位数。完整方法压缩 p50/p95 约 5.23/6.10 秒，QA 1.12/1.58 秒，恢复 0.023/0.027 秒，见 `docs/experiments.md`。

`usage.json` 的 efficiency 块：唯一保存响应输入 1,694,940、输出 85,588 token。ablation 块是另一组数（输入 5,762,538、输出 259,603），不要加总后当成一次账单。不换算金额。

## 环境

`environment-current.json`：Python 3.12.0，torch 2.7.1，torch_npu 2.7.1.post2，transformers 4.53.1，tokenizers 0.21.4，numpy 1.26.4，accelerate 1.0.1，npu_name Ascend910B4。`docs/experiments.md` 写 HBM 总量 32768 MB，npu-smi 25.5.1 不等于 CANN。

`package-versions.json` 里另有 `tokenizers` 0.21.0。两个文件不一致。幻灯片用 `environment-current.json` 的 0.21.4，并口头说明这个不一致，不要把 0.21.0 说成同一次记录。

压缩权重 revision `351844e75ed0bcbbe3f10671b3c808d2b83894ee`，见 `docs/experiments.md`。

## 阶段一离线审计（2026-11-21，无新 API）

来源 `reports/stage1-supplement/offline-audit.json`。`predictions.jsonl` 的 sha256 是 `cac37c9e84678f2f591af8c4f6ccdb7a69d010cf71eae5678b85109bcb27bd62`。五个 NQ gz 的 sha256 与 `manifests/resources.json` 一致。审计耗时 2.055 秒，Python 3.12.3，API 调用数 0。

| 检查 | 结果 |
| --- | --- |
| smoke 是 pilot 前 20、pilot 是 main 前 100 | 是 |
| 20 题 × 五位置文档集合一致、gold 位置正确、可见字段无答案 | 失败 0 |
| 300 槽预算 | 违规 0。在线 prompt token 全部等于本地压缩 token + 4 |
| 用同一 `best_subspan_em` 重评分 | 与已存 score 不一致 0 条。均值仍是 0.92 / 0.87 / 0.64 |
| 诊断：首行为 0、把换行拼成空格后为 1 | 2 槽，都在问题 `64a3debb…` 的 original、位置 5 和 20 |
| 诊断：首行强否认且官方分数为 1 | 4 槽，同一题的 bm25，位置 1、10、15 中的四条 |

诊断不是新的主指标。13 条槽写在 `reports/stage1-supplement/cases.md`。

## 当前 9 页演示稿

提交用的文件是 `docs/presentation/final/slides.pptx` 与同目录 `slides.pdf`。`docs/presentation/slides/G14-LongLLMLingua-template.pptx` 是更早的骨架，不是这份 slides。P1、P2、P7 保留结论横幅，其余 6 页改为就地表达。页上主比较、阶段一 smoke、阶段二 396/400、阶段四 82.6/45.0/78.0 和效率 1.12/6.45 秒与本登记表一致。

作图映射 `docs/presentation/final/v5-chart-data-and-mapping.json` 已与仓库原件逐字段核对：`summary.json` 的 7 个方法、`stats.json` 的 Long 2x/4x 两条区间、`ablation.csv` 的 8 行、`efficiency.csv` 里 original 与 Long 2x 的 p50/p95。不一致 0 条。21 个点是 7 个 EM、2 个区间中心、8 个消融差值、4 个效率端点；9 条区间是主比较 2 条加消融 7 条，full 行没有区间。位置 EM original 84/84/84/85/86、Long 2x 83/83/82/84/84 来自 `summary.json` 的 groups。这次核对的是数值，没有重测幻灯片上的英寸坐标。

物理第 8 页（B1）现在的命令是 `python -m json.tool reports/stage3-main/run.json`。它只读打印已保存的 pilot 运行快照。仓库里仍然没有 `configs/stage3-pilot-as-run.json`，默认 `configs/stage3.json` 的 split 仍是 main。上一版页上的 plan 配置路径已经从这一版幻灯片正文去掉。本轮没有执行该命令，也没有新推理。

物理第 9 页（B2）的 `python scripts/analyze_stage4.py --out /tmp/g14-stage4-audit` 与脚本参数一致。默认 `--out` 会写回 `reports/stage4-ablation-efficiency/`。现场若要跑，必须把输出放到临时目录。本轮没有执行。

## cursor_dialogue

没有回答，没有分数，没有耗时。关卡未通过，见 `reports/cursor_dialogue/PROTOCOL.md`。试跑只准备了 3 条盲提示；重建后的 token 与同一 DeepSeek 槽一致：original 3289/3289/3289，bm25_2x 3289/1644/1644，bm25_4x 3289/822/822。不能把这些数字写成 Cursor 的 EM 或延迟。

## 本机计时（2026-11-21，无 API）

`python scripts/analyze_stage4.py` 用时 0.337 秒，会重写 `ablation.csv` 和 `efficiency.csv`。`python scripts/plot_results.py` 在安装 matplotlib 3.10.0 后用时 1.413 秒，会重写三张图。两次运行后都已用 git 恢复原文件。现场可以跑分析脚本，不要把覆盖提交进仓库。
