# v7 证据导航

物理页序不变P1–9；既有P5→P8→P6→P9→P7页内链接保留。
推荐视频路线：P1–4约150秒 → P5–7约150秒 → P9进入本页自动播放60秒视频 → QA90秒 → 换组30秒；不要再单讲P8/P9各30秒，也不要给视频追加引入/收尾。
静态备选路线：1,2,3,4,5,8,6,9,7；P1–7合计300秒，P8/P9各30秒。两种路线二选一，不叠加。
P8保留CUDA历史run/coverage/summary/stats；P9左历史NPU图，右新片poster，下方原77/77归因。
B1只读命令：`python -m json.tool reports/stage3-main/run.json`。B2离线复查：`bash reports/local-verification/recheck.sh`。构建PPT不执行这些命令，不声称其为新推理。

v7：P1–P7主讲300秒；证据段仅60秒，不追加引入或收尾。推荐（待成员认可）：两人主讲P1–4约150秒/P5–7约150秒，第三人操作60秒证据，第四人控时/QA协助；教师指定成员先答。四人无需每人讲一页。静态备选P8/P9各30秒；视频版先讲完P1–7，再到P9进入本页后自动播放，整段60秒替换静态证据。QA90秒、换组30秒，总8分钟，均为预算未真人计时。
视频含中文讲解和烧录中文字幕；制作说明客观记录合成配音来源。画面已剪辑、1×原速、含短定格；样本独立补拍。CPU BM25结果已跑完，对保存回答现场评分；Long仅代码展示未执行，CUDA/NPU为历史记录，不能称完整实时重跑或新模型推理。77/77仍仅由既有pytest-full.stdout/JUnit证实，不是新视频跑出的成绩。新版视频技术参数与哈希已核实；本次仅检查PPT静态poster布局，不声称音频听验或Windows实际播放通过。
缺口：P编号/四人登记、成员本人贡献与认可、stage2/3/4完整逐条输出及压缩/问答缓存与校验和、CUDA具体型号、阶段4 CANN、受控Cursor结果。PowerPoint桌面播放/Windows投影、真人计时未实测。
来源：core-evidence-60s.mp4、poster.png、core-evidence-60s.srt、NARRATION.md、EDIT-MAP.md（/workspace/g14-core-demo/final）；SHA256 3192f268b4a9daf937678d4bd8c154bb7b380e9723858023cbbcc099862eb3d6。