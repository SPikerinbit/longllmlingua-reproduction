# G14 v7 — edit / finish

平台：PowerPoint，本地工作。唯一最终源：preview-g1-fix.pptx及当前notes/g1.md；未读取历史validation。9页，实际16:9；只校正尺寸type元数据，未改页面宽高。无repo修改/推送，无工作区清理。

## 版式目录（由catalog/grid.jpg与预览亲看确认）
- 封面论文图：slide1.xml；论文图+项目范围，绿横幅。
- 数据与基线：slide2.xml；数据代码样式+结果表，绿横幅。
- 方法：slide3.xml；论文图+真实代码双区，无横幅。
- 预算：slide4.xml；校验日志+预算数值，无横幅。
- 主结果：slide5.xml；点图+配对差CI，锁定。
- 消融效率：slide6.xml；配对CI+独立耗时分位图，锁定。
- 结论：slide7.xml；结论表/CI/案例，绿横幅。
- CUDA记录：slide8.xml；run/coverage/summary/stats，锁定正文。
- NPU与本机验收：slide9.xml；左原NPU图、右poster、下方77证据，唯一需改视觉页。

## Storyboard（物理顺序不变，映射已核对presentation.xml+rels）
1. LongLLMLingua复现｜封面论文图｜slide1.xml｜不动。
2. 数据与基线｜数据/结果双区｜slide2.xml｜不动。
3. 压缩方法｜论文图+代码｜slide3.xml｜不动。
4. 预算验收｜日志/预算｜slide4.xml｜不动。
5. 主要结果｜点图+配对CI｜slide5.xml｜不动。
6. 消融与效率｜配对CI+独立分位图｜slide6.xml｜不动。
7. 结果与边界｜结论表/CI/案例｜slide7.xml｜不动。
8. CUDA运行记录｜历史来源链｜slide8.xml｜正文不动；仅在讲稿确有旧视频表述时改notes。
9. NPU与本机验收｜左原图+右内嵌视频poster｜slide9.xml｜原位替换截图为可点击内嵌movie；页底外链文字改播放说明，50秒改新60秒；其余结构/事实不动。


## 合并最新g1记录
# edit / fix / g1（P8–P9）
新最终视频已替换，来源/workspace/g14-core-demo/final/core-evidence-60s.mp4；SHA256 e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e。poster SHA256 f0dcb9d32a98ee4822c44712450664f993b59d8a1553ddea65b8f5c86447b5a8。
P9右上标准OOXML movie，内部videoFile/p14:media关系、点击动作及手动开始timing；不自动播放。可见页眉“核心证据 · 60秒中文讲解”，poster顶栏普通“LongLLMLingua 复现演示”，历史GPU/NPU标“历史实验结果”。制作说明保留真实合成配音来源与剪辑边界，不称真人现场。
P1–P8正文及关系不改；P9左NPU图、77/77及其归因不改；标题30pt/改写正文20pt，不缩字。300秒主讲+60秒证据，不叠加；推荐分工未获本人认可，缺口保留。旧哈希与过时媒体说明已从当前PPTX注释/交付文档中替换。
下一步finish：合并本notes，生成全套PDF静态poster并移除file://视频动作，统一交付包只能采用本轮preview-g1-fix.pptx及当前media-source/scripts/README-v7.md，不打包旧preview或validation历史中间件。Windows/PowerPoint真实播放尚未测试；结构/解码核验不等于播放通过，音频未听验。

## 本轮已验证
`office pack --original start.pptx` schema通过：72项、0问题。`check-fonts` 0缺失、`check-overlap`无发现。已亲看renders/g1-2/contact.jpg：普通页眉、新poster、20pt播放提示及替代预算正常，无新增溢出。
独立validation/final-offline-pptx-only目录仅slides.pptx；抽取新MP4字节SHA与最终源完全一致，抽出后完整解码通过。包内只有1个MP4，两个video/media关系均指向同一内部媒体，poster哈希正确，旧哈希不在PPTX XML/关系中；当前交付文档扫描亦无旧哈希。P1–P8 slide/rels及P9左NPU/77/exit/归因再次对照不变。详见validation/final-media-audit.json。
供finish的唯一当前预览：preview-g1-fix.pptx。图片renders/g1-2/slide-09.jpg；P8只notes变更且正文未变，无需重复检查。PDF动作清理仍留finish；不得交付renders中的未清理PDF。

## 最终执行
当前文稿已整理到deliverables-v7/scripts，默认primary-two-speakers.md；P1–4 150秒、P5–7 150秒，内嵌视频60秒替换P8–9证据预算。成员本人认可仍待补。保留四人备选分段，不作默认分工。
## 设计与来源
原Noto Sans CJK SC及代码字体、白底深绿006C39、橙页签与页脚不变。正文/原图/数据不重建。事实来源沿用PPT逐页notes及当前scripts；媒体制作来源见sources/NARRATION.md、EDIT-MAP.md。
## 剩余缺陷/边界
Windows/PowerPoint真实放映与音频听验未做；真人计时未做。原始证据区/图中文字及来源页脚存在低于20pt的既有小字，保留原文原图不偷偷缩字；大号标题/核心结论用于主讲，细节供PDF放大查阅，不将整页所有文字冒称满足20pt。
