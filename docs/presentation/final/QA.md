# G14 LongLLMLingua｜QA（另计90秒）
建议三题各30秒，未真人计时；未被问到的条目作备查。

## 成员二：是否复现了原论文？
是官方方法链的适配复现，不是原模型原设置的逐值复现。DeepSeek替换GPT，恢复分词器也变更；k映射无效，指令与问题压缩未实现。

## 成员三：区间跨零是否等效？预算是否公平？
不是。Long2x-original的95%配对区间[-6.2,+3.0]跨零，只能说现样本未排除零差异，没有预设等效界。Long4x18/500超预算，不能称严格同预算。stage2另外396/400满足，4条异常有原记录但不猜原因。

## 成员四：是否获得加速？恢复一定有效吗？
独立NPU效率中没有端到端加速：original/Long2x p50为1.12/6.45秒。阶段中位数不能相加。已有恢复案例含3个1→0槽；no_recovery是已有回答派生评分，不是新增推理。

## 成员一：92和84.6为何不同？EM能否代表语义正确？
stage1 smoke20的92/87/64来自300槽；CUDA pilot100的84.6/83.2/79是不同批次。首行best_subspan_em有否认回答仍得1的真实例子，所以不改官方指标但注明语义边界。

## 备查：现场跑了吗？缺什么？
没有。本次只打开既有记录，Cursor受控对话未执行，无新对话分数、新推理或新API。缺CUDA型号、CANN版本及stage2/3/4完整输出与校验和；已有stage1 canonical预测不在此缺失范围。Windows/投影、真人计时、录屏未完成。不声称课程全满分验收通过。

## B1命令做什么？
`python -m json.tool reports/stage3-main/run.json`只格式化查看已有pilot运行快照，不加载模型、不调用API，不生成计划。默认configs/stage3.json是main，不能拿来解释pilot。B2命令仍为`python scripts/analyze_stage4.py --out /tmp/g14-stage4-audit`，保留临时out，避免覆盖已提交结果；本轮未执行。


## v5 本轮补充核验
仅更改视觉表达与图表指认，原数据变化为0；不新增推理/API。P1/P2/P7保留结论横幅，P3/P4/P5/P6/P8/P9改局部证据表达。
P5七方法可编辑点图按原方法顺序，EM轴0–100；仅右侧两条真实问题级配对CI，跨0不证明等效，Long4x18/500超预算。
P6以NPU full82.6为配对参照；ablation.csv与analyze_stage4.py L54–71证明CI来自paired_comparisons，full无CI、original外部参照、no_recovery为已有回答派生。右侧独立效率total_pipeline_seconds_p50/p95是分位点，非CI；没有端到端加速。
P9保留原效率图，阶段中位数不能相加为E2E。P8只查看已有pilot快照：`python -m json.tool reports/stage3-main/run.json`。P9保留`python scripts/analyze_stage4.py --out /tmp/g14-stage4-audit`，本轮两命令均未执行。
作图原值/线性映射见sources/g2/v5-chart-data-and-mapping.json，独立坐标核对见chart-source-audit-v5.json。历史输出缓存、CUDA型号、CANN缺口保留；Windows投影与真人计时未验证。
