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

|8|9|NPU与本机验收|4|30|7|

|9|7|结果与边界|1|30|QA|

主讲P1–P7共300秒；B1/B2共60秒；每人90秒。QA90秒、换人总30秒另计；合计480秒（8分钟）的计划，不是实测。

B1指run→coverage→summary与stats；B2指历史NPU效率图/coverage→本机真实截图→stdout/JUnit 77/77→相对视频备用链接。材料小字可用放大/备注备查，关键结论由20pt标签和18pt表承担。

B1：`python -m json.tool reports/stage3-main/run.json`——只读查看已保存pilot运行快照，非现场推理。本轮未执行。
B2：`bash reports/local-verification/recheck.sh`——仓库根目录、已准备数据后离线复查；非新推理，本build未执行。


## v5 本轮补充核验
仅更改视觉表达与图表指认，原数据变化为0；不新增推理/API。P1/P2/P7保留结论横幅，P3/P4/P5/P6/P8/P9改局部证据表达。
P5七方法可编辑点图按原方法顺序，EM轴0–100；仅右侧两条真实问题级配对CI，跨0不证明等效，Long4x18/500超预算。
P6以NPU full82.6为配对参照；ablation.csv与analyze_stage4.py L54–71证明CI来自paired_comparisons，full无CI、original外部参照、no_recovery为已有回答派生。右侧独立效率total_pipeline_seconds_p50/p95是分位点，非CI；没有端到端加速。
P9保留原效率图，阶段中位数不能相加为E2E。P8只查看已有pilot快照：`python -m json.tool reports/stage3-main/run.json`。P9保留`bash reports/local-verification/recheck.sh`，本轮两命令均未执行。
作图原值/线性映射见sources/g2/v5-chart-data-and-mapping.json，独立坐标核对见chart-source-audit-v5.json。历史输出缓存、CUDA型号、CANN缺口保留；Windows投影与真人计时未验证。


## v6 本机证据更新（2026-11-21，Asia/Shanghai）
默认演讲次序1,2,3,4,5,8,6,9,7，不改变物理页序；主讲P1–P7=300秒，P8/P9静态证据各30秒=60秒，总360秒。成员1=25+35+30=90秒；成员2=45+45=90秒；成员3=P5 60+P8 30=90秒；成员4=P6 60+P9 30=90秒。均为预算，真人讲述计时未完成。
历史CUDA与历史NPU及2026-11-21本机CPU/离线验收严格分批；本机Python3.13.5/tokenizers0.22.1不能替代历史NPU Python3.12.0/tokenizers0.21.4。此次不推理、不加载权重、不调用问答API，已发表分数不变。
本机77/77依据reports/local-verification/pytest-full.stdout中77 passed in3.53s与junit-full.xml的77项、零失败/错误/跳过；不是凭截图77 items标题推断。真实截图显示进度100%及脚本exit0。tokenizer和50秒实录已解决；videoReview已核验连续进度100%+exit0且无秘密（依用户交接）。
可选方案（非默认）：50秒视频替换原60秒证据段，不另加。按原P8/P9两个30秒窗口各播放连续25秒：成员3先5秒引入+前25秒旁白，成员4后25秒旁白+5秒收尾，两人都发声，仍各90秒；P8/P9静态画面备用。若不适合边播边讲，保持默认静态，不挤掉成员3/4发言。文件相对链接evidence/local-offline-evidence.mp4，不嵌PPT、不自动播放。
缺口保留：stage2/3/4完整results.jsonl、压缩/问答缓存及sha256，CUDA具体型号、阶段4 CANN、受控Cursor结果、P号/四人登记。Windows/投影未验；本人贡献与本人确认未完成，不替本人填写或认领。
