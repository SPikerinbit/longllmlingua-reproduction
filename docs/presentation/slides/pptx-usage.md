# 幻灯片用法

模板文件：`docs/presentation/slides/G14-LongLLMLingua-template.pptx`。成员一定稿三页：`docs/presentation/members/member1/slides-P1-P2-P7.pptx`。生成脚本：`docs/presentation/slides/build_slides.py`。改字之后重新运行脚本，再用 LibreOffice 导出，不要只在本机 PowerPoint 里另存一版配色。

## 配色

颜色和已有结果图对齐，图文件本身没有改。

| 角色 | 色值 | 用在哪 |
| --- | --- | --- |
| 墨蓝 | `#1B3A4B` | 标题、页脚底 |
| 主色 | `#245C84` | 与 `ablation.png` 里完整方法的深色条一致 |
| 强调 | `#C4843C` | 由效率图 QA 段 `#E6A14A` 压暗，保证浅底上仍能读 |
| 纸色 | `#F6F4F1` | 页背景 |
| 表头 | `#245C84` 白字 | 全部结果表 |
| 高亮行 | `#E7F0F6` | LongLLMLingua 2x 或 BM25 4x 那一行 |

`positions.png` 仍是 `scripts/plot_results.py` 的 matplotlib 默认色。它不放进七页主讲，避免和这套主色抢。`ablation.png` 放在 P6 右侧；图里的字是脚本设置的 10 pt，页上另用 20 pt 和 28 pt 写出 45.0、78.0、83.2。不要把图拉大到盖住左侧数字，也不要重新导出覆盖仓库里的 png。

## 字体

模板里的西文和中文都指定为 `Noto Sans CJK SC`。本环境已安装这个家族，LibreOffice 渲染没有缺字。

汇报电脑若没有 Noto，按这个顺序换，只换字体名，不改字号和位置：

1. Noto Sans CJK SC
2. Source Han Sans SC（思源黑体，与 Noto CJK 同源）
3. Microsoft YaHei（微软雅黑）
4. WenQuanYi Micro Hei（文泉驿微米黑）
5. Droid Sans Fallback

Windows 上最常见的是微软雅黑。换字体后看 P5 的表有没有把 “LongLLMLingua 4x” 挤出格子。

## 字号

课程要求：标题不小于 28 磅，正文不小于 20 磅，结果表不小于 18 磅。

| 元素 | 磅 | 说明 |
| --- | ---: | --- |
| 封面主标题 | 36 | P1 |
| 内页标题 | 28–32 | P6 标题是 28，因为句子长 |
| 结论和正文 | 20 | |
| 表 | 18 | |
| 来源和表注 | 18 | |
| 页脚 “G14 · LongLLMLingua 复现” 和页码 | 14 | 页脚条，不是正文 |
| 右上角成员标签 | 18 | |

生成脚本会拒绝正文和表里低于 18 磅的文字。页脚低于 14 磅也会失败。

## 九页分别是什么

| 页 | 版式 | 谁改 |
| --- | --- | --- |
| P1 | 封面 | 成员一，已定稿 |
| P2 | 正文 + 小表 | 成员一，已定稿 |
| P3 | 正文四行 | 成员二。可改“建议句”，不可改 revision 和 100/100 |
| P4 | 结果表 | 成员二。可改建议句，不可改表内对照 |
| P5 | 结果表 | 成员三。七行数字与 README 主比较表一致 |
| P6 | 图 + 结论 | 成员四。左侧数字是口播用的，右侧图只作对照 |
| P7 | 结论 | 成员一，已定稿 |
| 运行证据 | 两栏 | 左 30 秒成员三，右 30 秒成员四 |
| 备份 | 四行 | 录屏路径仍是 TODO |

## 渲染检查

2026-11-21 在本环境用 LibreOffice Impress 24.2 导出 PDF，再用 `pdftoppm -png -r 110` 得到：

- `slides/previews/template-1.png` 到 `template-9.png`
- `slides/previews/G14-LongLLMLingua-template.pdf`
- `members/member1/previews/slide-1.png` 到 `slide-3.png`
- `members/member1/previews/slides-P1-P2-P7.pdf`

检查过的结果：中文没有方框；P5 的表注不再伸进页脚；P6 的纵轴标签还在图内；页脚没有挡住正文。P6 图内的 10 pt 标签很小，这是原图，不是幻灯片字号不够。口播以左侧大字为准。

不要把预览 PNG 当成 `slides.pdf` 交上去。终稿 PDF 要从四人改完的那一份 pptx 重新导出。
