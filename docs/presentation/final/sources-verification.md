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
