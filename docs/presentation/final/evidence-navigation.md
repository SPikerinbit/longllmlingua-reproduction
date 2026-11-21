# G14｜证据演示跳转表

只展示已有运行记录，不是现场推理；不运行模型或API，也不现场执行离线分析命令。放映可输入物理页码再回车。已有页脚链接：P5→B1→P6→B2→P7。

|演讲次序|物理页|内容|成员|秒|下一物理页|

|---|---|---|---|---|---|

|1|1|LongLLMLingua复现|1|25|2|

|2|2|数据与基线|1|35|3|

|3|3|压缩方法|2|45|4|

|4|4|预算验收|2|45|5|

|5|5|主要结果|3|60|8|

|6|8|CUDA运行记录|3|30|6|

|7|6|消融与效率|4|60|9|

|8|9|NPU运行记录|4|30|7|

|9|7|结果与边界|1|30|QA|

主讲P1–P7共300秒；B1/B2共60秒；每人90秒。QA90秒、换人总30秒另计；合计480秒（8分钟）的计划，不是实测。

B1指run→coverage→summary与stats；B2指run/coverage→环境→效率图。材料小字可用放大/备注备查，关键结论由20pt标签和18pt表承担。

B1：`python -m json.tool reports/stage3-main/run.json`——只读查看已保存pilot运行快照，非现场推理。本轮未执行。
B2：`python scripts/analyze_stage4.py --out /tmp/g14-stage4-audit`——保留临时out避免覆盖已提交结果；本轮未执行。


## v5 本轮补充核验
仅更改视觉表达与图表指认，原数据变化为0；不新增推理/API。P1/P2/P7保留结论横幅，P3/P4/P5/P6/P8/P9改局部证据表达。
P5七方法可编辑点图按原方法顺序，EM轴0–100；仅右侧两条真实问题级配对CI，跨0不证明等效，Long4x18/500超预算。
P6以NPU full82.6为配对参照；ablation.csv与analyze_stage4.py L54–71证明CI来自paired_comparisons，full无CI、original外部参照、no_recovery为已有回答派生。右侧独立效率total_pipeline_seconds_p50/p95是分位点，非CI；没有端到端加速。
P9保留原效率图，阶段中位数不能相加为E2E。P8只查看已有pilot快照：`python -m json.tool reports/stage3-main/run.json`。P9保留`python scripts/analyze_stage4.py --out /tmp/g14-stage4-audit`，本轮两命令均未执行。
作图原值/线性映射见sources/g2/v5-chart-data-and-mapping.json，独立坐标核对见chart-source-audit-v5.json。历史输出缓存、CUDA型号、CANN缺口保留；Windows投影与真人计时未验证。
