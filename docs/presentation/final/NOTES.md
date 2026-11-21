# G14 本机证据补充：edit / storyboard

平台：PowerPoint；编辑面：本地 PPTX。最后阶段：storyboard。起始：start.pptx（v5）。
本阶段未修改任何幻灯片正文/结果图/数字。preview.pptx 为9页原布局预览；contact-sheet.jpg 的页外标注是待 build 方案，不是已完成的修改。

## 版式目录
- 论文封面+方法图：slide1.xml，绿横幅；短标题。
- 数据与结果双区：slide2.xml，绿横幅；终端样式数据与表格。
- 论文图/真实代码双区：slide3.xml，无横幅。
- 校验日志/预算混合：slide4.xml，无横幅；396/400。
- 点图+配对差CI：slide5.xml，无横幅；主结果，锁定不动。
- 消融配对差CI+独立耗时分位图：slide6.xml，无横幅；锁定不动。
- 结论表/CI/案例：slide7.xml，绿横幅；保持不动。
- CUDA来源链：slide8.xml，无横幅；JSON原字段、coverage、CI。
- NPU记录图+批次证据：slide9.xml，无横幅；保留左侧原结果图，右侧改实录截图。

## Storyboard（严格9页，顺序不变）
1. LongLLMLingua复现｜封面论文图｜slide1.xml｜不动。
2. 数据与基线｜数据/结果双区｜slide2.xml｜不动。
3. 压缩方法｜论文图+真实代码｜slide3.xml｜不动。
4. 预算验收｜验证日志/预算｜slide4.xml｜不动。
5. 主强结果｜点图+配对差CI｜slide5.xml｜不动；全部图/数锁定。
6. 消融与效率｜配对差CI+独立耗时分位图｜slide6.xml｜不动；全部图/数锁定。
7. 结果与边界｜结果/结论｜slide7.xml｜不动。
8. CUDA运行记录｜原来源链｜slide8.xml｜最小修改：仅在现有底部说明处加“历史CUDA批次”；保留所有字段/图数/命令，在讲稿区明确与本机验收分批，主图来源仍为原stage3记录。
9. NPU与本机验收｜保留NPU图+终端截图｜slide9.xml｜主要修改：左侧原结果图位置/内容不变；右上现有环境表/说明区域换为 evidence/local-offline-evidence-result.webp（原图等比，不能把复排文字伪装终端截图）；右下大号77/77及exit 0，标注此结论依据stdout/JUnit；原NPU run/coverage/env移至左下紧凑来源条，分批标“历史NPU”与“2026-11-21本机离线验收”。页底命令 bash reports/local-verification/recheck.sh；下一行相对链接 evidence/local-offline-evidence.mp4（50s备用、不嵌二进制）。

## Build分组
唯一组 g1：P8–P9（slide8.xml、slide9.xml）。P8只改底部批次说明与讲稿；P9换右侧证据区并迁移现有环境表。无须第3页或第10页。
P9短标题建议“NPU与本机验收”（7字），不得扩展成长句。
P9布局边界：保留左图(0.6,1.79,6.7,3.402)；右区约(7.63,1.79,5.1,3.19)用于截图；左下5.3–6.05区域收纳历史NPU run/coverage/设备/依赖，不删数字；右下约5.1–6.05用于77/77与当前环境；6.1–6.9用于复查命令、视频链接、来源。若正文拥挤，run哈希全文放讲稿而正文保留唯一前缀+文件来源，不缩小结果图。

## 风格锁定
保留Noto Sans CJK SC/原代码字体、白底深绿006C39、橙色页签、底部页脚；标题30pt附近沿用原值。仅P1/P2/P7绿横幅；禁止重复全页横幅/等宽卡/长标题。其他页面逐字逐对象不动。

## 事实及来源
- main bdb11d3；Python3.13.5/tokenizers0.22.1；prepare配置公开官方tokenizer与NQ五个gz；77项全过、exit0；2026-11-21 17:46:58–17:47:02 Asia/Shanghai（北京时间）。依据 /workspace/g14-local-main/repo/reports/local-verification/{README.md,pytest-full.stdout,junit-full.xml,full-pytest.command.relative.txt,pip-freeze-post.txt,data-tokenizer-sha256.txt}。
- 复查命令：仓库根目录 bash reports/local-verification/recheck.sh。四阶段离线audit api_calls=0；不载权重、非新推理、已发表分数不变。来源同目录audits/及 /workspace/g14-local-main/docs/RUN-SUMMARY.md。
- 当前env与历史GPU/NPU环境不能合并；历史stage4 Python3.12.0/tokenizers0.21.4是另一批。官方tokenizer revision 314113f8a7dadb388215396ba5fbee2c610a04d6，资源哈希已匹配。正文可简写，详情讲稿/README。
- 真实录屏：用户交接报告videoReview已核验连续5项通过、全套77进度至100%、脚本退出0，无secret或其他应用。我未观看/解析视频；只读了用户提供结果截图。H264、1920×1200、50s、1915107 bytes依用户交接。包内路径 evidence/local-offline-evidence.mp4；不嵌PPT。
- 实录截图 evidence/local-offline-evidence-result.webp 是原图副本；其77项段落显示进度100%，77/77明确数字来自完整stdout/JUnit，不把它误称视频中打印了77 passed摘要。
- README/建议文档中“录屏仍缺”是录屏完成前的旧状态，以用户本轮事实为准；不再列tokenizer/录屏缺口。

## 讲稿/计时（build更新，不扩大任务）
四人各90秒：保持主讲300s+证据60s，总360s。P8约25s、P9约35s共60s，作为原证据段替换；50s视频默认备用不自动播放，不额外叠加。若选播放，50s替换同段证据演示，仅留10s引入/收尾，仍60s；不是额外视频时段。P1–P7主讲和四人分配不重排。

## 剩余缺陷/待办
- P8：left，尚待build补历史批次标签/讲稿隔离声明。
- P9：left，尚待build截图/77/77/复查命令/相对视频链接/历史NPU来源迁移；需render检查可读性。
- 事实材料仍缺：stage2/3/4完整results.jsonl及压缩/问答缓存+sha256，CUDA具体型号、阶段4 CANN、Cursor受控问答结果、P号、登记表四人信息、本人确认。不得编造、不得标“可直接提交”。
- tokenizer资源缺口和录屏未完成已解决，不再列缺口；不修改真实论文图和原日志。
- 当前尚未build或finish；preview不是交付版，不嵌视频。


# v6 finish 合并（edit / finish，PowerPoint本地）
起始 preview-g1.pptx；严格9页，不新增页，P1–P7受保护；以下build记录覆盖前文尚未build的历史状态。
# edit / build / g1 — P8/P9，准备finish合并v6
- 物理页映射已按presentation.xml+rels确认：P8=slide8.xml，P9=slide9.xml，未用旧历史映射。
- P8 fixed：增加历史CUDA批次20pt阅读标签；run/coverage/summary/stats、CI及只读命令原文与来源链不改。讲稿声明不与本机验收合批。
- P9 fixed：保留原真实NPU图/位置/图形内容，替换右区真实截图；新增38pt 77/77与24pt exit0，图旁明确stdout/JUnit来源；20pt本机CPU/离线标签、Python3.13.5/tokenizers0.22.1；历史NPU完整run/设备/依赖原数移至备注，正文保留3500/3500、1200/1200、Ascend910B4、CANN缺口。
- P9 fixed：仓库根复查命令bash reports/local-verification/recheck.sh；相对外链evidence/local-offline-evidence.mp4，文件已在旁，不嵌视频。未运行原实验、未修改repo、未上传。
- 图像事实：WEBP是源原图副本，PNG是无损格式转存，未拼接/改终端内容。77/77通过实际JUnit77 testcase且零失败/错误/跳过+完整stdout77 passed核验。截图不是77 passed摘要；videoReview由用户交接，本build未另看视频。
- 保护：P1–P7 XML/关系、presentation及package关系不变；历史NPU图canonical XML完全相同。P9自己的关系仅按新截图/相对外链需求变更。checks/有核验记录。
- 四人稿/导航：notes/scripts/*-v6.md为本地更新版；各90秒，主讲300s+证据60s。默认P8/P9各30s；视频50s可选替代原60s，各25s旁白+5s引入/收尾，成员3/4都发声。P1–P7正文与分工不重排。
- left（真实缺口，不能视觉修复）：stage2/3/4完整results.jsonl及压缩/问答缓存+sha256，CUDA型号、阶段4 CANN、Cursor受控结果、P号及四人登记信息；真人讲述计时/本人确认/本人贡献未完成，不能代填。tokenizer与录屏不再列缺口。
- finish待做：合并本组notes至NOTES.md、全套9页检查/打包v6；保留相对evidence目录和四人稿。build不改NOTES.md、不做clean或full pack。

## 本阶段亲看与机械检查
已亲看renders/g1-1/contact.jpg及P8/P9，发现P9原来源小注与视频链接重叠；唯一fix pass把完整历史来源移入P9备注，亲看renders/g1-2/contact.jpg与P9，重叠已消除，关键标签/正文无裁切。P8未在fix pass改变。最终check-overlap为0，validate --original通过，字体均安装。NOTES.md未改。


# finish v6 最终状态
workflow edit / phase finish；preview-g1.pptx → deliverables-v6/G14-LongLLMLingua-slides-v6.pptx。已合并g1和v6讲稿，9页最终渲染逐页亲看；schema/重叠/字体/PDF9页与证据链接检查通过，无新增视觉缺陷，无新页。P1–P7受保护，P9原NPU图保留。工作目录保留未clean（仅执行PPTX包内无用部件clean）。
# v6 来源与核验
本轮本地finish，未上传、未修改repo、未重跑测试/推理/API。九页最终渲染已逐页亲看，无裁切或遮挡；短标题及差异化版式保留。P1–P7正文与关系、全9页build后正文canonical核对一致，P9原NPU图保留。机械检查详见checks。

## 证据来源
- 视频：工作目录 evidence/local-offline-evidence.mp4 等字节复制至本包同路径；ffprobe确认H264、1920×1200、50.000s、1915107 bytes。内容连续与无秘密依据用户交接videoReview，本finish未重新观看视频。
- 截图：/workspace/g14-local-main/runs/G14-local-offline-evidence-result.webp 与包内WEBP哈希相同；PNG为build无损转存，未复排终端。
- 77项：repo/reports/local-verification/pytest-full.stdout、junit-full.xml、README.md → evidence/local-verification/同名文件。JUnit77项、零失败错误跳过与stdout77 passed交叉核验；exit0来自运行记录/截图。截图不是77 passed摘要。
- 本机main bdb11d3，2026-11-21 17:46:58–17:47:02 Asia/Shanghai，CPU离线，Python3.13.5/tokenizers0.22.1；四阶段api_calls=0；不载权重，不是新模型推理，历史分数不变。
- P8历史CUDA：e07ac77 reports/stage3-main/{run,coverage,summary,stats}.json；已附轻量JSON到sources/g1和sources/g2。
- P9历史NPU：f08b229 reports/stage4-ablation-efficiency/，轻量run/coverage/environment在sources/historical-npu；原图及数据不改。Python3.12.0/tokenizers0.21.4不能与本机混批。
- 作图mapping：sources/g2/v5-chart-data-and-mapping.json；chart-source-audit-v5.json为原v5核验，不冒充本轮重跑实验；CSV和作图代码随附。
- sources/history/sources-verification-v5.md仅历史源链；旧“录屏未完成”及旧B2命令以v6文档为准。

## 链接检查
PPTX所有external关系已列checks/final-audit-v6.json；相对evidence/local-offline-evidence.mp4在包内存在，不嵌入、不自动播放。正式课程包同样将evidence/置于PPTX旁。外网URL只检查关系/格式，本finish不远端重新研究；Windows PowerPoint点击与投影未实测。

## left
stage2/3/4完整results.jsonl、压缩/问答缓存及sha256，CUDA具体型号、阶段4 CANN、受控Cursor结果仍缺。真人计时、本人贡献/本人确认、P号及四人登记未完成；P7已有“本人”字样按保护要求保留，不等于本轮代本人确认。tokenizer与录屏已解决，不再列缺口。
