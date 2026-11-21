from pathlib import Path
import json,csv,shutil,hashlib,re,math
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image,ImageDraw,ImageFont
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
R=Path(__file__).parent; S=R/'sources'; F=R/'figures'
# Input source snapshots are already frozen under sources/. No repository access is needed to rebuild.
summary=json.loads((S/'g1/summary.json').read_text()); stats=json.loads((S/'stage3-stats-remote.json').read_text());cases=json.loads((S/'cases-verified.json').read_text())
ab=list(csv.DictReader((S/'g2/ablation.csv').open()));eff=list(csv.DictReader((S/'g2/efficiency.csv').open())); heads=json.loads((S/'branch-heads.json').read_text())
assert json.loads((S/'g2/stats.json').read_text())==stats
assert list(csv.DictReader((S/'stage4-ablation-remote.csv').open()))==ab
assert [m['mean_em'] for m in summary['methods']]==[.846,.724,.558,.468,.356,.832,.790]
assert json.loads((S/'stage2-acceptance-remote.json').read_text())['budget_satisfied']==396
# Honest, source-derived position chart. No invented observations.
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def ft(n):return ImageFont.truetype(font,n)
im=Image.new('RGB',(1800,510),'white');d=ImageDraw.Draw(im)
L,T,W,H=130,45,1070,360
for y in [30,40,50,60,70,80,90]:
 py=T+H-(y-30)/60*H;d.line((L,py,L+W,py),fill='#dce1e6',width=2);d.text((L-70,py-17),str(y),font=ft(28),fill='#333333')
for i,p in enumerate([1,5,10,15,20]):
 x=L+i*W/4;d.text((x-15,T+H+15),str(p),font=ft(28),fill='#333333')
d.text((L,4),'EM (%)',font=ft(28),fill='#333333');d.text((430,465),'Gold document position (1-based)',font=ft(28),fill='#333333')
for j,(m,label,color) in enumerate([('original','Original','#333333'),('longllmlingua_2x','LongLLMLingua 2x','#20668b'),('longllmlingua_4x','LongLLMLingua 4x','#458d76'),('bm25_4x','BM25 4x','#bb7941'),('llmlingua_4x','LLMLingua 4x','#895a85')]):
 vals=[g['best_subspan_em']*100 for g in summary['groups'] if g['method']==m]
 pts=[(L+i*W/4,T+H-(v-30)/60*H) for i,v in enumerate(vals)]
 d.line(pts,fill=color,width=5)
 for x,y in pts:d.ellipse((x-6,y-6,x+6,y+6),fill=color)
 yy=72+j*70;d.line((1280,yy+16,1350,yy+16),fill=color,width=5);d.text((1370,yy),label,font=ft(28),fill='#333333')
im.save(F/'stage3-position.png')
# DOCX, editable text/tables, not a page-image document.
doc=Document();sec=doc.sections[0];sec.page_height=Cm(29.7);sec.page_width=Cm(21)
sec.top_margin=Cm(1.9);sec.bottom_margin=Cm(1.8);sec.left_margin=Cm(2.15);sec.right_margin=Cm(2.15);sec.header_distance=Cm(.8);sec.footer_distance=Cm(.8)
styles=doc.styles
for name in ['Normal','Body Text']:
 st=styles[name];st.font.name='Noto Serif CJK SC';st.font.size=Pt(10.5);st._element.rPr.rFonts.set(qn('w:eastAsia'),'Noto Serif CJK SC');st.paragraph_format.line_spacing=1.16;st.paragraph_format.space_after=Pt(5)
for name,size in [('Title',19),('Heading 1',13),('Heading 2',11.5)]:
 st=styles[name];st.font.name='Noto Sans CJK SC';st.font.size=Pt(size);st.font.color.rgb=RGBColor.from_string('17364D');st._element.rPr.rFonts.set(qn('w:eastAsia'),'Noto Sans CJK SC');st.paragraph_format.space_before=Pt(8);st.paragraph_format.space_after=Pt(6)
header=sec.header.paragraphs[0];header.text='北京理工大学 · 自然语言处理课程　|　G14 方法级复现报告';header.style='Normal'
for r in header.runs:r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string('666666')
f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER
f.add_run('G14　·　');fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');f._p.append(fld)
for r in f.runs:r.font.size=Pt(8)
md=[]
NEXT_PAGE=False
def para(t,size=None,bold=False):
 p=doc.add_paragraph();p.paragraph_format.widow_control=True
 r=p.add_run(t);r.bold=bold
 if size:r.font.size=Pt(size)
 md.append(t+'\n');return p
def h(t,l=1):
 global NEXT_PAGE
 p=doc.add_heading(t,l)
 if NEXT_PAGE:p.paragraph_format.page_break_before=True;NEXT_PAGE=False
 md.append('#'*(l+1)+' '+t+'\n')
def title(t):
 p=doc.add_paragraph(t,'Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;md.append('# '+t+'\n')
def caption(t):
 p=para(t,8.5);p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_after=Pt(6);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 for r in p.runs:r.font.color.rgb=RGBColor.from_string('555555')
def table(headers,rows,widths=None):
 t=doc.add_table(rows=1, cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 if widths:
  for c,w in zip(t.columns,widths):c.width=Cm(w)
 for c,txt in zip(t.rows[0].cells,headers):c.text=str(txt)
 for row in rows:
  for c,txt in zip(t.add_row().cells,row):c.text=str(txt)
 for ri,row in enumerate(t.rows):
  trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
  for ci,c in enumerate(row.cells):
   if widths:c.width=Cm(widths[ci])
   c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   tcpr=c._tc.get_or_add_tcPr();marg=OxmlElement('w:tcMar')
   for side in ['top','bottom','left','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),'55' if side in ['top','bottom'] else '70');el.set(qn('w:type'),'dxa');marg.append(el)
   tcpr.append(marg)
   if ri==0:
    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E9EFF3');tcpr.append(shade)
   for p in c.paragraphs:
    p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.05
    for r in p.runs:r.font.size=Pt(9);r.bold=(ri==0)
  if ri==0:trpr.append(OxmlElement('w:tblHeader'))
 md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n')
 return t

def image(name,width):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(0);p.add_run().add_picture(str(F/name),width=Cm(width));md.append(f'![图]({"figures/"+name})\n')
def page():
 global NEXT_PAGE
 NEXT_PAGE=True;md.append('\n<!-- PAGE BREAK -->\n')
def link(label,url):
 p=doc.add_paragraph();p.paragraph_format.space_after=Pt(5);p.paragraph_format.line_spacing=1.08
 rel=p.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
 hy=OxmlElement('w:hyperlink');hy.set(qn('r:id'),rel);r=OxmlElement('w:r');pr=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'225D82');pr.append(color);sz=OxmlElement('w:sz');sz.set(qn('w:val'),'18');pr.append(sz);r.append(pr);text=OxmlElement('w:t');text.text=label;r.append(text);hy.append(r);p._p.append(hy);md.append(f'[{label}]({url})\n')
# BODY 1
title('LongLLMLingua 方法级复现报告')
p=para('BIT 自然语言处理课程　G14\n2026年11月21日（Asia/Shanghai）',10);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
para('摘要　针对长上下文问答中的冗余与位置偏置，本文整理并核验 G14 已有的 LongLLMLingua 复现记录。CUDA pilot 100题上，2×压缩 EM 为83.2%，原始提示为84.6%；按题配对的差值95%区间为[−6.2, +3.0]个百分点。独立NPU实验表明问题感知文档筛选作用较大，但本批次未获得端到端加速。本文仅作既有实验汇编与离线核验，不声称重新推理。',10)
h('1　问题与复现范围')
para('LongLLMLingua[1]通过提高与问题相关的信息密度、调整信息位置并恢复输出子序列，缓解长提示的成本与性能问题。本文检验三个问题：同一问答设置下能否在2×/4×压缩后保留准确率；哪些模块贡献较大；输入缩短是否转化为整条流水线加速。')
para('范围限定为 Natural Questions 的20文档多文档问答版本[2,3]与固定 pilot 100题、五个gold位置；不覆盖原论文全部基准、训练或GPT-3.5绝对分数。问答模型替换为deepseek-flash，因此属于方法级而非逐数值复现。500题仅有清单，不作为已完成结果。')
h('2　方法与实现差异')
image('paper-figure2.png',15.7)
caption('图1　LongLLMLingua原方法框架。来源：Jiang等[1]，arXiv:2310.06839v2，图2（原图截取，非本组实验图）。')
para('粗粒度阶段以文档条件下的问题及restrict后缀的困惑度刻画相关性；细粒度阶段利用问题感知对比困惑度迭代选择token，并按文档排名动态分配预算。压缩后的提示送入黑盒问答模型，恢复模块在问答后对输出作子序列恢复[1,4]。')
para('主比较关闭文档重排序，以保留五位置干预；重排序另列消融。固定实现中的k=2映射在当前路径无效，τ_ins=0.85与τ_que=0.9预压缩未实现；动态比率0.3按排名线性分配，不能宣称与论文控制完全等价[5]。',10)
# BODY 2
page();h('3　数据、实现设置与公平性')
h('3.1　输入与版本固定',2)
para('数据总体为2655题。先按稳定ID排序，再用seed=42打乱，按嵌套前缀取得smoke 20题、pilot 100题和main 500题。每题20篇文档，gold置于1、5、10、15、20（从1计数）。一“槽”指题目×位置×方法，不是独立问题。输入仅含问题与文档ID、标题、正文；参考答案、gold标记和位置元数据不进入BM25或问答提示[6]。')
table(['项目','实际设置与来源'],[
 ['压缩器','LLMLingua与LongLLMLingua共用LLaMA-2-7B-Chat镜像权重；fp16、eager，迭代段长200'],
 ['问答API','deepseek-flash，非思考，temperature=0，max_tokens=512；历史真实记录保持不变'],
 ['计数与BM25','DeepSeek固定分词器；BM25 k1=1.5、b=0.75，unicode-word-lower-v1'],
 ['代码锁定','压缩库、数据模板与指标锁定提交；完整SHA见[9,10]，权重revision见附录A'],
 ['实际批次','阶段三为CUDA（仅cuda:0，型号未登记）；阶段四为Ascend910B4，不能合并硬件记录']
],[2.65,13.8])
h('3.2　指标、配对区间与预算边界',2)
para('主指标沿用首行best_subspan_em：先取模型回答第一行，再按上游规范化规则检查参考答案子串。它不是语义正确性判定，否定句提及答案也可能得1分。统计先在每题内平均五位置，再计算方法与original的题内差值；以题目为单位配对bootstrap 2000次，seed=42，保留同题全部位置，报告95%区间[7]。不能把500槽当作500道独立题。')
para('所有方法共享题单、可见输入、模板、问答设置与计数口径。硬预算目标为⌊原始完整提示本地token数/目标倍率⌋；压缩器最多3轮收紧预算，保留超标槽而不删失。库内context_budget=“+100”是软余量，不是最终合格标准。恢复只作用于回答，且采用DeepSeek分词器，区别于论文恢复粒度[5]。')
para('本地预算仅计提示文本，不含API聊天封装；阶段一300槽的API输入均比本地多4 token，不能将文本长度直接当账单。压缩率均值是逐槽比值的平均，不等于API输入总量之比。temperature=0和返回fingerprint亦不足以证明不可变模型快照。')
h('3.3　分阶段验收与证据等级',2)
table(['批次','槽数与结果','解释'],[
 ['阶段一 smoke','20×5×3=300；EM 92.0/87.0/64.0%','依次为original/BM25 2×/4×；预算300/300'],
 ['阶段二 smoke','20×5×4=400；预算396/400','canonical run a1bd…；4槽超标，不写成全合格'],
 ['历史离线审计','阶段一重评分不一致0；API 0','原记录耗时2.055秒，不是推理效率'],
 ['本机完整pytest','77/77、退出0；问答API 0','2026-11-21 17:46:58–17:47:02（北京时间）[12]']
],[3,6.0,7.45])
para('阶段一已记录五个公开gz校验和一致、20题跨位置文档集合与gold位置检查失败0。阶段二4个异常均为同题Long 4×，目标742，实测749/751/754/753 token；只报告现象，不推断完整缓存中尚未核实的根因。兼容旧分支stage_3的394/400不作为本报告口径。',10)
# BODY3
page();h('4　主比较：CUDA pilot 100题')
para('阶段三run e8f151b9c286648caf98共3500/3500槽：100题×5位置×7方法，每方法500槽。表1来自summary.json与stats.json[7]；置信区间直接引用既有按题配对统计，不以汇总均值伪造逐样本区间。下文Long为LongLLMLingua的简称。')
caption('表1　CUDA主比较。EM为%；Δ与95% CI为相对original的百分点（pp）；倍率为本地实测均值。')
rows=[];st={r['method']:r for r in stats['comparisons']}
labels=['Original','BM25 2×','BM25 4×','LLMLingua 2×','LLMLingua 4×','Long 2×','Long 4×']
for label,m in zip(labels,summary['methods']):
 s=st.get(m['method']); rows.append([label,f"{m['mean_em']*100:.1f}",'—' if not s else f"{s['mean']*100:+.1f}",'基线' if not s else f"[{s['ci_low']*100:+.1f}, {s['ci_high']*100:+.1f}]",f"{m['mean_actual_ratio']:.3f}×",f"{round(m['budget_satisfied_rate']*500)}/500"])
table(['方法','EM','Δ (pp)','95% CI (pp)','倍率','预算合格'],rows,[3.2,1.3,1.6,4.0,2.1,2.25])
para('同批次中，Long 2×较BM25 2×高10.8pp，Long 4×较BM25 4×高23.2pp；这是点估计差，表1区间的参照始终是original，不能误用作方法间差值的区间。LLMLingua在本设置明显较低，不能据此断言其在所有任务无效。')
para('Long 2×相对original为−1.4pp，95% CI [−6.2, +3.0]跨0：数据未明确区分两者，但未预设等效界值，不能写成“等效”或“无损”。Long 4×差−5.6pp，区间[−11.6, −0.4]，且18/500槽超预算；79.0%的EM是含这些超标槽的整体结果，不是严格4×预算下的无条件性能。')
image('stage3-position.png',16.3)
caption('图2　同一CUDA批次的分位置EM，每点100题。依据[7]的groups重绘；坐标从30%起，未绘方法见表1。')
para('图2将平均分拆至五个位置，避免只凭总体EM判断位置鲁棒性。当前原始提示未呈现典型的“中间最差”曲线；本文未另作位置差的显著性检验，不将其包装为复现了论文全部位置偏置现象。Long两档在所测位置均相对稳定，但只有100题与五个离散位置，不能推出一般长上下文鲁棒性。')
para('阶段一original 92.0%对应嵌套smoke 20题，阶段三84.6%对应pilot 100题及独立运行；两者不是同一分母。本文不跨批次拼接最优值，也不将小样本smoke结果作为CUDA主比较的基线。')
# BODY4
page();h('5　独立NPU消融与效率')
h('5.1　单因素消融',2)
para('阶段四run a9d2295195adde90484d基于pilot 100题、五位置，既有推理记录3500槽。参照是同机Long 2×的82.6%，不是CUDA的83.2%。表2中“无恢复”由已有恢复前得分离线派生，不额外计作500次推理[8]。')
caption('表2　NPU消融，各行500槽；Δ与按题配对95% CI均相对同批次完整Long 2×。')
ablab=['Original','Long 2×完整','无问题感知粗粒度','无问题感知细粒度','无动态预算','无restrict后缀','额外开启重排序','无恢复（离线派生）']
rows=[]
for label,r in zip(ablab,ab):
 ci='参照' if not r['ci_low_pp'] else f"[{float(r['ci_low_pp']):+.1f}, {float(r['ci_high_pp']):+.1f}]"
 rows.append([label,f"{float(r['em_percent']):.1f}",f"{float(r['delta_pp']):+.1f}",ci])
table(['方法/改动','EM (%)','Δ (pp)','95% CI (pp)'],rows,[6.6,2.2,2.3,5.35])
para('“无粗粒度”具体是将rank_method改为llmlingua，仍保留文档过滤，并非禁用整个筛选过程；其−37.6pp支持问题感知排序在本设置的重要性。去动态预算下降4.6pp。细粒度与restrict的区间跨0，证据不足以稳定排序小幅效果；主比较原本关闭重排序，此处为额外打开而非再次移除。')
para('关闭恢复的点估计反而高0.6pp，区间[0.0, +1.6]包含边界0；已有3条恢复由对变错记录，集中于2题。恢复不是单调有益模块，不能以原论文叙述替代本批次负面证据。')
h('5.2　端到端效率而非仅token节约',2)
para('效率独立run 2a7f4accf6127178a76b共1200槽（12方法×100个共同题目—位置槽）。每方法去掉同一个首槽后为99槽，位置分布19/20/20/20/20；它们不是99道独立题。表3保留主要参照，完整12行见随附CSV。')
caption('表3　NPU同批次耗时（秒）与峰值分配内存（十进制GB）；p50/p95分别为中位数/95分位。')
rows=[]
for k in ['original','bm25_2x','llmlingua_2x','longllmlingua_2x','longllmlingua_4x']:
 r=next(x for x in eff if x['method']==k);label={'original':'Original','bm25_2x':'BM25 2×','llmlingua_2x':'LLMLingua 2×','longllmlingua_2x':'Long 2×','longllmlingua_4x':'Long 4×'}[k]
 rows.append([label,f"{float(r['compression_seconds_p50']):.2f}",f"{float(r['api_seconds_p50']):.2f}",f"{float(r['total_pipeline_seconds_p50']):.2f} / {float(r['total_pipeline_seconds_p95']):.2f}",'未报' if not r['peak_allocated_GB'] else f"{float(r['peak_allocated_GB']):.2f}"])
table(['方法','压缩p50','API p50','端到端p50 / p95','峰值GB'],rows,[3.5,2.3,2.3,5.1,3.25])
para('端到端包含压缩、API与恢复及流程开销。Long 2×为6.45秒，对比original 1.12秒，没有端到端加速；压缩开销在本批次占主导。各组件分位数不能直接相加得到总分位数。效率不等于API账单，也不包含Cursor会话计时；CUDA与NPU耗时不可相加。')
# BODY5
page();h('6　真实案例与误差边界')
para('附录B列出S1-01至S1-13的真实首行、参考答案、token和分数，均来自阶段一run d54b3118c61ea4930624并与canonical预测核对一致。13槽仅覆盖4题，不是13道独立问题，亦非阶段三LongLLMLingua逐样本误差集。')
table(['真实槽索引','观察','可支持的解释'],[
 ['S1-01—03','Manipur：original/2×对，4×错；822/822 token','输出Pakhangpa而非参考Pakhangba/Pamheiba；预算合格不保证答案保留'],
 ['S1-04—06','Macbeth：三种方法均写Banquo，均得1','BM25在部分问题可保留关键实体，不应只挑失败槽'],
 ['S1-07—11','Heaven：拒答、否定提及和首行边界','S1-08/09否定句含Los Lonely Boys仍得1；10/11仅后续行命中'],
 ['S1-12—13','Astros：2013变为2017；4×得0','压缩后发生年份混淆；仅由输出不能断定内部因果']
],[3.15,6.1,7.2])
para('首行子串EM不等于语义正确：S1-08/09否定目标歌名却提及Los Lonely Boys而得1。既有审计共4槽同类现象；另2槽original拼接全文后由0变1。本文保留官方首行指标，不作事后替换。')
para('恢复负例中，Bantu Education Act回答截短后由1变0；Cracker Barrel两个位置输出替换为“645 stores in 44 states”等文本后得0。缺完整缓存与参考上下文，仅支持恢复可能损害既定EM，不声称已定位全部根因[8]。')
h('7　局限、代码与AI辅助披露')
para('结论受单一数据集、100题、五位置及问答模型替代限制。硬预算、恢复分词器与无效k映射偏离论文；API版本非不可变快照。未预注册等效界值，消融区间未作多重比较校正，小差异不作稳健优劣结论。')
para('CUDA型号、阶段四CANN及阶段二/三/四完整输出、压缩/问答缓存和校验和仍缺，不能独立重放全部推理；阶段一canonical预测已核验。历史tokenizers 0.21.0/0.21.4与本机离线0.22.1分开，阶段二16.67 GB与效率16.428 GB不合并。')
para('代码依赖锁定版本的LLMLingua与Lost in the Middle；本文档更新未改源码或原结果。AI辅助仅用于汇编、写作、图表与排版，不生成模型回答、压缩文本或案例。2026-11-21初版所载43项为历史回传，当时未在报告环境亲跑。同日17:46:58–17:47:02（北京时间），本机完整pytest为77/77、退出0，问答API调用0；配齐公开NQ与固定分词器后，原72过/5因缺资源失败已解决[12]。这是离线代码/记录核验，不是重新推理3500槽，原分数未改。')
para('受控Cursor回答仍缺、无新分数，不把对话当DeepSeek API。代推进不冒充成员亲历，未代勾自检。占位包已生成，P号及四人登记信息仍缺。60秒核心演示视频已完成，CPU重算/评分与历史GPU/NPU结果分开展示；真人讲述计时及本人确认仍缺，不承诺满分。')
h('8　结论')
para('本次方法级证据支持LongLLMLingua较传统压缩基线保留更多问答性能，问题感知排序贡献突出；但2×未证成等效，4×有预算超标，且本批次无端到端加速。结论受批次、计数口径和缺失原始输出限制。')
# REFERENCES
page();h('参考文献与公开来源（不计正文）')
para('正文为前5页。以下为参考文献及来源索引；公开网页核对日期：2026年11月21日（Asia/Shanghai）。文献作者以ACL Anthology正式条目核对，版权人不代替合著者名单。',9)
refs=[
('[1] Jiang, H., Wu, Q., Luo, X., Li, D., Lin, C.-Y., Yang, Y., & Qiu, L. 2024. LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression. ACL 2024 (Long Papers). 本报告对照arXiv:2310.06839v2。','https://aclanthology.org/2024.acl-long.91/'),
('[2] Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. 2024. Lost in the Middle: How Language Models Use Long Contexts. Transactions of the Association for Computational Linguistics, 12:157–173.','https://aclanthology.org/2024.tacl-1.9/'),
('[3] Kwiatkowski, T., et al. 2019. Natural Questions: A Benchmark for Question Answering Research. Transactions of the Association for Computational Linguistics, 7:453–466.','https://aclanthology.org/Q19-1026/'),
('[4] Jiang, H., Wu, Q., Lin, C.-Y., Yang, Y., & Qiu, L. 2023. LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models. EMNLP 2023.','https://aclanthology.org/2023.emnlp-main.825/'),
('[5] G14. 论文参数与固定实现对照（stage2-parameter-map.md）；记录k映射、预压缩、计数和恢复的差异。','https://github.com/SPikerinbit/longllmlingua-reproduction/blob/'+heads['stage2-compression']+'/docs/stage2-parameter-map.md'),
('[6] G14. 阶段一离线审计、canonical预测与13槽案例；stage1-foundation公开记录。','https://github.com/SPikerinbit/longllmlingua-reproduction/blob/'+heads['stage1-foundation']+'/reports/stage1-supplement/cases.md'),
('[7] G14. CUDA pilot主比较：run.json、summary.json与stats.json；stage3-main-comparison公开记录。','https://github.com/SPikerinbit/longllmlingua-reproduction/blob/'+heads['stage3-main-comparison']+'/reports/stage3-main/stats.json'),
('[8] G14. 独立NPU消融、效率与恢复负例；stage4-ablation-efficiency公开记录。','https://github.com/SPikerinbit/longllmlingua-reproduction/tree/'+heads['stage4-ablation-efficiency']+'/reports/stage4-ablation-efficiency'),
('[9] Microsoft. LLMLingua公开实现，锁定提交5a4c78ae18ab17a98cf997e8259354e546081d64。','https://github.com/microsoft/LLMLingua/tree/5a4c78ae18ab17a98cf997e8259354e546081d64'),
('[10] Lost in the Middle. 数据、问答模板及评分代码，锁定提交29b8a6d042ce29abccee3db1a73171a107d7e6af。','https://github.com/nelson-liu/lost-in-the-middle/tree/29b8a6d042ce29abccee3db1a73171a107d7e6af'),
('[11] BIT自然语言处理课程. 2026年课程要求，第七节。验收由课程方判定，本文不推定评分。','https://nlp.hltbit.top/2026/materials/w01/classroom/requirements.html'),
('[12] G14. 2026-11-21本机离线核验记录：命令、JUnit、资源SHA与四阶段审计随附sources/local-verification/。被测代码为main bdb11d3；链接指向代码提交，不冒充已推送的证据目录。','https://github.com/SPikerinbit/longllmlingua-reproduction/commit/bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4')]
for label,url in refs:link(label+' [点击来源]',url)
para('本地随附SOURCES.md给出来源清单、对应批次、锁定分支头与文件SHA-256；sources/保存实际用于报告的轻量表格与案例。原论文PDF位于用户指定本地目录；图1标注原文图号。本文新绘图2仅从真实分位置汇总重绘，未添加模拟点。',9)
# APPENDIX A
page();h('附录A　可追溯性与待补清单（不计正文）')
h('A.1　锁定资源与真实运行',2)
para('压缩权重：NousResearch/Llama-2-7b-chat-hf；revision 351844e75ed0bcbbe3f10671b3c808d2b83894ee。DeepSeek计数分词器：deepseek-ai/DeepSeek-V4.1-Flash；revision 314113f8a7dadb388215396ba5fbee2c610a04d6。问答API模型名并不证明该版本被不可变固定。',9)
para('阶段四已记录环境：Python 3.12.0，torch 2.7.1，torch-npu 2.7.1.post2，transformers 4.53.1，tokenizers 0.21.4，numpy 1.26.4，accelerate 1.0.1；设备Ascend910B4。CANN版本未登记，不能以npu-smi版本替代。',9)
para('本机离线核验环境为Python 3.13.5、tokenizers 0.22.1，与上述推理环境分开。prepare已配齐公开NQ五gz与上述固定revision的官方tokenizer.json；六文件SHA与清单一致，不载权重、不调用付费API。tokenizer SHA-256：\nc90dfa01249db1be4245780a052ede752e1361c612ac6d08e2bdada7d599476b。',9)
table(['阶段 / run_id','证据定位（仓库路径）'],[
 ['一 d54b3118c61ea4930624','reports/stage1-acceptance/predictions.jsonl；reports/stage1-supplement/offline-audit.json'],
 ['二 a1bd26fe3d82dea3f65d','reports/smoke-stage2-acceptance.json；预算396/400'],
 ['三 e8f151b9c286648caf98','reports/stage3-main/run.json、summary.json、stats.json'],
 ['四 a9d2295195adde90484d','reports/stage4-ablation-efficiency/ablation.csv与inputs/ablation-run.json'],
 ['效率 2a7f4accf6127178a76b','同目录efficiency.csv与inputs/efficiency-run.json']
],[6.5,9.95])
para('阶段三pilot快照为reports/stage3-main/run.json；默认configs/stage3.json是main，不能冒充pilot。此次本机四阶段审计的api_calls均为0；阶段四已重建至独立输出目录，未覆盖原结果，JSON一致、CSV仅CRLF/LF差异。证据见随附local-verification/与运行摘要[12]。',9)
para('阶段一canonical预测SHA-256：\ncac37c9e84678f2f591af8c4f6ccdb7a69d010cf71eae5678b85109bcb27bd62。该校验和与原审计、本机新审计一致；13槽首行、分数与token均已核对，主比较与消融分数未改。',9)
h('A.2　源稿差异处理记录',2)
table(['项目','本报告处理'],[
 ['stage2旧394/400','推荐分支口径396/400；旧兼容副本单独说明，不混用run'],
 ['PPT中的pilot配置入口','仓库不存在独立pilot-as-run配置文件；只引用真实run.json快照'],
 ['当前77/77','2026-11-21本机全套pytest全过；31/36/43/44是历史不同子集/回传，非同一全套口径。43为当日报告初版回传，当时未亲跑；详见[12]'],
 ['环境与显存差异','阶段二CANN 8.5.2不外推至阶段四；tokenizers与峰值GB并列差异不暗改'],
 ['公开资源与资料包','缺tokenizer/NQ导致的5项失败已解决；占位包与60秒核心实录已完成，登记及本人确认仍缺']
],[4.4,12.05])
h('A.3　实际剩余缺口',2)
para('仍缺CUDA型号、阶段四CANN、阶段二/三/四完整逐条输出及压缩/问答缓存与校验和、受控Cursor回答、P号与四人登记信息、本人确认及真人讲述计时。公开资源已齐，课程占位包已生成但登记未齐。60秒1920×1080核心视频配中文讲解及字幕；真实GUI终端素材经剪辑，样本独立补拍。展示入口配置、字段隔离、已完成CPU BM25的3289→1644→822及gold丢失、保存回答评分边界和历史CUDA/NPU表。无现场GPU/NPU/Long新推理，非六章连续实时演算。视频为evidence/core-evidence-60s.mp4；文稿、字幕、剪辑对照及SHA见SOURCES。内嵌PPT制作中，未验证Windows播放；未代勾本人确认。',9.5)
# APPENDIX B: full 13 source first-lines over four pages
qidmap={c['question_id']:None for c in cases}
for i,q in enumerate(qidmap):qidmap[q]=f'Q{i+1}'
for gi,group in enumerate([cases[:3],cases[3:6],cases[6:10],cases[10:]]):
 page();h(f'附录B　13条真实槽案例（{gi+1}/4，不计正文）')
 if gi==0:
  para('统一run：d54b3118c61ea4930624；问答：deepseek-flash。以下为来源首行原文（保留英文以便核验），分数不重写。时间统一转换为Asia/Shanghai。完整64位ID与slot_id随附cases-verified.json，以下使用12位ID前缀定位，前缀在本组13槽中无歧义。',9)
 for c in group:
  h(c['case_id']+'　'+c['method']+' / 位置'+str(c['position']),2)
  para('问题：'+c['question']+'\n参考：'+c['references']+'　｜　ID前缀：'+c['question_id'][:12],9)
  tm=datetime.fromisoformat(c['created_at']).astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
  para(f"score={c['score']:.0f}；原始/压缩/目标={c['origin_tokens']}/{c['compressed_tokens']}/{c['target_tokens']} token；{tm}（Asia/Shanghai）",8.5)
  p=para(c['first_line'],9);p.paragraph_format.line_spacing=1.08;p.paragraph_format.left_indent=Cm(.25)
  para('诊断：'+c['diagnosis']+'。',8.5)
 if gi==3:
  para('可复查来源：reports/stage1-supplement/cases.md与canonical predictions.jsonl。本报告13条槽不代表13道独立问题，且不能替代尚缺的阶段二/三完整逐条记录。',9)
# Save text and native editable file.
doc.core_properties.title='G14 LongLLMLingua 方法级复现报告';doc.core_properties.author='G14';doc.core_properties.subject='BIT NLP课程；既有真实实验与离线审计'
doc.save(R/'report.docx');(R/'report.md').write_text('\n'.join(md))
# Source provenance: historical immutable material and current local read-only evidence.
registry=['# G14报告来源清单（本机核验更新版）\n',
'更新日期：2026-11-21（Asia/Shanghai）。仅编辑`/workspace/reports/g14-core-final/`报告产物；未修改repo工作树、原始结果或测试，未上传。\n',
'## 当前代码与证据基线\n',
'- 本机被测main：`bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4`；环境、时间线、命令和JUnit均指向此代码。',
'- 用户17:56（Asia/Shanghai）回传当前四头：stage1-foundation `a485190`；stage2-compression `93f74bc`；stage3-main-comparison `32f7b6e`；stage4-ablation-efficiency `6fe6274`。这些是当前分支简写，不拿它们冒充初版文件的取样提交。',
'- `sources/report-repo-source-20261121.md`来自此次指定的最新版仓库报告；与初版报告Markdown字节相同，后按精确建议更新本文。',
'- `sources/KNOWLEDGEWORK-SUGGESTIONS-20261121.md`、`sources/RUN-SUMMARY-20261121.md`：此次修改要求及真实运行摘要。',
'\n## 本机真实离线核验（当前77项入口）\n',
'- `sources/local-verification/`：脱敏命令、stdout/stderr、JUnit、环境与依赖、资源SHA、四阶段审计、plan与阶段四独立重建。证据副本不包含权重、公开数据正文、tokenizer本体、虚拟环境或凭证。',
'- 2026-11-21 17:45:50–17:45:51（Asia/Shanghai）：完整收集77项，72通过、5因缺公开NQ或固定tokenizer失败，退出1；见baseline日志与JUnit。',
'- 17:46:00–17:46:07（同日Asia/Shanghai）：prepare成功，只配公开五gz及官方tokenizer.json；不下载LLaMA权重，不调用付费问答API。',
'- 17:46:58–17:47:02（同日Asia/Shanghai）：完整pytest 77/77、0失败/0跳过、退出0，JUnit耗时3.530秒。见`pytest-full.stdout`、`junit-full.xml`、`timeline.txt`。报告编辑本轮只读检查该证据，没有额外重跑pytest或模型。',
'- 当前离线环境Python 3.13.5 / tokenizers 0.22.1；不是历史CUDA/NPU推理环境。历史阶段四仍为Python 3.12.0 / tokenizers 0.21.4，历史0.21.0也不合并。',
'- 官方公开DeepSeek-V4.1-Flash tokenizer固定revision `314113f8a7dadb388215396ba5fbee2c610a04d6`；tokenizer.json SHA-256 `c90dfa01249db1be4245780a052ede752e1361c612ac6d08e2bdada7d599476b`，6,367,257字节。五NQ gz SHA与原清单一致。',
'- `sources/local-resource-readonly-check.json`：报告编辑对实际六个公开资源只读计算SHA，与脱敏证据逐项一致；未复制原始资源进包。',
'- 四阶段本机审计均api_calls=0；CUDA主比较、396/400、NPU消融与效率原数不变。阶段四重建写独立目录；JSON/RESULTS.md一致，CSV仅CRLF/LF换行差异。',
'- `plan/smoke-plan.rerun.json`与published版slots/token合计一致，仅config_hash不同（实现文件换行LF/CRLF）；DeepSeek LICENSE亦有1064/1084字节LF/CRLF等价差异，原清单未覆盖。',
'- 43项为2026-11-21初版报告制作时历史回传，当时未在该报告环境亲跑。31/36/43/44属历史子集或回传口径，当前不再作为完整验收入口，不据数量差异认定造假。',
'- 2026-11-21 21:46（Asia/Shanghai）同步最终60秒核心视频：`evidence/core-evidence-60s.mp4`，60.000秒、1920×1080、H.264视频及AAC音轨；SHA-256为`e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e`，与用户给定值和实际源文件一致。旧50秒测试视频不收入本包，也不把旧片videoReview结果套用到新片。',
'- 讲解音轨采用TTS制作，配中文字幕；最终画面顶栏为普通标题，历史GPU/NPU结果标签保留，不声称真人现场口播。随附`evidence/core-evidence-60s.srt`、`evidence/voice/NARRATION.md`、`evidence/EDIT-MAP.md`与`evidence/poster.png`；语音软件/音色、语速、剪辑和补拍时间轴均有披露。',
'- 真实GUI终端素材经剪辑并含已披露定格，样本章独立补拍且有镜头调序。展示入口配置、样本可见字段隔离、已完成CPU BM25结果3289→1644→822与gold丢失、对已保存回答评分及首行指标边界、历史CUDA/NPU表。不是六章连续完整实时演算，无现场GPU/NPU/Long新推理，视频不新增问答模型分数。',
'- 本轮报告编辑读取解说/字幕/剪辑对照，并核对ffprobe元数据、给定视频SHA和所有包内副本；不冒称重新执行整套实验或新片videoReview。PPT内嵌工作另行制作，本报告包不含任何PPT或旧外链版，不宣称Windows已播放。',
'- 录屏完成不等同真人讲述计时、成员本人参与/确认或新模型实验，这些缺口仍保留；视频不提供新的方法分数。',
'- 占位资料包已生成，尚缺P号、四人登记信息与本人确认等；不再写zip未打，也不宣称可直接最终提交。',
'\n## 初版历史资料锁定头（2026-11-21 16:25–16:34，Asia/Shanghai）\n']
for b,sha in heads.items():registry.append(f'- [{b}历史快照](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/{sha})：`{sha}`。正文原方法数字继续引用该锁定资料，不伪称这仍是当前分支头。')
registry += ['\n## 原方法资料用途\n',
'- `canonical-stage1/`与`cases-verified.json`：300槽canonical预测、原审计及13真实槽（4题）；此次更新未改首行、分数、token或原始时间。',
'- `stage1-cases.md`、`stage2-acceptance-remote.json`、`stage3-stats-remote.json`与`stage4-ablation-remote.csv`：初版通过GitHub只读取得的来源快照，不冒称此次重新抓取。',
'- `g1/summary.json`、`g1/run.json`：CUDA主比较；`g1/parameter-map.md`：有效/无效参数差异；396/400以canonical验收为准。',
'- `g2/ablation.csv`、`efficiency.csv`及run/coverage/environment/恢复案例：独立NPU批次；完整输出/压缩缓存及其SHA仍未取得，不用新资源哈希冒充。',
'- `g2/analyze_stage4.py`为原文档制作时源码快照；无恢复行从已有score_before_recovery派生。本机此次真实重建证据另存local-verification/stage4-rebuild/，未覆盖原表。',
'- 原源稿、五项证据、验收矩阵与`report-source-updated.md`为历史材料，只作变化对照，其中旧的未完成状态不当作当前结论。',
'- 图1：随附原论文PDF的图2原图截取，`figures/paper-figure2.png`；图2：真实CUDA summary.groups重绘，`figures/stage3-position.png`。原始分数不变，无模拟点。',
'- 真实pilot配置快照是`reports/stage3-main/run.json`；默认stage3配置是main。不存在的独立pilot-as-run配置不作入口。',
'\n## 参考文献与可点击来源（作者在初版已从ACL官方页核对）\n']
for label,url in refs:registry.append(f'- [{label}]({url})')
registry+=['\n## 随附来源副本SHA-256\n','这些是资料副本校验和，不冒充缺失的阶段二/三/四完整输出缓存校验和。\n']
for p in sorted(S.rglob('*')):
 if p.is_file():registry.append(f'- `{p.relative_to(R)}`  `{hashlib.sha256(p.read_bytes()).hexdigest()}`')
registry+=['\n## 核心视频及配套素材SHA-256（课程包相对路径）\n']
for p in sorted((R/'evidence').rglob('*')):
 if p.is_file():registry.append(f'- `{p.relative_to(R)}`  `{hashlib.sha256(p.read_bytes()).hexdigest()}`  {p.stat().st_size} bytes')
registry.append('- 录屏元数据、复核来源和范围：`qa/recording-verification.json`。未声称真人口播计时/成员确认已完成。')
(R/'SOURCES.md').write_text('\n'.join(registry)+'\n')
(R/'qa/source-checks.json').write_text(json.dumps({'new_model_calls':0,'current_local_tests':{'collected':77,'passed':77,'failed':0,'skipped':0,'exit':0,'start':'2026-11-21 17:46:58+08:00','end':'2026-11-21 17:47:02+08:00','code_commit':'bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4','python':'3.13.5','tokenizers':'0.22.1','evidence':'sources/local-verification/','test_execution_by_report_editor':False},'previous_baseline':{'passed':72,'failed_missing_resources':5,'resolved':True},'historical_43':'2026-11-21 initial-report relay; not executed in that report environment','case_count':13,'distinct_case_questions':len(qidmap),'case_first_lines_scores_tokens_match_canonical':True,'stage3_stats_equal_local_snapshot':True,'stage4_remote_csv_equal_local_snapshot':True,'stage2_canonical_budget':'396/400','stage3_slots':3500,'body_target_pages':5,'video':{'status':'edited core evidence with synthetic Chinese narration/subtitles','seconds':60,'width':1920,'height':1080,'narration':'TTS production; Chinese narration and subtitles','edited_real_GUI_footage':True,'independent_sample_pickup':True,'new_GPU_NPU_Long_inference':False,'six_chapter_continuous_recalculation':False,'embedded_PPT':'in production separately; not included or playback-verified','metadata_and_copy_sha_checked':True,'personal_confirmation_and_oral_timing':'still missing'}},ensure_ascii=False,indent=2)+'\n')
print('Updated local-verification DOCX, Markdown and source registry written')
