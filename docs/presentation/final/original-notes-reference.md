# 物理第1页 原资料（旧口播已被v3讲稿替代）
【口播 25 秒】
我们复现 LongLLMLingua。原论文图中从原始提示，经问题感知压缩，再交给问答模型，是本组比较的方法链。课程固定一百题、五个位置，问答用 DeepSeek 替换历史 GPT。因此我们做方法级复现，不把本组分数与论文绝对数值横比。

【交付使用提示，不口播】
本地显式字体：Noto Sans CJK SC（中文/正文）、Inconsolata（英文摘录）；主题同为 Noto Sans CJK SC。Windows PowerPoint 显示、字体替换与放映仍需本人确认；未在 Windows 验证。

【事实/方法设置，不口播】
来源是本轮用户提供的本地导出材料，不宣称重新执行实验。
本地：sources/docs/presentation/members/member1/report-draft.md §1–3；sources/docs/presentation/01-number-registry.md。
论文：https://arxiv.org/abs/2310.06839
官方压缩代码：https://github.com/microsoft/LLMLingua/tree/5a4c78ae18ab17a98cf997e8259354e546081d64
上游数据与模板：https://github.com/nelson-liu/lost-in-the-middle/tree/29b8a6d042ce29abccee3db1a73171a107d7e6af
复现项目：https://github.com/SPikerinbit/longllmlingua-reproduction
用户给定 stage1-foundation 提交：183cf488db1d2e5b79a37f28e2120cea2ce2ae27（前序 fix 已只读读取锁定提交；finish 未访问远端）。
课程范围 pilot100题×5位置；seed42；20/100/500为嵌套题单；500题是扩展清单，不表明500题已完成。问答deepseek-flash，temperature0，max_tokens512，非思考。原论文GPT-3.5-Turbo-0613已被替换，因此只作本组方法比较。返回fingerprint不是模型快照的证明。
输入—压缩—问答图是任务关系示意，不是本人实现LongLLMLingua的声明。
Cursor独立对话基线尚无新数据，页上和备注中的旧DeepSeek数字不得改名。

【本次真实素材核验】PDF第一页明确arXiv:2310.06839v2 [cs.CL] 12 Aug 2024；题目LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression；作者Huiqiang Jiang, Qianhui Wu, Xufang Luo, Dongsheng Li, Chin-Yew Lin, Yuqing Yang, Lili Qiu；ACL 2024 Long Papers pp.1658–1677。Figure 2，PDF第3页，caption Framework of LongLLMLingua. Gray Italic content: As in LLMLingua. 原图裁出，未重绘、未改图内模型标志。图内GPT等为原论文设置，本组问答用DeepSeek。公开PDF：https://arxiv.org/pdf/2310.06839v2；会议目录：https://aclanthology.org/2024.acl-long.91/ 。完整图题：Framework of LongLLMLingua；主论文完整英文标题如上。图中文字作为引用原材料保留原字号，图外中文说明20pt。

# 物理第2页 原资料（旧口播已被v3讲稿替代）
【口播 35 秒】
左边是真实固定样本：四倍压缩后，没有保住可评分的答案名。右表是二十题 smoke，原始、BM25 两倍、四倍的 EM 为九十二、八十七、六十四。三百槽全部成功，不是三百道独立题。新离线审计重评分不一致和预算违规都为零，没有新增 API 推理；主指标仍用首行子串匹配。

【事实/评分与验收，不口播】
本地：sources/docs/presentation/01-number-registry.md「阶段一smoke」；member1/report-draft.md §2–3；member1/qa.md Q3/Q8/Q9；member1/cases.md M1-03。
可追溯项目路径：https://github.com/SPikerinbit/longllmlingua-reproduction/tree/main/reports/stage1-acceptance
登记表路径：https://github.com/SPikerinbit/longllmlingua-reproduction/blob/main/docs/presentation/01-number-registry.md
run d54b3118c61ea4930624；acceptance.json success300/failed0/missing0。20题×5位置×3方法；每方法100槽。原始92.0%、BM25_2x87.0%、BM25_4x64.0%；实测1.000x/2.001x/4.007x。来源为用户导出的既有DeepSeek记录，前序 fix 已只读核对预测与样本，finish 仅复核本地材料、未逐槽重放 API。
五个绿色位置同时显示是五份输入变体的概念示意；每一份输入只有一篇gold文档。不能据此声称显著位置效应。
首行best_subspan_em：归一化后任一参考答案作为首行子串出现则记1；不是严格整句完全匹配或人工语义判分，否定句提及答案也可能得分。answers/gold/位置不传给BM25或QA；不把代码设计说成已逐条人工检查所有完整提示。
BM25工程设定：BM25Okapi，k1=1.5,b=0.75，Unicode词法casefold；选文档后恢复原顺序，最后篇可词前缀截断。完整提示硬预算floor(original_tokens/2或4)。这些是小组固定工程选择，不称为论文等价实现。
主比较original84.6%来自100题500槽，和20题100槽的92.0%分母不同，不解释为模型退步。

【本次真实样本/记录核验】通过内置GitHub只读工具读取锁定提交的manifests/smoke.json及reports/stage1-acceptance/predictions.jsonl。样本ID ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc 位于smoke题单。问题/参考答案来自本地cases.md先前按上游gz sha256对齐的M1-01。图上ID仅省略显示，完整ID在此。位置1原始、BM25_2x、BM25_4x score=1/1/0，tokens=3289/1644/822。摘录用省略号保留原句中的选段，不伪装终端执行。源URL：https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/reports/stage1-acceptance/predictions.jsonl 与 https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/manifests/smoke.json 。新审计报告sources/verified/stage1-audit.json：prediction_rows300，rescore.mismatches[]，budget.violations[]，api_calls0；没有新推理。审计说明局限：没有组内完整提示，不能重跑accept_stage1.py，诊断正则非300槽人工语义复核。口头给定36测试通过另一路提供，JSON未列测试数，本页未写36。强否认仍得1有4槽，首行0拼行1有2槽，仅作诊断，不更换主指标。五位置为1/5/10/15/20，每题20篇，不能据此说位置效应显著。

【finish canonical 来源闭环，不口播】
本次通过内置GitHub只读工具核对stage1-foundation，检查时分支头为5788cc2d4aab75501b390dcfb9553df5bf086d71。predictions、acceptance、smoke题单与stage1配置在该头与锁定提交183cf488db1d2e5b79a37f28e2120cea2ce2ae27的Git blob均相同。实际引用来源为sources/canonical-stage1/predictions.jsonl，其SHA256=cac37c9e84678f2f591af8c4f6ccdb7a69d010cf71eae5678b85109bcb27bd62，342167字节，Git blob=1b83a71924e015a1fff3354cdd21958d2ee5722e。已逐条核对300条全部JSON字段及17项关键字段，300/300一致；20题×5位置×3方法与smoke题单、配置完全覆盖，run为d54b3118c61ea4930624。canonical offline-audit与所给审计JSON对象一致，记录的预测SHA256也完全吻合。原验收记录local_acceptance_passed=true、peer_review_pending=true；本轮是来源核验，不是重跑验收/推理，不宣称完成同伴评审。原导出差异已验证闭环，详见独立canonical核查报告。
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/reports/stage1-acceptance/predictions.jsonl
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/reports/stage1-acceptance/acceptance.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/manifests/smoke.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/configs/stage1.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/5788cc2d4aab75501b390dcfb9553df5bf086d71/reports/stage1-supplement/offline-audit.json

# 物理第3页 原资料（旧口播已被v3讲稿替代）
成员二P3｜45秒。左侧只保留论文Fig.2的方法列，避免重复P1完整框架。右上是compression.py真实选行，不是伪代码，行号按固定commit原文件。176行把question传给压缩器；179和187分别是文档筛选开关与排名方法，映射原图I；185是动态比率，186是细粒度条件对比，映射II。本次配置为Long排名、0.3、条件对比开启。主比较保持original顺序，恢复在问答之后；这是一套官方算法的适配调用，不是本组原创。REPORT与canonical验收记录100/100槽保留文档不同于LLMLingua。k=2映射已查明在当前路径无效，τ_ins与τ_que没有实现；代码历史注释有“近似”说法但后续参数映射核验已否定其有效性，不能照旧注释夸等价。恢复分词器使用DeepSeek而非原论文LLaMA。

图注：LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression. Jiang et al. ACL 2024 Long Papers, pp.1658–1677, Figure 2, p3。原图仅裁取方法列，未重绘算法。https://aclanthology.org/2024.acl-long.91/
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/reproduction/compression.py#L176-L187
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/docs/stage2-parameter-map.md
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/reports/stage2-smoke/REPORT.md
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/reports/smoke-stage2-acceptance.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/run.json

# 物理第4页 原资料（旧口播已被v3讲稿替代）
成员二P4｜45秒。先看左上canonical原始JSON摘录：accepted_run指a1bd26fe3d82dea3f65d、400槽、hard预算、396满足、passed为true。passed指验收要求通过，不是400条预算都满足。右上是verification里第一个budget_miss的完整原对象，保留完整slot_id；右下把四条记录原值排成可读表，同一题Long4x，位置1/5/10/15，目标742，实测749/751/754/753。我们掌握逐槽异常记录，但没有取得原始results.jsonl和完整attempts，因此不推断四条超标原因、不隐藏、不改分。它不是兼容stage_3的394副本。固定20文档、gold五位置1/5/10/15/20、seed42；smoke20⊂pilot100⊂main500。七方法共用deepseek-flash、temperature0、max_tokens512、首行best_subspan_em与DeepSeek tokenizer；换了原论文GPT及恢复分词器，只能叫方法级复现。CUDA主比较Long4x另有18/500超预算，不和smoke混算。

两处JSON都是字段选择/原对象排版，不是终端或本次新执行输出。左侧从canonical对象选取5个键，accepted_run仅改变JSON空白换行；右侧完整budget_misses[0]，下表逐项来自[0:4]，无推断原因。
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/reports/smoke-stage2-acceptance.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/reports/stage2-smoke/verification.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/docs/stage2-parameter-map.md
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/run.json

# 物理第5页 原资料（旧口播已被v3讲稿替代）
成员三P5主讲60秒，B1证据30秒，共90秒。先看七方法表，每行同为100题五位置共500槽，合计3500槽不是3500独立题。原提示84.6；BM25 2x72.4、4x55.8；LLMLingua 2x46.8、4x35.6；Long2x83.2、4x79.0。Long2x保持较高EM，但相对original低1.4个百分点，右上问题级配对bootstrap95%区间[-6.2,+3.0]跨零，不证明等效。Long4x区间[-11.6,-0.4]不跨零，且18/500超预算，不声称严格同预算。右下是五位置原值，每格100题，变化不大，不能冒称复现U形。主比较只有cuda:0，无GPU型号；不混用NPU消融或效率。下面切B1指历史run、coverage和0.832。

逐图/逐片段来源（固定提交）：
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/summary.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/stats.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/coverage.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/run.json

# 物理第6页 原资料（旧口播已被v3讲稿替代）
成员四P6主讲60秒，B2证据30秒，共90秒。左图为仓库原始ablation.png，真实NPU消融，3500成功槽；原始7方法运行不含no_recovery重新推理，该行由已有回答恢复前评分派生，各展示行500槽。完整Long2x82.6不是CUDA的83.2；去粗粒度45.0，相对完整低37.6pp，95%CI[-47.2,-28.4]；去动态78.0，低4.6pp，区间[-8.6,-0.8]。重排是在主配置original的基础上额外开启，不能叫移除重排。右表是另一独立NPU效率run，20题五位置12方法1200槽，对共同question+position去同一个首样本后99/方法。Long2x端到端p50/p95为6.45/7.49秒，original1.12/1.54秒：该设置没有端到端加速，不用token减少替代速度。不把阶段耗时中位数相加冒充端到端中位数。恢复也不是必然改善；来源记录有3个1→0槽，全文及ID在备注来源中，不伪造新输出。

逐图/逐片段来源（固定提交）：
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/RESULTS.md
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/ablation.csv
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/efficiency.csv
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/figures/ablation.png
原图为仓库提交的PNG，按原像素无损封装成DrawingML矢量路径，保持原标签、颜色、几何，不另造曲线；目的为保持现有rels与其他页面完全不变。

# 物理第7页 原资料（旧口播已被v3讲稿替代）
【口播 30 秒】
一百题 CUDA 主比较里，两倍低一点四个百分点，区间跨零，但不证明等效。另一批 NPU 记录中，压缩也没有带来端到端提速。下面的真实预测否认能回答，却提到 Los Lonely Boys，子串仍记一分。所以结果必须连同压缩代价、环境和评分边界一起读。

【事实/环境隔离，不口播】
主表来自全组已导出number-registry「阶段三主比较」，不是成员一smoke，也不表示本人对其他成员结果作了逐条独立核验。
主比较：https://github.com/SPikerinbit/longllmlingua-reproduction/tree/main/reports/stage3-main
run e8f151b9c286648caf98；100题×5位置×7方法=3500槽；设备仅记录cuda:0，无可核验GPU型号。表中original84.6%，Long2x83.2%，Long4x79.0%；实际压缩比分别1.00x/2.08x/4.09x。差值−1.4pp/−5.6pp；问题级配对bootstrap2000次、seed42，95%区间2x[−6.2,+3.0]pp，4x[−11.6,−0.4]pp。区间跨0不证明等效、不证明无差异。4x硬预算满足率0.964，18/500槽超预算，不将成功槽等同于预算合格槽。
效率是另一批smoke：run 2a7f4accf6127178a76b；number-registry「阶段四效率」记录每方法n=99，位置19/20/20/20/20。环境为Ascend910B4/NPU，与CUDA主比较不同。原始端到端p50=1.120468680979684s，Long2x=6.449125320883468s；仅按登记表舍入1.12/6.45。缓存读取时间不当作模型生成耗时。不能合并或横比两台机器的绝对耗时，阶段中位数也不能直接相加。
贡献只陈述本人阶段一：数据与嵌套题单、模板、缓存、original/BM25、评分与300槽验收。压缩算法来自官方锁定代码，其他成员的个人贡献/姓名不代为核验或虚构。
效率来源路径需结合导出登记表的run与efficiency.csv定位；本轮未调用远程仓库或复跑。Cursor新基线尚无数据，未添加任何新结果。

【评分边界原始记录核验】完整slot_id=64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:10:bm25_4x，model deepseek-flash，score1.0；问题who sang the song how far is heaven，参考Los Lonely Boys（本地已对齐cases M1-03）。图上两段是不连续原文选段，省略号显式表示删节，没有改写被引词串。完整原始首行：Based on the provided search results, none of the documents contain information about a song titled "How Far Is Heaven." The results mention songs such as "If Heaven Wasn't So Far Away," "Heaven" by Los Lonely Boys, "The Nearest Thing to Heaven," and "Over the Hills and Far Away," but none of these match the song in your question. Therefore, the search results do not provide an answer.
源URL：https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/reports/stage1-acceptance/predictions.jsonl 。新离线审计同样列出此槽，4条强否认仍得1并非重新定义官方EM。本人没有宣称替其他成员个人核验，CUDA与NPU仅按全组登记表引用。

# 物理第8页 原资料（旧口播已被v3讲稿替代）
成员三B1证据30秒，接P5主讲60秒，共90秒。本页都是已提交文件字段，不是本次新终端。左上run_id和pilot、seed42、五位置、DeepSeek配置锁定运行；右上coverage记录100题、3500成功、无失败缺失，3500是100×5×7槽。右下summary把method=longllmlingua_2x和500槽的mean_em0.832放在同一个真实对象字段摘录里，不是3500题平均。左下stats的配对差值与区间来自相同pilot产物，问题级2000次重采样。底部plan仅检查矩阵；若真实重跑改为run且需数据、原权重和API密钥。本轮都未执行。CUDA型号和原始results.jsonl未取得，不用summary代全文，不拿会话墙钟当API延迟。

字段摘录说明：run/config/coverage/summary均只选择真实键保留真实值，不宣称完整对象逐字连续。运行配置导出副本在sources/g1/configs/stage3-pilot-as-run.json，源对象run.config；JSON格式化字节不等于历史config_hash，不能混淆。将该文件放入原仓库configs后可执行：
python -m reproduction.stage3 --config configs/stage3-pilot-as-run.json plan
python -m reproduction.stage3 --config configs/stage3-pilot-as-run.json run
默认configs/stage3.json为main，不能误用。原数据/模型revision见run，权重与密钥需本人准备；本轮未执行这两条。
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/run.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/coverage.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/summary.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/stats.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reproduction/stage3.py#L780-L800

# 物理第9页 原资料（旧口播已被v3讲稿替代）
成员四B2证据30秒。左侧是已提交efficiency.png原图，显示压缩/问答/恢复各阶段中位数，图自身也说明各中位数之和不是端到端延迟；真正E2E看P6表中total_pipeline_seconds。右侧两次run_id与coverage对应消融3500、效率1200。环境原件只写Ascend910B4、torch2.7.1、torch_npu2.7.1.post2，没有CANN版本，不能补写；tokenizers环境文件0.21.4与另份0.21.0记录不能合并。底部命令从已存metrics重建表，--out写临时审计目录避免覆盖源汇总；本轮仅阅读源码和记录，没有执行命令，没有推理或API新分数。缺完整输出缓存和其sha256；轻量metrics不是原始回答全文。

逐图/逐片段来源（固定提交）：
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/coverage.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/inputs/ablation-run.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/inputs/efficiency-run.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/environment/environment-current.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/figures/efficiency.png
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/inputs/recovery-cases.json
原图为仓库提交的PNG，按原像素无损封装成DrawingML矢量路径，保持原标签、颜色、几何，不另造曲线；目的为保持现有rels与其他页面完全不变。

真实恢复负面案例原文：
{
  "question_id": "a1bc042605bbfadedc64e1ddb4d9ba81f26af53c062b4d860005b97a93bd9773",
  "position": 5,
  "question": "how many cracker barrels in the united states",
  "before_score": 1.0,
  "after_score": 0.0,
  "before_first_line": "Based on the search results, Cracker Barrel operates 645 stores in 4 states (Document 2), or 639 stores in 43 states as of September 18, 2012 (Document 5).",
  "after_first_line": "Based on the search results, Cracker Barrel operates 645 stores in 44 states. Cracker Barrel's menu is based on traditional Southern cuisine, with"
}

命令源码：https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/scripts/analyze_stage4.py；该脚本离线读取inputs/metrics.jsonl，会写csv等，因此本页使用--out新目录。