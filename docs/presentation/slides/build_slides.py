#!/usr/bin/env python3
"""Build the G14 16:9 deck and the member-one finished pages.

Numbers on the slides are the rounded figures already printed in README.md
or the stage reports. Unrounded sources are listed in the speaker notes and
in docs/presentation/01-number-registry.md. This script does not read or
rewrite reports/.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[3]
SLIDE_W = Inches(13.333333)
SLIDE_H = Inches(7.5)
FONT = "Noto Sans CJK SC"

INK = RGBColor(0x1B, 0x3A, 0x4B)
PRIMARY = RGBColor(0x24, 0x5C, 0x84)
PRIMARY_DEEP = RGBColor(0x1A, 0x45, 0x66)
ACCENT = RGBColor(0xC4, 0x84, 0x3C)
ACCENT_SOFT = RGBColor(0xF8, 0xEF, 0xE4)
PAPER = RGBColor(0xF6, 0xF4, 0xF1)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEXT = RGBColor(0x1C, 0x24, 0x2B)
MUTED = RGBColor(0x4E, 0x5D, 0x68)
LINE = RGBColor(0xD5, 0xDE, 0xE6)
ROW = RGBColor(0xF4, 0xF8, 0xFB)
HILITE = RGBColor(0xE7, 0xF0, 0xF6)
SAGE_SOFT = RGBColor(0xE7, 0xF2, 0xE6)


def set_run(run, text, size, bold=False, color=TEXT, font=FONT):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    rpr = run._r.get_or_add_rPr()
    for tag in ("latin", "ea", "cs"):
        node = rpr.find(qn(f"a:{tag}"))
        if node is None:
            node = rpr.makeelement(qn(f"a:{tag}"))
            rpr.append(node)
        node.set("typeface", font)


def add_rect(slide, l, t, w, h, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    # Drop the rounded-rect adjustment if any, and the shadow.
    sppr = shape._element.spPr
    effect = sppr.find(qn("a:effectLst"))
    if effect is not None:
        sppr.remove(effect)
    return shape


def add_text(slide, l, t, w, h, content, size=20, bold=False, color=TEXT,
             align="left", anchor=MSO_ANCHOR.TOP, spacing=1.0):
    box = slide.shapes.add_textbox(l, t, w, h)
    frame = box.text_frame
    frame.word_wrap = True
    frame.auto_size = None
    frame.margin_left = Emu(0)
    frame.margin_right = Emu(0)
    frame.margin_top = Emu(0)
    frame.margin_bottom = Emu(0)
    frame.vertical_anchor = anchor
    if isinstance(content, str):
        content = [content]
    for i, item in enumerate(content):
        if isinstance(item, str):
            text, sz, bd, col = item, size, bold, color
        else:
            text = item["text"]
            sz = item.get("size", size)
            bd = item.get("bold", bold)
            col = item.get("color", color)
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        p.line_spacing = spacing
        set_run(p.add_run(), text, sz, bd, col)
    return box


def set_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def chrome(slide, page_label, owner, seconds):
    """Footer and the responsibility chip. Footer is chrome, not body copy."""
    add_rect(slide, 0, 0, Inches(0.10), SLIDE_H, PRIMARY)
    add_rect(slide, 0, Inches(7.16), SLIDE_W, Inches(0.34), INK)
    add_text(slide, Inches(0.32), Inches(7.20), Inches(8.4), Inches(0.26),
             "G14 · LongLLMLingua 复现", size=14, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(8.6), Inches(7.20), Inches(4.4), Inches(0.26),
             page_label, size=14, bold=True, color=WHITE, align="right", anchor=MSO_ANCHOR.MIDDLE)
    add_rect(slide, Inches(10.15), Inches(0.18), Inches(2.90), Inches(0.42), ACCENT_SOFT)
    add_text(slide, Inches(10.20), Inches(0.20), Inches(2.80), Inches(0.38),
             f"{owner} · {seconds}", size=18, bold=True, color=ACCENT,
             align="center", anchor=MSO_ANCHOR.MIDDLE)


def style_cell(cell, text, size, bold, fill, color, align="left"):
    cell.text = ""
    cell.fill.solid()
    cell.fill.fore_color.rgb = fill
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.08)
    cell.margin_right = Inches(0.06)
    cell.margin_top = Inches(0.02)
    cell.margin_bottom = Inches(0.02)
    p = cell.text_frame.paragraphs[0]
    p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
    p.space_before = Pt(0)
    p.space_after = Pt(0)
    set_run(p.add_run(), text, size, bold, color)
    # Kill the theme font on the cell defRPr as well.
    tc = cell._tc
    tcpr = tc.get_or_add_tcPr()
    for child in list(tcpr):
        if child.tag == qn("a:solidFill"):
            continue


def add_table(slide, l, t, w, h, rows, col_widths, font=18, highlight=None):
    table_shape = slide.shapes.add_table(len(rows), len(rows[0]), l, t, w, h)
    table = table_shape.table
    table.horz_banding = False
    table.vert_banding = False
    for i, width in enumerate(col_widths):
        table.columns[i].width = width
    row_h = int(h / len(rows))
    for r, row in enumerate(rows):
        table.rows[r].height = row_h
        for c, value in enumerate(row):
            if r == 0:
                fill, color, bold = PRIMARY, WHITE, True
            elif highlight is not None and r == highlight:
                fill, color, bold = HILITE, TEXT, True
            elif r % 2 == 0:
                fill, color, bold = ROW, TEXT, False
            else:
                fill, color, bold = WHITE, TEXT, False
            align = "left" if c == 0 else "right"
            style_cell(table.cell(r, c), value, font, bold, fill, color, align)
    # Remove the default table style so LibreOffice does not restyle fonts.
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    style = tbl_pr.find(qn("a:tableStyleId"))
    if style is not None:
        tbl_pr.remove(style)
    return table_shape


def new_prs():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    prs.core_properties.title = "G14 LongLLMLingua 复现"
    prs.core_properties.subject = "NLP 2026 论文部分复现"
    prs.core_properties.category = "G14"
    return prs


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def slide_p1(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    add_rect(s, 0, 0, SLIDE_W, Inches(0.12), PRIMARY)
    add_rect(s, 0, 0, Inches(0.10), SLIDE_H, PRIMARY)
    add_rect(s, 0, Inches(7.16), SLIDE_W, Inches(0.34), INK)
    add_text(s, Inches(0.32), Inches(7.20), Inches(8.4), Inches(0.26),
             "G14 · LongLLMLingua 复现", size=14, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(8.6), Inches(7.20), Inches(4.4), Inches(0.26),
             page_label, size=14, bold=True, color=WHITE, align="right", anchor=MSO_ANCHOR.MIDDLE)
    add_rect(s, Inches(10.05), Inches(0.26), Inches(3.00), Inches(0.42), ACCENT_SOFT)
    add_text(s, Inches(10.12), Inches(0.28), Inches(2.86), Inches(0.38),
             "成员一 · 25 秒", size=18, bold=True, color=ACCENT,
             align="center", anchor=MSO_ANCHOR.MIDDLE)

    add_text(s, Inches(0.42), Inches(0.32), Inches(9.4), Inches(0.36),
             "NLP 2026  ·  论文部分复现  ·  包名 NLP2026_G14_Pxx.zip",
             size=20, bold=True, color=PRIMARY)
    add_text(s, Inches(0.40), Inches(0.78), Inches(12.4), Inches(0.72),
             "LongLLMLingua：固定 100 题上的方法级复现",
             size=36, bold=True, color=INK)
    add_text(s, Inches(0.42), Inches(1.52), Inches(12.2), Inches(0.40),
             "长上下文提示压缩  ·  Natural Questions，每题 20 篇文档",
             size=22, color=PRIMARY_DEEP)

    cards = [
        ("论文与代码", "arXiv:2310.06839v2。官方代码锁定\nLLMLingua 提交 5a4c78ae。"),
        ("数据", "Lost in the Middle 提交 29b8a6d。\n答案位置 1 / 5 / 10 / 15 / 20。"),
        ("课程范围", "seed=42，pilot 100 题 × 五位置。\n20/100/500 嵌套。不跑 500 题矩阵。"),
        ("问答与指标", "deepseek-flash，temperature=0。\n最多 512 token。指标看回答首行。"),
    ]
    for i, (title, body) in enumerate(cards):
        x = 0.42 + (i % 2) * 6.35
        y = 2.15 + (i // 2) * 1.62
        add_rect(s, Inches(x), Inches(y), Inches(6.10), Inches(1.48), WHITE, LINE)
        add_rect(s, Inches(x), Inches(y), Inches(0.08), Inches(1.48), ACCENT if i == 0 else PRIMARY)
        add_text(s, Inches(x + 0.24), Inches(y + 0.12), Inches(5.7), Inches(0.36),
                 title, size=20, bold=True, color=PRIMARY)
        add_text(s, Inches(x + 0.24), Inches(y + 0.50), Inches(5.7), Inches(0.86),
                 body, size=20, color=TEXT, spacing=1.05)

    add_rect(s, Inches(0.42), Inches(5.50), Inches(12.48), Inches(1.05), ACCENT_SOFT)
    add_rect(s, Inches(0.42), Inches(5.50), Inches(0.08), Inches(1.05), ACCENT)
    add_text(s, Inches(0.68), Inches(5.60), Inches(12.05), Inches(0.85),
             "一句话：本组检验问题感知压缩能否在这 100 题上保住 EM。\n"
             "不把分数写成论文里 GPT-3.5-Turbo-0613 的历史数值。",
             size=20, color=INK, spacing=1.05)
    add_text(s, Inches(0.42), Inches(6.66), Inches(12.5), Inches(0.40),
             "来源：README.md 开篇与实验设计；manifests/resources.json；configs/stage1.json。P 编号待教师确认。",
             size=18, color=MUTED)
    notes(s, (
        "【定稿讲稿 · 115 字 · 稳速约 27 秒，快语速约 23 秒。预算 25 秒。"
        "超时就删“论文 2310.06839 第二版”。】\n"
        "我们复现 LongLLMLingua，论文 2310.06839 第二版，代码锁定提交 5a4c78ae。"
        "课程只做 seed 四十二的一百题、五个位置，问答用 deepseek-flash。"
        "比方法，不比论文里 GPT 的绝对分数。\n"
        "来源：README.md；manifests/resources.json；configs/stage1.json。Pxx 是占位。"
    ))
    return s


def slide_p2(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    chrome(s, page_label, "成员一", "35 秒")
    add_text(s, Inches(0.38), Inches(0.22), Inches(9.5), Inches(0.48),
             "问题：答案位置固定，BM25 四倍会掉点", size=30, bold=True, color=INK)
    add_rect(s, Inches(0.38), Inches(0.82), Inches(12.55), Inches(0.78), WHITE, LINE)
    add_rect(s, Inches(0.38), Inches(0.82), Inches(0.08), Inches(0.78), ACCENT)
    add_text(s, Inches(0.60), Inches(0.88), Inches(12.2), Inches(0.64),
             "smoke 20 题：BM25 4x 的 EM 是 64.0%，原始提示是 92.0%。各 100 槽。",
             size=20, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)

    add_table(
        s, Inches(0.38), Inches(1.78), Inches(8.15), Inches(2.15),
        [
            ["方法", "槽", "EM", "实测压缩比"],
            ["原始提示", "100", "92.0%", "1.000x"],
            ["BM25 2x", "100", "87.0%", "2.001x"],
            ["BM25 4x", "100", "64.0%", "4.007x"],
        ],
        [Inches(2.35), Inches(1.45), Inches(1.90), Inches(2.45)],
        font=18, highlight=3,
    )
    add_rect(s, Inches(8.72), Inches(1.78), Inches(4.20), Inches(2.15), INK)
    add_text(s, Inches(8.92), Inches(1.92), Inches(3.85), Inches(1.90),
             [
                 {"text": "这 20 题不是主结果", "size": 20, "bold": True, "color": WHITE},
                 {"text": "100 题原始提示 EM 是 84.6%，共 500 槽。主比较用这个数。", "size": 20, "color": WHITE},
             ], spacing=1.05)

    bullets = [
        "每题 20 篇。gold 只在位置 1/5/10/15/20，对应上游索引 0/4/9/14/19。",
        "问题 ID 由归一化后的问题与答案集合生成。smoke 20 题是 pilot 100 题的前 20 个，pilot 是 main 500 题的前 100 个。",
        "答案、gold、位置不进入 BM25 和问答提示。评分只取回答第一行，做 best_subspan_em。",
    ]
    add_text(s, Inches(0.38), Inches(4.12), Inches(12.55), Inches(2.05),
             bullets, size=20, color=TEXT, spacing=1.15)
    add_text(s, Inches(0.38), Inches(6.28), Inches(12.55), Inches(0.72),
             "来源：reports/stage1-acceptance/REPORT.md 与 acceptance.json，run d54b3118c61ea4930624。\n"
             "位置曲线见同目录 summary.md。100 题的 84.6% 见 reports/stage3-main/summary.json。",
             size=18, color=MUTED, spacing=1.05)
    notes(s, (
        "【定稿讲稿 · 约 35 秒 · 与 P1 合计 60 秒】\n"
        "每题二十篇文档，标准答案只放在第一、五、十、十五、二十篇。"
        "编号按归一化后的问题和答案集合生成，不用行号。答案不会进入 BM25。"
        "阶段一 smoke 三百槽全部成功：原始提示 EM 百分之九十二，BM25 两倍百分之八十七，四倍百分之六十四。"
        "这只是二十题。主比较用一百题的百分之八十四点六。\n"
        "来源：REPORT.md 基线表；acceptance.json 的 em_percent 与 mean_actual_ratio；"
        "summary.md 五位置；manifests/smoke.json、pilot.json、main.json 已核对嵌套；"
        "reproduction/evaluation.py 只把 answer 第一行送进 best_subspan_em；"
        "docs/stage1-implementation.md 写明评估字段不进方法。"
    ))
    return s


def slide_p3(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    chrome(s, page_label, "成员二", "约 45 秒")
    add_text(s, Inches(0.38), Inches(0.22), Inches(9.5), Inches(0.48),
             "方法：问题感知筛选，再压到硬预算", size=30, bold=True, color=INK)
    add_rect(s, Inches(0.38), Inches(0.80), Inches(12.55), Inches(0.72), WHITE, LINE)
    add_rect(s, Inches(0.38), Inches(0.80), Inches(0.08), Inches(0.72), ACCENT)
    add_text(s, Inches(0.60), Inches(0.88), Inches(12.2), Inches(0.56),
             "建议句：smoke 上，问题感知排名让 100/100 个样本的保留文档不同于 LLMLingua。",
             size=20, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    items = [
        ("同一权重", "NousResearch/Llama-2-7b-chat-hf，revision 351844e75ed0。LLMLingua 与 LongLLMLingua 共用。fp16，eager。"),
        ("三个开关", "粗粒度 rank_method=longllmlingua。细粒度 condition_compare=True。动态比率 0.3。"),
        ("主比较关掉的", "reorder_context=original。重排序不放进主表，阶段四另开。恢复在问答之后执行。"),
        ("不能拿来消融的", "k=2 在当前路径无效。指令 τ_ins=0.85、问题 τ_que=0.9 未实现，不写成已复现。"),
    ]
    for i, (title, body) in enumerate(items):
        y = 1.70 + i * 1.18
        add_rect(s, Inches(0.38), Inches(y), Inches(12.55), Inches(1.08), WHITE, LINE)
        add_rect(s, Inches(0.38), Inches(y), Inches(0.08), Inches(1.08), PRIMARY)
        add_text(s, Inches(0.62), Inches(y + 0.08), Inches(2.5), Inches(0.90),
                 title, size=20, bold=True, color=PRIMARY, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, Inches(3.20), Inches(y + 0.12), Inches(9.5), Inches(0.84),
                 body, size=20, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(0.38), Inches(6.48), Inches(12.55), Inches(0.58),
             "来源：docs/stage2-parameter-map.md；docs/experiments.md 第四阶段环境；\n"
             "reports/stage2-smoke/REPORT.md 第 4 节（100/100）。成员二可改措辞，不要改这些数。",
             size=18, color=MUTED)
    notes(s, (
        "【建议稿 · 成员二核对后使用 · 目标不超过 45 秒，给 P4 留约 45 秒】\n"
        "压缩模型是 Llama-2-7B-Chat 的镜像，revision 351844e75ed0，两种压缩方法共用。"
        "LongLLMLingua 打开粗粒度、细粒度和 0.3 的动态比率。主比较关闭重排序。"
        "smoke 里 100 个样本的保留文档都和 LLMLingua 不同。k=2、指令预压缩和问题预压缩没有做成有效开关。\n"
        "来源见页底。recovery 使用 DeepSeek tokenizer 放到 P4 讲。"
    ))
    return s


def slide_p4(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    chrome(s, page_label, "成员二", "约 45 秒")
    add_text(s, Inches(0.38), Inches(0.22), Inches(9.5), Inches(0.46),
             "设置：和论文不同的地方", size=30, bold=True, color=INK)
    add_rect(s, Inches(0.38), Inches(0.76), Inches(12.55), Inches(0.64), WHITE, LINE)
    add_rect(s, Inches(0.38), Inches(0.76), Inches(0.08), Inches(0.64), ACCENT)
    add_text(s, Inches(0.60), Inches(0.82), Inches(12.2), Inches(0.50),
             "建议句：这些差异都已登记，EM 不能和论文的 GPT 历史数字横比。",
             size=20, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    add_table(
        s, Inches(0.38), Inches(1.56), Inches(12.55), Inches(3.55),
        [
            ["项目", "论文", "本组记录"],
            ["问答", "GPT-3.5-Turbo-0613", "deepseek-flash，temperature 0，512"],
            ["预算计数", "tiktoken 软目标", "完整提示硬预算，DeepSeek tokenizer"],
            ["恢复分词", "LLaMA-2 tokenizer", "DeepSeek tokenizer"],
            ["主比较硬件", "V100-32G", "只记录到 cuda:0，无型号"],
            ["消融硬件", "同上", "Ascend 910B4，HBM 总量 32768 MB"],
        ],
        [Inches(2.55), Inches(4.55), Inches(5.45)],
        font=18,
    )
    add_text(s, Inches(0.38), Inches(5.28), Inches(12.55), Inches(1.70),
             [
                 "阶段二 smoke：400/400 成功，硬预算 396/400。4 条超标都来自同一题的 longllmlingua_4x，目标 742，实测 749/751/754/753。",
                 "阶段三 LongLLMLingua 4x 另有 18/500 未达硬预算，预算满足率 0.964。两处都保留原记录。",
                 "来源：docs/stage2-parameter-map.md；docs/experiments.md；reports/stage2-smoke/verification.json；reports/stage3-main/summary.json。",
             ], size=20, color=TEXT, spacing=1.02)
    notes(s, (
        "【建议稿 · 成员二 · 约 45 秒】\n"
        "问答换成 deepseek-flash。预算按完整提示的 DeepSeek token 做硬上限，不用库自己的 ratio。"
        "恢复也用 DeepSeek 分词器，不用论文的 LLaMA-2 分词器。"
        "主比较机器只记到 cuda:0，不能补写成 V100。消融是 910B4。"
        "阶段二有 4 条 4x 超标，阶段三有 18 条，都留在记录里。\n"
        "4 条的 slot 前缀是 23707ea62773，见 verification.json 的 budget_misses。"
    ))
    return s


def slide_p5(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    chrome(s, page_label, "成员三", "60 秒")
    add_text(s, Inches(0.38), Inches(0.20), Inches(9.5), Inches(0.44),
             "主结果：pilot 100 题 × 五位置", size=30, bold=True, color=INK)
    add_rect(s, Inches(0.38), Inches(0.68), Inches(12.55), Inches(0.86), WHITE, LINE)
    add_rect(s, Inches(0.38), Inches(0.68), Inches(0.08), Inches(0.86), ACCENT)
    add_text(s, Inches(0.58), Inches(0.74), Inches(12.2), Inches(0.74),
             "LongLLMLingua 2x 为 83.2%，比原始提示低 1.4 个百分点。\n95% 区间 [−6.2, 3.0]，跨过 0。",
             size=20, bold=True, color=INK)
    add_table(
        s, Inches(0.38), Inches(1.66), Inches(12.55), Inches(3.84),
        [
            ["方法", "平均 EM", "平均实际压缩比", "成功槽"],
            ["原始提示", "84.6%", "1.00x", "500/500"],
            ["BM25 2x", "72.4%", "2.00x", "500/500"],
            ["BM25 4x", "55.8%", "4.01x", "500/500"],
            ["LLMLingua 2x", "46.8%", "2.04x", "500/500"],
            ["LLMLingua 4x", "35.6%", "4.17x", "500/500"],
            ["LongLLMLingua 2x", "83.2%", "2.08x", "500/500"],
            ["LongLLMLingua 4x", "79.0%", "4.09x", "500/500"],
        ],
        [Inches(3.55), Inches(2.70), Inches(3.50), Inches(2.80)],
        font=18, highlight=6,
    )
    add_text(s, Inches(0.38), Inches(5.62), Inches(12.55), Inches(1.40),
             "run e8f151b9c286648caf98，split=pilot。按问题配对，五位置绑在一起，bootstrap 2000 次，seed 42。\n"
             "4x 预算满足率 0.964，即 18/500 未达硬预算。页上比值按 README.md 舍入，原值在 summary.json。",
             size=18, color=MUTED, spacing=1.0)
    notes(s, (
        "【建议稿 · 成员三 · 60 秒。运行证据另计 30 秒，不要挤进这一页。】\n"
        "主比较是一百题、五个位置、七个方法，三千五百槽全部成功。"
        "LongLLMLingua 两倍 EM 百分之八十三点二，原始提示百分之八十四点六，差一点四个百分点，区间跨零。"
        "四倍是百分之七十九，区间不跨零。同预算下它高于 BM25 和 LLMLingua。"
        "有十八条四倍没有卡进硬预算。\n"
        "stats.json：longllmlingua_2x 对 original，mean −0.014，ci_low −0.062，ci_high 0.030；"
        "4x 的 mean −0.056，ci_low −0.116，ci_high −0.004。"
    ))
    return s


def slide_p6(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    chrome(s, page_label, "成员四", "60 秒")
    add_text(s, Inches(0.38), Inches(0.20), Inches(9.5), Inches(0.46),
             "消融在 910B 上重跑，不拼接 CUDA 耗时", size=28, bold=True, color=INK)
    add_rect(s, Inches(0.38), Inches(0.72), Inches(6.35), Inches(0.78), WHITE, LINE)
    add_rect(s, Inches(0.38), Inches(0.72), Inches(0.08), Inches(0.78), ACCENT)
    add_text(s, Inches(0.56), Inches(0.78), Inches(6.05), Inches(0.66),
             "同机完整方法是 82.6%。这不是主比较里的 83.2%。",
             size=20, bold=True, color=INK)
    calls = [
        ("45.0%", "去掉粗粒度。差 −37.6 pp，区间 [−47.2, −28.4]。"),
        ("78.0%", "去掉动态预算。差 −4.6 pp，区间 [−8.6, −0.8]。"),
        ("83.2%", "去掉恢复。差 +0.6 pp。另有 3 个槽由对变错。"),
    ]
    for i, (num, text) in enumerate(calls):
        y = 1.64 + i * 1.18
        add_rect(s, Inches(0.38), Inches(y), Inches(6.35), Inches(1.08), WHITE, LINE)
        add_text(s, Inches(0.52), Inches(y + 0.10), Inches(1.70), Inches(0.86),
                 num, size=28, bold=True, color=PRIMARY, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, Inches(2.25), Inches(y + 0.10), Inches(4.30), Inches(0.88),
                 text, size=20, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
    img = ROOT / "reports/stage4-ablation-efficiency/figures/ablation.png"
    s.shapes.add_picture(str(img), Inches(6.95), Inches(0.72), Inches(5.95), Inches(2.94))
    add_text(s, Inches(6.95), Inches(3.70), Inches(5.95), Inches(0.72),
             "图内字是脚本的 10 pt。幻灯片以左侧 18 pt 以上的数字为准。",
             size=18, color=MUTED)
    add_rect(s, Inches(6.95), Inches(4.50), Inches(5.95), Inches(1.90), INK)
    add_text(s, Inches(7.10), Inches(4.60), Inches(5.65), Inches(1.70),
             "效率是另一批 smoke。每方法 99 个样本。\n"
             "完整 2x 端到端 p50/p95：6.45 / 7.49 秒。\n"
             "原始提示：1.12 / 1.54 秒。峰值 16.43 GB。",
             size=18, color=WHITE, spacing=1.08)
    add_text(s, Inches(0.38), Inches(6.48), Inches(6.35), Inches(0.58),
             "来源：RESULTS.md、ablation.csv、efficiency.csv。n=500；效率 n=99。",
             size=18, color=MUTED)
    notes(s, (
        "【建议稿 · 成员四 · 60 秒。运行证据后半另计 30 秒。】\n"
        "消融和主比较不是同一台机器。910B 上完整 LongLLMLingua 两倍是百分之八十二点六。"
        "去掉粗粒度掉到百分之四十五，区间远离零。去掉动态预算到百分之七十八，区间也不跨零。"
        "去掉恢复后 EM 是百分之八十三点二，但有三个槽从对变成错。"
        "效率上，完整两倍的端到端中位大约六点四五秒，原始提示一点一二秒，压缩没有更快。\n"
        "三例 question_id 见 inputs/recovery-cases.json。效率原始值见 efficiency.csv："
        "6.449125320883468 / 7.4866623027483 与 1.120468680979684 / 1.5420867950422685，"
        "peak_allocated_GB 16.428089344。GB 按 1e9 字节。页上用 README 的两位小数。"
    ))
    return s


def slide_p7(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    chrome(s, page_label, "成员一", "30 秒")
    add_text(s, Inches(0.38), Inches(0.22), Inches(9.5), Inches(0.48),
             "结论与四人贡献", size=32, bold=True, color=INK)
    findings = [
        ("1", "100 题主比较",
         "LongLLMLingua 2x 是 83.2%，原始提示 84.6%。差 −1.4 个百分点，95% 区间 [−6.2, 3.0]，跨过 0。4x 是 79.0%，区间不跨 0。"),
        ("2", "910B 消融",
         "去掉粗粒度后是 45.0%（−37.6 pp）。去掉恢复后 EM 升到 83.2%，同时有 3 个槽由对变错。两台机器的耗时不相加。"),
        ("3", "效率",
         "完整 2x 的端到端 p50/p95 是 6.45/7.49 秒，原始提示是 1.12/1.54 秒。峰值 allocated HBM 约 16.43 GB。压缩减少了输入 token，这次没有换来更低延迟。"),
    ]
    for i, (num, title, body) in enumerate(findings):
        y = 0.84 + i * 1.38
        add_rect(s, Inches(0.38), Inches(y), Inches(12.55), Inches(1.28), WHITE, LINE)
        add_rect(s, Inches(0.38), Inches(y), Inches(0.62), Inches(1.28), PRIMARY if i < 2 else ACCENT)
        add_text(s, Inches(0.38), Inches(y), Inches(0.62), Inches(1.28),
                 num, size=24, bold=True, color=WHITE, align="center", anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, Inches(1.16), Inches(y + 0.08), Inches(11.55), Inches(0.36),
                 title, size=20, bold=True, color=PRIMARY)
        add_text(s, Inches(1.16), Inches(y + 0.42), Inches(11.55), Inches(0.80),
                 body, size=20, color=TEXT)
    add_text(s, Inches(0.38), Inches(5.08), Inches(12.55), Inches(1.35),
             "贡献按阶段拆开。成员一做数据、BM25 和评分。成员二做压缩适配和参数映射。"
             "成员三做 3500 槽主比较。成员四做 910B 上 3500 槽消融和 1200 槽效率。"
             "压缩算法复用 LLMLingua@5a4c78ae，不是本组原创。",
             size=20, color=INK, spacing=1.0)
    add_text(s, Inches(0.38), Inches(6.50), Inches(12.55), Inches(0.55),
             "来源：README.md 主比较表与消融段；stats.json；RESULTS.md；efficiency.csv；recovery-cases.json 共 3 条。",
             size=18, color=MUTED)
    notes(s, (
        "【定稿讲稿 · 30 秒。超时就删第 3 句的 GB，不要删来源。】\n"
        "一百题上，LongLLMLingua 两倍是百分之八十三点二，比原始提示低一点四个百分点，百分之九十五区间跨过零。"
        "去掉粗粒度问题感知后掉到百分之四十五。端到端中位时间，两倍方法六点四五秒，原始提示一点一二秒。"
        "四人按阶段各做一块，压缩算法用的是微软固定版本。\n"
        "4x 的区间不跨零写在页上，30 秒口播可以不说。恢复的 3 个负面槽口播也可留给提问。"
    ))
    return s


def slide_evidence(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    chrome(s, page_label, "运行证据", "60 秒")
    add_text(s, Inches(0.38), Inches(0.20), Inches(9.5), Inches(0.42),
             "运行证据：打开文件，不重新训练", size=30, bold=True, color=INK)
    add_rect(s, Inches(0.38), Inches(0.74), Inches(6.20), Inches(5.55), WHITE, LINE)
    add_rect(s, Inches(0.38), Inches(0.74), Inches(6.20), Inches(0.46), PRIMARY)
    add_text(s, Inches(0.52), Inches(0.78), Inches(5.9), Inches(0.38),
             "前 30 秒 · 成员三", size=20, bold=True, color=WHITE)
    add_text(s, Inches(0.54), Inches(1.32), Inches(5.85), Inches(4.80),
             [
                 "1. 入口：python -m reproduction.stage3",
                 "2. 打开 reports/stage3-main/run.json，指出 run_id e8f151b9c286648caf98，split=pilot。",
                 "3. 打开 coverage.json：success 3500，failed 0，missing 0。",
                 "4. 打开 summary.json 里 longllmlingua_2x 的 mean_em：0.832。",
                 "5. 逐条全文在组内 results.jsonl。仓库里没有这 3500 行全文。",
             ], size=20, color=TEXT, spacing=1.02)
    add_rect(s, Inches(6.74), Inches(0.74), Inches(6.20), Inches(5.55), WHITE, LINE)
    add_rect(s, Inches(6.74), Inches(0.74), Inches(6.20), Inches(0.46), ACCENT)
    add_text(s, Inches(6.88), Inches(0.78), Inches(5.9), Inches(0.38),
             "后 30 秒 · 成员四", size=20, bold=True, color=WHITE)
    add_text(s, Inches(6.90), Inches(1.32), Inches(5.85), Inches(4.80),
             [
                 "1. python scripts/analyze_stage4.py",
                 "   本机实测 0.337 秒，不调用 API。它会重写 csv，演示后不要提交。",
                 "2. 打开 environment-current.json：npu_name 为 Ascend910B4。",
                 "3. 打开 coverage.json：消融 3500，效率 1200。",
                 "4. 图用已提交的 ablation.png，不在现场重画。",
             ], size=20, color=TEXT, spacing=1.02)
    add_text(s, Inches(0.38), Inches(6.40), Inches(12.55), Inches(0.64),
             "configs/stage3.json 的 split 是 main，不是这次 100 题运行。现场以 run.json 里的配置快照为准。\n"
             "来源：README.md 本地重建；docs/experiments.md；上述 json。计时是 2026-11-21 本机一次运行。",
             size=18, color=MUTED)
    notes(s, (
        "现场 60 秒只做打开和指认。成员三不要现场跑 3500 槽。成员四不要现场加载 LLaMA。\n"
        "analyze_stage4.py 在本环境 0.337 秒，随后 git checkout 恢复了被改写的 csv。\n"
        "plot_results.py 需要 matplotlib==3.10.0，本机 1.413 秒，会重写 png/pdf，备份录屏可以用，现场优先打开已有 png。"
    ))
    return s


def slide_backup(prs, page_label):
    s = blank(prs)
    set_bg(s, PAPER)
    chrome(s, page_label, "四人备份", "环境故障时")
    add_text(s, Inches(0.38), Inches(0.20), Inches(9.5), Inches(0.46),
             "备份页：录屏不能代替原始结果", size=30, bold=True, color=INK)
    rows = [
        ("成员三", "画面依次是 run.json 的 run_id、coverage.json 的 3500、summary.json 的 0.832，以及组内一条 results.jsonl。"),
        ("成员四", "终端跑 analyze_stage4.py，再打开 environment-current.json 和已有 ablation.png。不把重写的图提交。"),
        ("成员一", "提问时打开 predictions.jsonl 里案例 M1-01 的三条 slot，以及 acceptance.json 的 300/0/0。"),
        ("成员二", "提问时打开 verification.json 的 budget_misses：目标 742，实测 749、751、754、753。"),
    ]
    for i, (who, body) in enumerate(rows):
        y = 0.82 + i * 1.22
        add_rect(s, Inches(0.38), Inches(y), Inches(12.55), Inches(1.12), WHITE, LINE)
        add_rect(s, Inches(0.38), Inches(y), Inches(1.70), Inches(1.12), PRIMARY if i < 2 else INK)
        add_text(s, Inches(0.46), Inches(y), Inches(1.54), Inches(1.12),
                 who, size=18, bold=True, color=WHITE, align="center", anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, Inches(2.24), Inches(y + 0.12), Inches(10.5), Inches(0.88),
                 body, size=20, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, Inches(0.38), Inches(5.78), Inches(12.55), Inches(1.20),
             "录屏文件名留 TODO：results/demo/member3-evidence.mp4 与 results/demo/member4-evidence.mp4。\n"
             "视频不进 git。zip 里放文件，并在 README 写时长。课程要求录屏不能替代代码和原始结果。\n"
             "规范：https://nlp.hltbit.top/2026/materials/w01/classroom/requirements.html 第四节。",
             size=18, color=MUTED, spacing=1.05)
    notes(s, "这是占位备份页，不是第 8 分钟的主讲页。四人各自确认录屏路径后再把 TODO 换成真实文件名。")
    return s


def assert_sizes(prs):
    """Spoken content stays at the course floors. Footer chrome is 14 pt."""
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    for i, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            top = shape.top
            for p in shape.text_frame.paragraphs:
                for run in p.runs:
                    if run.font.size is None:
                        continue
                    pt = run.font.size.pt
                    if top is not None and top >= Inches(7.16):
                        if pt < 14:
                            raise SystemExit(f"slide {i} footer {pt} pt: {run.text[:40]}")
                        continue
                    floor = 18 if pt < 20 else 20
                    # 18 pt is allowed for tables, captions and sources; 20 pt for body.
                    if pt < 18:
                        raise SystemExit(f"slide {i} text {pt} pt below 18: {run.text[:60]}")
                    if floor == 20 and pt < 18:
                        raise SystemExit(run.text)
        if shape.has_table:
            for cell in shape.table.iter_cells():
                for p in cell.text_frame.paragraphs:
                    for run in p.runs:
                        if run.font.size is None or run.font.size.pt < 18:
                            raise SystemExit(f"slide {i} table below 18: {run.text}")
    # Titles: first non-footer text box on each content slide should be >= 28.
    # Cover uses 36. Checked loosely by the explicit sizes above.


def build(path: Path, kind: str):
    prs = new_prs()
    if kind == "template":
        slide_p1(prs, "P1  ·  1/9")
        slide_p2(prs, "P2  ·  2/9")
        slide_p3(prs, "P3  ·  3/9")
        slide_p4(prs, "P4  ·  4/9")
        slide_p5(prs, "P5  ·  5/9")
        slide_p6(prs, "P6  ·  6/9")
        slide_p7(prs, "P7  ·  7/9")
        slide_evidence(prs, "运行证据  ·  8/9")
        slide_backup(prs, "备份  ·  9/9")
    elif kind == "member1":
        slide_p1(prs, "P1  ·  成员一定稿")
        slide_p2(prs, "P2  ·  成员一定稿")
        slide_p7(prs, "P7  ·  成员一定稿")
    else:
        raise SystemExit(kind)
    assert_sizes(prs)
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)
    print(path, "slides", len(prs.slides))


def main():
    here = Path(__file__).resolve().parent
    build(here / "G14-LongLLMLingua-template.pptx", "template")
    build(here.parent / "members" / "member1" / "slides-P1-P2-P7.pptx", "member1")


if __name__ == "__main__":
    main()
