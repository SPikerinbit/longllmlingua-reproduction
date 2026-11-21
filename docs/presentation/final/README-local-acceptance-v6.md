说明：本文是 v6 当时的本机验收记录，只作历史材料。当前入口是本目录 v7 的 `slides.pptx` / `slides.pdf`，P9 内嵌 `evidence/core-evidence-60s.mp4`；见 [README.md](README.md)。

# G14 v6 本机验收与交付
平台PowerPoint本地；严格9页。PPTX/PDF在本目录，pages/含9页图，contact.jpg为最终拼图；scripts/四人讲稿及导航，QA-v6.md，sources-verification-v6.md，sources/作图映射与轻量源，checks/机械核验。

## 时间预算
演讲次序1,2,3,4,5,8,6,9,7；成员1 P1/P2/P7=25+35+30=90秒，成员2 P3/P4=45+45=90秒，成员3 P5/P8=60+30=90秒，成员4 P6/P9=60+30=90秒。主讲300秒+静态证据60秒=360秒；QA90秒+换人30秒=480秒原8分钟预算，非真人实测。默认静态P8/P9两人各30秒。50秒视频仅替代原60秒证据，不额外添加；按导航成员3/4各25秒旁白+5秒引入/收尾，保持各90秒。

## 使用与复查
整包解压，不单独移动PPTX；evidence/必须与PPTX相邻。P8只读命令：python -m json.tool reports/stage3-main/run.json。P9复查入口：bash reports/local-verification/recheck.sh；必须在已准备数据的正式仓库根目录执行。本包仅随附证据，不含repo、venv、数据、tokenizer或模型大文件，不能直接在本包根运行脚本。本finish未执行这些命令。
本机是CPU离线测试验收，不是新模型推理，历史CUDA与NPU分批，不能合并环境；77/77来源及边界见来源核验。真实视频/截图已复制；无上传、无repo修改、工作目录未clean。

## 验收
schema 72部件通过；overlap无发现；3字体均安装；PDF9页；全9页最终渲染亲看；P1–P7正文及关系保护；P9原图保护；相对视频链接存在；77日志交叉核验。外部网页未联网重新验证，PowerPoint/Windows投影点击未实测。
SHA256SUMS为包内文件清单（不含自身）；zip置于目录外，不递归纳入，旁置同名.sha256。

## 真实left
stage2/3/4完整results.jsonl、压缩/问答缓存及sha256；CUDA型号、阶段4 CANN、受控Cursor结果；P号和四人登记；真人计时、本人贡献/本人确认；Windows/投影实测。不得宣称可直接提交或课程全满分通过。tokenizer与视频不再缺。
