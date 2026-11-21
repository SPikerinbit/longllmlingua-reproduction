# G14 LongLLMLingua 正式课程复现报告

## 交付
- `report.pdf`：正式中文报告，A4，共11页；正文1–5页，参考文献第6页，附录7–11页。
- `report.docx`：主要可编辑源文件，原生文字与表格，不是整页图片，也不是PPT或Pages文件。
- `report.md`：同步可编辑文字源，含图表/参考来源。
- `build_report.py`：用随附来源生成DOCX/Markdown及真实分位置图的文档脚本，不调用模型、不修改仓库。
- `SOURCES.md`：来源用途、公开链接、观测分支头、实际使用文件的SHA-256。
- `sources/`：轻量来源快照、13条真实案例及原论文；`figures/`：原图与基于真实数据重绘图。
- `qa/`：逐页分页、文本边界、字体嵌入、点击链接与源数据检查；`pages/final-*.jpg`：逐页视觉核验图。
- `report-package.zip`：仅报告与证据源的本地便携包，不冒称课程完整终包。

## 已核验
11页已逐页渲染查看；正文恰好5页。无空白页、裁切表格或案例跨页孤块；PDF字体全部嵌入，11个不同来源链接保留可点击。13槽（4道题）首行、分数与token均与canonical预测一致。阶段二canonical为396/400；CUDA统计与远端stats一致；NPU消融本地/远端CSV一致。

## 范围与剩余缺口
这是基于既有真实DeepSeek实验、既有离线审计与本次来源对照制作的报告，未新推理、未重跑3500槽。受控Cursor试跑未执行，无新分数。43项离线测试通过是仓库侧回传，不冒称报告制作环境亲跑。

仍缺：CUDA具体型号、阶段四CANN版本/完整环境锁；阶段二/三/四完整输出、问答/压缩缓存及校验和和相应Long方法逐样本案例；P编号与姓名；成员本人贡献确认、自检、现场计时和录屏。报告制作未替本人勾选，未上传，未checkout仓库，未修改源代码或原结果。

后续仓库源更新应与`SOURCES.md`保存的快照对照；本报告不会自动继承后续变化。

## 本地重建（只生成本文档）
环境：Python 3 + python-docx + Pillow；LibreOffice Writer；Noto Serif CJK SC / Noto Sans CJK SC、DejaVu Sans字体；Poppler用于核验。

```bash
python3 build_report.py
libreoffice -env:UserInstallation=file:///tmp/g14-report-rebuild --headless --convert-to pdf --outdir . report.docx
python3 qa/check_report.py
```

Word/LibreOffice版本或字体变化可能影响分页，应以交付PDF为准并重新核验。不要以默认`configs/stage3.json`的main设置冒充pilot；实际运行配置快照在仓库`reports/stage3-main/run.json`。
