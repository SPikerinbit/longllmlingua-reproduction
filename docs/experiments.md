# 实验配置、结果来源与复核

## 数据与比较口径

本轮课程主比较与消融采用固定 pilot 100 题 × 五位置，使用原有 seed=42 嵌套清单，不重新抽样、不按分数选题。原 500 题完整矩阵不属于本轮验收范围；`manifests/main.json` 和相应旧配置作为扩展配置保留，不代表已有 500 题完整结果。

每题 20 文档，答案位置为 1/5/10/15/20。原始提示只运行一次，其余三种主比较方法分别设 2x/4x；实际比值按完整提示的固定 DeepSeek token 计数测量。方法输入只接收问题与文档，不包含答案、gold 或答案位置。指标沿用上游首行 best_subspan_em；按问题 ID 配对 bootstrap，重采样时保留该题全部五位置，seed=42、2000 次、95% 区间。

## 结果来源

| 阶段 | 原始 run_id | 样本与覆盖 | 记录位置 |
| --- | --- | --- | --- |
| 一 | d54b3118c61ea4930624 | smoke 20题，300槽 | `reports/stage1-acceptance/` |
| 二 | a1bd26fe3d82dea3f65d | smoke 20题，400槽 | `reports/stage2-smoke/` |
| 三 | e8f151b9c286648caf98 | pilot 100题，3500槽 | `reports/stage3-main/` |
| 四消融 | a9d2295195adde90484d | pilot 100题，3500槽 | `reports/stage4-ablation-efficiency/` |
| 四效率 | 2a7f4accf6127178a76b | smoke 20题，1200槽 | 同上，独立会话 course100-efficiency-final-v1 |

各阶段代码统一到根目录 `reproduction/`。阶段三的批量调度与统计由成员三交付；第四阶段增加云端执行、采样和离线分析脚本。重整仅调整统计脚本和测试读取结果的路径，未改变历史压缩、评分、问答或恢复算法；历史配置摘要、实现摘要和结果标签保留。

阶段三收到的压缩器记录仅明确 `cuda:0`，没有可核验的精确 GPU 型号或完整会话环境，不能擅自补写为 V100。阶段二历史 NPU 环境与第四阶段实际环境分别登记，不能把阶段二 CANN 版本当作第四阶段实测值。

## 第四阶段环境

实际返回记录见 `reports/stage4-ablation-efficiency/environment/`：Ascend910B4，HBM总量32768MB；Python 3.12.0，torch 2.7.1、torch_npu 2.7.1.post2、transformers 4.53.1、tokenizers 0.21.4、numpy 1.26.4、accelerate 1.0.1。

npu-smi 工具/驱动输出版本为25.5.1，不等于 CANN 版本；本次 CANN 未单独登记。压缩权重为 NousResearch/Llama-2-7b-chat-hf，revision `351844e75ed0bcbbe3f10671b3c808d2b83894ee`，npu:0、fp16、eager、单进程。QA 返回的 model 别名与 fingerprint 有记录，但不能单独证明不可变的历史模型快照。

## 消融设置与核验

`configs/stage4-ablation.json` 是实际100题消融配置。完整方法2x、原始提示与五个变体各500槽；一次只改变粗粒度问题感知、细粒度问题感知、动态预算、restrict或重排序中的一个配置。主比较已经关闭重排序，因此重排序是额外开启实验。恢复移除使用完整方法同一原回答单独评分，不新增问答。

消融3500槽成功、无失败或缺失、完整提示预算全部满足；3000槽恢复输出重放一致，3500槽QA缓存和3000槽压缩缓存核对一致。最终返回包的消融run.json与results.jsonl同此前已核验版本逐字节相同，因此复用原重放证据。最终效率1200槽重新独立核验，恢复重放700槽、原始/BM25提示重建300条均一致。核验记录见 `inputs/validation.json`。

各变体均有实际提示变化，行为对照见 `received-mechanism-checks.json`。硬预算重试可能进一步改变保留文档，这是执行反馈，不等于手动同时修改了多个机制。恢复损伤案例见 `inputs/recovery-cases.json`：三个槽位由对变错，涉及长跨度扩展与首行评估的相互作用，主指标保留原口径。

## 效率设置

`configs/stage4-efficiency.json` 与 `configs/cloud/efficiency-final.json` 为最终独立运行配置。smoke20题五位置12组合全部成功，未命中本地QA或压缩缓存。模型加载和两次压缩预热在逐槽计时之前；另按身份剔除每方法首个样本，最终99条/方法，五位置数量为19/20/20/20/20。相同负载键、p50/p95与峰值allocated HBM见 `efficiency.json`。

计时包括各自记录的网络/重试，不包括循环外限流间隔；API服务端prompt cache未关闭，不能等同于服务端无缓存。GB为十进制1e9字节，阶段中位数相加不等于端到端中位数。完整方法压缩p50/p95约5.23/6.10秒、QA1.12/1.58秒、恢复0.023/0.027秒；不能用本地缓存读取时间声称推理加速。

旧效率run `6fa24e170b73981099fd` 因HTTP402中断，738成功、1失败、461缺失；它及500题部分运行保留在组内原始归档，不进入最终统计。最终效率使用单独完整会话，不拼接两次测量。保存响应usage合计输入1,694,940、输出85,588 token；usage不是平台账单，不按旧价格推算金额。

## 重建与独立复核

在仓库根目录，无需云服务器或API即可重建：

```bash
python scripts/analyze_stage4.py
python scripts/plot_results.py
```

前者从轻量逐槽指标重建消融、配对统计、覆盖率、效率和usage表；后者从保存的主比较汇总和重建表绘图。阶段三已有汇总、覆盖率、配对统计和独立核验结果一并保留；要从原始回答再次评分，需要组内保存的原始包。

完整数据和tokenizer可运行 `python -m reproduction prepare` 获取。将最终原始返回包解压到本地 `data/final/` 后，可独立重评分、重建提示并重放恢复：

```bash
python scripts/validate_received.py --ablation data/final/outputs/stage3/a9d2295195adde90484d --efficiency data/final/outputs/stage3/2a7f4accf6127178a76b --data-root data --cache-root data/final/cache --out outputs/final-validation
```

重核验使用tokenizers=0.21.4，与云端固定计数环境一致。命令不加载压缩模型、不调用问答API，输出单独放在outputs中，不覆盖已提交的核验记录。

成员二、三的原始包核查入口分别为 `scripts/verify_member2_handoff.py` 和 `scripts/verify_member3_handoff.py`。保留的历史核验JSON中“500题尚缺”等判断属于当时原计划；本轮课程完成标准以固定100题范围为准，历史结果本身未改写。

## 已知差异与交付状态

论文历史GPT问答模型已替换；指令/问题预压缩未实现；k=2的近似映射在该LongLLMLingua路径无效；恢复使用DeepSeek tokenizer。具体源码映射见 `stage2-parameter-map.md`。阶段二smoke有4条、阶段三LongLLMLingua4x有18条预算超标，均保留实测记录。

实验完成与队友PR复核分别登记，不提前创建stage4-ready。中期报告将在PR完成后另行撰写。原始数据、模型、完整预测、请求缓存及实验运行日志留在组内存储；仓库提交代码、配置、样本清单、轻量证据和必要许可证。
