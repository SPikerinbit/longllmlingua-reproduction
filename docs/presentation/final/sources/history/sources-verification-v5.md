# v5补正（当前有效）

B1命令纠正为`python -m json.tool reports/stage3-main/run.json`，用于查看已保存pilot运行快照；不是新实验、不是计划生成或推理复现。依据用户本轮仓库侧交叉核验及既有run.json源链，未进行新的远端研究。v3已被替代；以下历史核验中“页面文字完全不变”仅指上一轮v3，v5仅改B1命令、阅读标签及对应资料。B2离线分析命令保持临时out，未执行。

# G14 LongLLMLingua v5｜素材来源与核验报告

本轮仅本地finish，无新增页、无推理、无API、无远端上传。9页已逐页渲染亲看；按已认可前三页证据标准复核密度、层次、证据可读、结论对应和图注，而非只看无重叠。

## fixed

- P4：四槽表行高及内边距收紧，保持18pt和全部原数，末行不再挨结论。

- B1：两段JSON行距及上下内边距修正，闭括号纳入容器，不降字号。

- P1–P9：合并备注、四人分段稿、QA与跳转路线；九个短标题保持不变。

## left

本轮只编辑和核对已有材料，没有新推理、新API或Cursor受控对话成绩。CUDA主比较与NPU消融/效率为独立批次。stage1 92/87/64不与CUDA pilot100混用；stage2 canonical396/400，四异常原因不推断，旧394不是现值。Long2x区间跨0非等效；Long4x18/500超预算。NPU p50 1.12对6.45秒不构成端到端加速。缺CUDA型号、CANN版本、stage2/3/4完整results或输出缓存及其校验和；stage1 canonical预测已有核验，不能把缺口泛化到stage1。Windows/投影、真人计时和录屏未验证，个人贡献与亲历未经替本人确认。

## 素材源链（沿用本地已锁定资料；本轮未重新取远端）

### sources/verified-member1-sources.md

# 修订成品素材来源

P2/P7预测与验收最终均引用已验证canonical源；旧导出仅缺末尾LF，证据链已闭环，详见同前缀Canonical核查报告。主表数字不变，无新推理。

【finish canonical 来源闭环，不口播】
本次通过内置GitHub只读工具核对stage1-foundation，检查时分支头为5788cc2d4aab75501b390dcfb9553df5bf086d71。predictions、acceptance、smoke题单与stage1配置在该头与锁定提交183cf488db1d2e5b79a37f28e2120cea2ce2ae27的Git blob均相同。实际引用来源为sources/canonical-stage1/predictions.jsonl，其SHA256=cac37c9e84678f2f591af8c4f6ccdb7a69d010cf71eae5678b85109bcb27bd62，342167字节，Git blob=1b83a71924e015a1fff3354cdd21958d2ee5722e。已逐条核对300条全部JSON字段及17项关键字段，300/300一致；20题×5位置×3方法与smoke题单、配置完全覆盖，run为d54b3118c61ea4930624。canonical offline-audit与所给审计JSON对象一致，记录的预测SHA256也完全吻合。原验收记录local_acceptance_passed=true、peer_review_pending=true；本轮是来源核验，不是重跑验收/推理，不宣称完成同伴评审。原导出差异已验证闭环，详见独立canonical核查报告。
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/reports/stage1-acceptance/predictions.jsonl
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/reports/stage1-acceptance/acceptance.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/manifests/smoke.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/configs/stage1.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/5788cc2d4aab75501b390dcfb9553df5bf086d71/reports/stage1-supplement/offline-audit.json

【本次真实素材核验】PDF第一页明确arXiv:2310.06839v2 [cs.CL] 12 Aug 2024；题目LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression；作者Huiqiang Jiang, Qianhui Wu, Xufang Luo, Dongsheng Li, Chin-Yew Lin, Yuqing Yang, Lili Qiu；ACL 2024 Long Papers pp.1658–1677。Figure 2，PDF第3页，caption Framework of LongLLMLingua. Gray Italic content: As in LLMLingua. 原图裁出，未重绘、未改图内模型标志。图内GPT等为原论文设置，本组问答用DeepSeek。公开PDF：https://arxiv.org/pdf/2310.06839v2；会议目录：https://aclanthology.org/2024.acl-long.91/ 。完整图题：Framework of LongLLMLingua；主论文完整英文标题如上。图中文字作为引用原材料保留原字号，图外中文说明20pt。

【本次真实样本/记录核验】通过内置GitHub只读工具读取锁定提交的manifests/smoke.json及reports/stage1-acceptance/predictions.jsonl。样本ID ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc 位于smoke题单。问题/参考答案来自本地cases.md先前按上游gz sha256对齐的M1-01。图上ID仅省略显示，完整ID在此。位置1原始、BM25_2x、BM25_4x score=1/1/0，tokens=3289/1644/822。摘录用省略号保留原句中的选段，不伪装终端执行。源URL：https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/reports/stage1-acceptance/predictions.jsonl 与 https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/manifests/smoke.json 。新审计报告sources/verified/stage1-audit.json：prediction_rows300，rescore.mismatches[]，budget.violations[]，api_calls0；没有新推理。审计说明局限：没有组内完整提示，不能重跑accept_stage1.py，诊断正则非300槽人工语义复核。口头给定36测试通过另一路提供，JSON未列测试数，本页未写36。强否认仍得1有4槽，首行0拼行1有2槽，仅作诊断，不更换主指标。五位置为1/5/10/15/20，每题20篇，不能据此说位置效应显著。

【评分边界原始记录核验】完整slot_id=64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:10:bm25_4x，model deepseek-flash，score1.0；问题who sang the song how far is heaven，参考Los Lonely Boys（本地已对齐cases M1-03）。图上两段是不连续原文选段，省略号显式表示删节，没有改写被引词串。完整原始首行：Based on the provided search results, none of the documents contain information about a song titled "How Far Is Heaven." The results mention songs such as "If Heaven Wasn't So Far Away," "Heaven" by Los Lonely Boys, "The Nearest Thing to Heaven," and "Over the Hills and Far Away," but none of these match the song in your question. Therefore, the search results do not provide an answer.
源URL：https://github.com/SPikerinbit/longllmlingua-reproduction/blob/183cf488db1d2e5b79a37f28e2120cea2ce2ae27/reports/stage1-acceptance/predictions.jsonl 。新离线审计同样列出此槽，4条强否认仍得1并非重新定义官方EM。本人没有宣称替其他成员个人核验，CUDA与NPU仅按全组登记表引用。

CUDA主比较/NPU另一批效率仍按 sources/docs/presentation/01-number-registry.md 引用；口径及run详见讲稿。Windows显示未确认，未真人计时。


### notes/g1-fix.md

# g1 fix
只修P3/P4/B1及三页备注；未改其他6页或rels。

成员二P3｜45秒。左侧只保留论文Fig.2的方法列，避免重复P1完整框架。右上是compression.py真实选行，不是伪代码，行号按固定commit原文件。176行把question传给压缩器；179和187分别是文档筛选开关与排名方法，映射原图I；185是动态比率，186是细粒度条件对比，映射II。本次配置为Long排名、0.3、条件对比开启。主比较保持original顺序，恢复在问答之后；这是一套官方算法的适配调用，不是本组原创。REPORT与canonical验收记录100/100槽保留文档不同于LLMLingua。k=2映射已查明在当前路径无效，τ_ins与τ_que没有实现；代码历史注释有“近似”说法但后续参数映射核验已否定其有效性，不能照旧注释夸等价。恢复分词器使用DeepSeek而非原论文LLaMA。

成员二P4｜45秒。先看左上canonical原始JSON摘录：accepted_run指a1bd26fe3d82dea3f65d、400槽、hard预算、396满足、passed为true。passed指验收要求通过，不是400条预算都满足。右上是verification里第一个budget_miss的完整原对象，保留完整slot_id；右下把四条记录原值排成可读表，同一题Long4x，位置1/5/10/15，目标742，实测749/751/754/753。我们掌握逐槽异常记录，但没有取得原始results.jsonl和完整attempts，因此不推断四条超标原因、不隐藏、不改分。它不是兼容stage_3的394副本。固定20文档、gold五位置1/5/10/15/20、seed42；smoke20⊂pilot100⊂main500。七方法共用deepseek-flash、temperature0、max_tokens512、首行best_subspan_em与DeepSeek tokenizer；换了原论文GPT及恢复分词器，只能叫方法级复现。CUDA主比较Long4x另有18/500超预算，不和smoke混算。

成员三B1证据30秒，接P5主讲60秒，共90秒。本页都是已提交文件字段，不是本次新终端。左上run_id和pilot、seed42、五位置、DeepSeek配置锁定运行；右上coverage记录100题、3500成功、无失败缺失，3500是100×5×7槽。右下summary把method=longllmlingua_2x和500槽的mean_em0.832放在同一个真实对象字段摘录里，不是3500题平均。左下stats的配对差值与区间来自相同pilot产物，问题级2000次重采样。底部命令只读查看已保存pilot运行快照，不是推理或计划生成，本轮未执行。CUDA型号和原始results.jsonl未取得，不用summary代全文，不拿会话墙钟当API延迟。

https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/reproduction/compression.py#L176-L187
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/reports/smoke-stage2-acceptance.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/reports/stage2-smoke/verification.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/run.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/coverage.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/summary.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/stats.json

## 当前标题
压缩方法 / 预算验收 / CUDA运行记录。全组标题目录见final-titles.md。最终逐项fixed/left见six-page-quality-audit.md。已亲看全组标题与三页证据布局；修掉源码和JSON容器溢出。


### notes/g2.md

# g2 build｜P5/P6/B2
仅编辑slide6.xml、slide7.xml、slide9.xml及其原有备注。不改其他6页或任何rels。

成员三P5主讲60秒，B1证据30秒，共90秒。先看七方法表，每行同为100题五位置共500槽，合计3500槽不是3500独立题。原提示84.6；BM25 2x72.4、4x55.8；LLMLingua 2x46.8、4x35.6；Long2x83.2、4x79.0。Long2x保持较高EM，但相对original低1.4个百分点，右上问题级配对bootstrap95%区间[-6.2,+3.0]跨零，不证明等效。Long4x区间[-11.6,-0.4]不跨零，且18/500超预算，不声称严格同预算。右下是五位置原值，每格100题，变化不大，不能冒称复现U形。主比较只有cuda:0，无GPU型号；不混用NPU消融或效率。下面切B1指历史run、coverage和0.832。

成员四P6主讲60秒，B2证据30秒，共90秒。左图为仓库原始ablation.png，真实NPU消融，3500成功槽；原始7方法运行不含no_recovery重新推理，该行由已有回答恢复前评分派生，各展示行500槽。完整Long2x82.6不是CUDA的83.2；去粗粒度45.0，相对完整低37.6pp，95%CI[-47.2,-28.4]；去动态78.0，低4.6pp，区间[-8.6,-0.8]。重排是在主配置original的基础上额外开启，不能叫移除重排。右表是另一独立NPU效率run，20题五位置12方法1200槽，对共同question+position去同一个首样本后99/方法。Long2x端到端p50/p95为6.45/7.49秒，original1.12/1.54秒：该设置没有端到端加速，不用token减少替代速度。不把阶段耗时中位数相加冒充端到端中位数。恢复也不是必然改善；来源记录有3个1→0槽，全文及ID在备注来源中，不伪造新输出。

成员四B2证据30秒。左侧是已提交efficiency.png原图，显示压缩/问答/恢复各阶段中位数，图自身也说明各中位数之和不是端到端延迟；真正E2E看P6表中total_pipeline_seconds。右侧两次run_id与coverage对应消融3500、效率1200。环境原件只写Ascend910B4、torch2.7.1、torch_npu2.7.1.post2，没有CANN版本，不能补写；tokenizers环境文件0.21.4与另份0.21.0记录不能合并。底部命令从已存metrics重建表，--out写临时审计目录避免覆盖源汇总；本轮仅阅读源码和记录，没有执行命令，没有推理或API新分数。缺完整输出缓存和其sha256；轻量metrics不是原始回答全文。

## 逐图来源
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/RESULTS.md
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/ablation.csv
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/efficiency.csv
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/coverage.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/inputs/ablation-run.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/inputs/efficiency-run.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/environment/environment-current.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/figures/ablation.png
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/figures/efficiency.png
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency/inputs/recovery-cases.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/summary.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/stats.json
https://github.com/SPikerinbit/longllmlingua-reproduction/blob/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/scripts/analyze_stage4.py

原PNG无损DrawingML封装；P6另设82.6/45.0/78.0大字阅读标签，对应完整/去粗粒度/去动态行。，保留来源标签、颜色与几何；与原图逐一核对，非重绘数值或模拟终端。

## 最终检查
已亲自打开verified三页与延河一号06/13/22/23并对照六页。详见notes/six-page-quality-audit.md。本组P5/P6/B2逐页看渲染并修正区间标题/行间距及原图关键值阅读标签。OOXML通过、check-overlap无发现、字体齐全；其他6页XML及rels保持字节一致，组内rels也未改。g1具体待修未跨阶段修改。


## 本地文件校验

以下仅为当前本地素材副本的SHA256，不冒充未取得的原始输出包或缓存校验和。

8b6f420d19fa4928fc2607ccb9f31e677d943153a6e1d0eaf3c6c6a8d892ef30  sources/acceptance-matrix.md

ff0f76de6d5805961e943a72c694d7ef9c374ccd03b5687554956d5c5d0b1ad2  sources/canonical-stage1/acceptance.json

cb82a0de26abc42fa31d9cf404354e2649d4e94819668784c79be9418ced612f  sources/canonical-stage1/offline-audit.json

cac37c9e84678f2f591af8c4f6ccdb7a69d010cf71eae5678b85109bcb27bd62  sources/canonical-stage1/predictions.jsonl

19adc9f2419d458733ceda7fe903f375a5f7f449d37ae037a7ae77048320ffc7  sources/canonical-stage1/smoke.json

0ff822600fa12ce031d05732ca5adc903425f3867a8fc6ea015426d201488355  sources/canonical-stage1/source-refs.json

45870fb32fc3d603a0fd9408a33e6a2dfdefe64c5dd876b2240893fc162d5dd6  sources/canonical-stage1/stage1.json

698a137171c7d19a4c1160b666eb2c7070ed0dab15a6e792648228800f5ccce3  sources/contributions.md

a69dbfbd9ec95fd9536ac53c98c9bbcea7dae1276be91a3d2e6bf4d702ca83ec  sources/data/README.md

46b1407d0a20db6a7a3046a8e369086ca04a11f87c20859d3fccd795681a50d5  sources/docs/presentation/00-division-of-labor.md

c12fce7551765680bab457f2dd791bbe3827cc89142c5e79b3ff282cbd056d71  sources/docs/presentation/01-number-registry.md

94c584a37ef6ef0cd309f86489f3e4764639686cb84b3a3386233218c22c3ad2  sources/docs/presentation/README.md

fd6df740a6b279e1a08d863e1427d699938e192804d65acfeebeac02bd1eea36  sources/docs/presentation/members/member1/cases.md

2a0a4e557abb32545bcdd49daa1b6a168acfcfe7c6d9904e79acd804510264b2  sources/docs/presentation/members/member1/previews/slide-1.png

ca375ff5c86b6eb0287b2e6e681b8f99c6dc57e7f9fac79f9dd40bccd8bd91f2  sources/docs/presentation/members/member1/previews/slide-2.png

01da4b86570291cad93e7283f92f70d19c3ebd9a8a96d7edb3eea41fa63a09ee  sources/docs/presentation/members/member1/previews/slide-3.png

d5aee5caa0dccbc87d88bfc8a67d21e76618fefa2ce2439a85b8c4a84258b30d  sources/docs/presentation/members/member1/previews/slides-P1-P2-P7.pdf

d8ef0c69dae61fb0960e352e8e63c4563f4e00ada12fb9063dd313dbc2fc2b50  sources/docs/presentation/members/member1/qa.md

bfe9bad948c2b55fdb581b33e77df5f41449d96e59aa39450882710dec347069  sources/docs/presentation/members/member1/report-draft.md

8465a575033799a3ea2bb6d01ad2a11b9e4ba5bbfe7f865c3e7d231a7eeb2b3e  sources/docs/presentation/members/member1/script.md

c95602aef235c517f5b7605cbc5c3eb5d316251848cf5adb36fc5496938f2c2e  sources/docs/presentation/members/member1/self-check.md

bc3ab48143029ef7bf6792fb103cab6f6213b741685c2774316299c7351f7c72  sources/docs/presentation/members/member1/slides-P1-P2-P7.pptx

9edf18162cd0f6f58436f18483520974d7686c829648420a4f2fdd8082679201  sources/docs/presentation/members/member1/task.md

b9cbb0e01d15f96aeb2e055879e87d3c12771d190d8499cfd8dd8f47659d25b5  sources/docs/presentation/members/member2/task.md

1dc680b4b50786e983440948ffc66138d33ac2ddc4a4529b7d65d16227be36c9  sources/docs/presentation/members/member3/task.md

dd7ba87052217039eb3fbfe70af4297a4aa76925b9ba436eca2af4dc2ebdc81a  sources/docs/presentation/members/member4/task.md

acab4692fba074f186cca905b53b0ca93c9fb377765cafc2369116ce9db634a1  sources/docs/presentation/slides/G14-LongLLMLingua-template.pptx

1f8353023cd05ced233d89df1504ac75e827c0cd12e841b626fc1a671ff300a8  sources/docs/presentation/slides/build_slides.py

fc71b17d7fdd1125cac9700ae6639563ac9deb6c6ed032a5038146e5b408b98a  sources/docs/presentation/slides/pptx-usage.md

c05be9c8c71651d0ac707ae7f7d556dea12ac949b0c75cf66a69295f143e7875  sources/docs/presentation/slides/previews/G14-LongLLMLingua-template.pdf

da959788ae79a15f264124a86b291b76de654d99a2a70ed5a9c9f487383d2027  sources/docs/presentation/slides/previews/template-1.png

b819f550878e35bede193d27366d9e98a75a889087fd68ab030f0ac97374f1f0  sources/docs/presentation/slides/previews/template-2.png

065fd900c83b21ddff9e909639aa1fa04900f38276c1b04ee30e10eac4cad4b6  sources/docs/presentation/slides/previews/template-3.png

618d421dd69e94ae03ca75b20abf89ffae325db78d3e9f69a2c71ef11a486b6e  sources/docs/presentation/slides/previews/template-4.png

f6a8c44be921d7b949fb6e272002638dabb0cbee31e575705b0b9e5b8f775aab  sources/docs/presentation/slides/previews/template-5.png

1591294a3f5bf6f98c43fd0a0d28408ce540beae1dd20ad40fc19f4260ab24be  sources/docs/presentation/slides/previews/template-6.png

556fa7f50f67916b61ccdac443323ac14d59272d474f72ab56dbc9ee8f86c861  sources/docs/presentation/slides/previews/template-7.png

3cb0eb23d5c37adf77bb015e7dae92bcf711f8ffdc928236b535a5b8be6d265d  sources/docs/presentation/slides/previews/template-8.png

f47aa7d55a5b09d0b0c69af3c4a06ee929ad3071e5a60edceaf30461b096c3f1  sources/docs/presentation/slides/previews/template-9.png

2330659724a3c4352e5bdb78fec854f912415b566c0d455c4574b7db4e6d83a8  sources/docs/presentation/templates/contributions.md

46947e181538ee85fa7ec274f6c2a3bb935ab386937076e9fd570d78916bdb27  sources/docs/presentation/templates/qa-card.md

25e0564dd15ea755509fe3596851d3e08f6beb4c3d94d86b756c1b52e7c1a6b7  sources/docs/presentation/templates/report-section.md

f15c335a09f196d0c5e60b97acc96ac8053d8bfaddb1d4553c3ed4273eb66d5d  sources/docs/presentation/templates/self-check.md

c0a36b2025e4541004abbd7eb90c3433db228bd40436a915ae89a7ddc287fd0f  sources/docs/presentation/templates/slide-page.md

7dc9d1df13bcea9ed0d9c504cf28122ea349ef3be70a340f3cf6be0d1fd2c988  sources/g1/REPORT-stage2.md

f60582980375114a606c87a6f3b2c8f6f484c44e0880b289e295312f4d28a77f  sources/g1/acceptance-stage2.json

c95e7d5d88144b7549ecf706884cb0d9de792011adfce3532d4dde8bbd8a04c1  sources/g1/compression.py

B1只读查看已保存pilot运行快照：`python -m json.tool reports/stage3-main/run.json`。不是推理复现命令；默认configs/stage3.json为main，不能代替pilot。

a95c030e8dd0c2758d2c7d8e1cd7856a1ba853b0bdab622e69b52065a1b1d029  sources/g1/coverage.json

dc70be7a39306986397ee88778212b60b43f592ea4e2dc43f352a602ce891843  sources/g1/parameter-map.md

433eb590541e62b4e402fc8d8d1c09570a5b26a7f533f150f7ea29ff03ef3ffd  sources/g1/run.json

ad34d1cb03ff6fb01b16518f266ed27172d0a2816d6b5fb3f877ebf709fbe563  sources/g1/stage3.py

435043bf6971bb3cd2bfbf2d1a26045b33378658453a82343ab411a27cef8a02  sources/g1/summary.json

095a6e9cc8c3d6b7194b05287088c8d438f3a038ad278a3d523f46770dc86db3  sources/g1/verification-stage2.json

7819b7ec7434d4459398a7d5beae8b73642e6ce00cb1d5fd985b50e4b2f68c0c  sources/g2/RESULTS.md

0b7c5f8c10a25ad569b73067d0f12c002c4591a705d3e048799db291b9cf5e71  sources/g2/ablation-run.json

d23b63dc6450bf6eecf4e00caa504f3a50ca19ce9516dee98dfc82fa9d6612d0  sources/g2/ablation.csv

58d7adb7a18a8ee612d82093186129b39b84c5ca324c8d1810710591fdae7032  sources/g2/analyze_stage4.py

d361c2795af955238012c7f087cf07b658ad3fcb9879ddc8da3f2d7fed905ed9  sources/g2/coverage.json

1778446711a293fc1e3c1ab2a3ea2821078661be565d26f1de7e3afac70f24fe  sources/g2/efficiency-run.json

3b27422a7552c44ff164448adf822ff402256786ba502de42ffb10f0292942aa  sources/g2/efficiency.csv

dd35590d77323e6e2bf27e276e77e2bbb11d990bdc8c1347f2fc01092e62a6b1  sources/g2/environment-current.json

8cadbcb8e5b2abd8aa9735e98d7381ed540fc8941718e1c5a363b0e51e968571  sources/g2/figures/ablation.png

2668609a27dec67d38b06ef85d24198f5212cea49bd19150deb8842554bbdcfc  sources/g2/figures/efficiency.png

fb7c4a8d4f53e2048eab1a9d3595941d1b0f26acd244f705986f72e745c4d780  sources/g2/recovery-cases.json

d8e110232901480083806003e648d7b8fa278cdce3d24ade7d77c167e2275aae  sources/g2/stats.json

a81090e2589fcef37f310ee2a265076e4560a296a59864c9d43a6e9b62fe3997  sources/paper/LongLLMLingua.pdf

653b779ef30d75a70ac83a6816d101927836a8fc6ed83cb76c47556f4b49836b  sources/paper/figure2.png

9a121f9dd5bf7db5d2033e3e7e030b175f771e41ef3cc425ce5efcca245e29b2  sources/paper/finish-paper-pages1-3.txt

cc03b706f98011afd9c1aae4c6a8f429264025ebab180b50ceaf56c90c85f9cd  sources/paper/page3.png

6afe37ae484aa63efec5f923aa1a6b8f25ba3b94369d26d2d6e1dac3aff72f62  sources/paper/paper.txt

d773e490aa6d0a2854098eacdd6d0dd53456e6a1828f828643ca7a20a5b0e9c8  sources/report-latest.md

57bcdbc2fca6530f9296d6a7f7b639eb658544fa34fcbff865fd273ee4af1c69  sources/speaker-map.md

d61f4228ae3ebc6e509f728c496c889a76854ac22c5c05130f80229c616d4bf0  sources/verified/cases.json

cb82a0de26abc42fa31d9cf404354e2649d4e94819668784c79be9418ced612f  sources/verified/stage1-audit.json

9ce361a3e5f3054895512870602eca6cb3baf986b5f080024841081cb284b98b  sources/verified/stage1-audit.md

beb0bb256c2b4732077de7d267226187e7182a4b4ae893e8f115821769c05a1b  sources/verified/stage1-predictions.jsonl

d3739a281dcd782ec9d064844364fdf906d9b82816d1d83664f15a7e44041724  sources/verified-member1-sources.md

## 最终成品检查结果
- 9页物理顺序未变；v5除B1只读证据命令、标签与出处说明外，其余8页页面XML与v3逐字节相同，未变数据、排版或短标题。
- 全9页逐页亲看；修后再看P4/B1与全组最终拼图。
- check-overlap：no findings；OOXML：72个XML部件校验通过，1个无schema；两种字体均已安装，无影响可见文本的缺失字体。
- P1/P2/P3/P7页面XML不变；P5/P6/B2只加既有页脚内部跳转；P4/B1仅残留排版修复。备注9/9写入新版讲稿与源链。
- 同版PDF和逐页图均从最终PPTX一次渲染导出；PDF为静态备览，PPTX保留原生文字、表格、图形和引用论文图，不是整页截图。
- 机器检查不替代Windows/投影、真人计时、录屏或课程评分验收。

## v5最终交叉核对
- 物理第8页正确命令：`python -m json.tool reports/stage3-main/run.json`；标签为查看已保存pilot运行快照。仅查看已有JSON，不加载模型、不调用API，不生成计划。
- 第9页原命令完整保留：`python scripts/analyze_stage4.py --out /tmp/g14-stage4-audit`。临时out避免覆盖已提交结果，本轮未执行。
- v5已去除不适用的配置路径与相关计划/推理命令；v5包不包含旧历史备注附件。v3成品和旧zip仍保留，仅历史参考，已被v5替代。
- 已亲看最终全组拼图与第8页渲染：无字符缺失、容器溢出或图注遮挡。其他8页XML字节不变。
- 全套check-overlap无发现；72个XML部件schema校验通过，1个无schema；两种字体已安装，无影响可见文本的缺失字体。
- 页数9不变；备注9页仅统一v5版本标识及相应错误修正；B1成员3讲稿、QA、证据导航与本报告同步。
- 本轮只修证据命令与配套资料，不是新实验，未执行所展示命令、模型推理或API，也未上传。既有事实边界和未验证项不变。


## v5 本轮补充核验
仅更改视觉表达与图表指认，原数据变化为0；不新增推理/API。P1/P2/P7保留结论横幅，P3/P4/P5/P6/P8/P9改局部证据表达。
P5七方法可编辑点图按原方法顺序，EM轴0–100；仅右侧两条真实问题级配对CI，跨0不证明等效，Long4x18/500超预算。
P6以NPU full82.6为配对参照；ablation.csv与analyze_stage4.py L54–71证明CI来自paired_comparisons，full无CI、original外部参照、no_recovery为已有回答派生。右侧独立效率total_pipeline_seconds_p50/p95是分位点，非CI；没有端到端加速。
P9保留原效率图，阶段中位数不能相加为E2E。P8只查看已有pilot快照：`python -m json.tool reports/stage3-main/run.json`。P9保留`python scripts/analyze_stage4.py --out /tmp/g14-stage4-audit`，本轮两命令均未执行。
作图原值/线性映射见sources/g2/v5-chart-data-and-mapping.json，独立坐标核对见chart-source-audit-v5.json。历史输出缓存、CUDA型号、CANN缺口保留；Windows投影与真人计时未验证。
