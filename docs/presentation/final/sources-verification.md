# 来源与核验

## v7（当前入口，2026-11-21 晚间，Asia/Shanghai）

当前演示稿（v10）是本目录 `slides.pptx` / `slides.pdf`（SHA-256 `b2bb8abaa8fd8ea8e6d981a81b1def2d4dc4a67d0ff2d404a893636c1196182f` / `f66aece4f5cf68b120aa14af0570f448fe9e00dda57d490b0e3d39bccdc294bd`）。P9 真正内嵌唯一 MP4 `ppt/media/media1.mp4`，抽出字节 SHA-256 `3192f268b4a9daf937678d4bd8c154bb7b380e9723858023cbbcc099862eb3d6`，与仓库根 `evidence/core-evidence-60s.mp4` 一致；video 与 media 两个关系指向同一内部部件，无 `TargetMode="External"`，无 `file:///workspace`。PDF 为静态 poster 版，无 `file://`、无活动视频动作。独立软件解码此前已通过；本仓库测试钉扎哈希与“无外部媒体”。Windows / PowerPoint 实播和音频听验仍未做。

旁置 mp4、SRT、poster、解说文稿与 `EDIT-MAP.md` 在仓库根 `evidence/`。同日 50 秒测试实录仍在该目录，只作历史材料。P8 历史 CUDA、P9 左历史 NPU 图与 77/77 归因、以及下面 v6 当时的来源链保持有效，未改实验表。

# v6 来源与核验（历史）
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
