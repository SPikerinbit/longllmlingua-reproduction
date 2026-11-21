# G14正式复现报告：本机离线核验更新版

## 正式文件
- `report.pdf`：A4共11页；正文1–5页，参考文献第6页，附录7–11页，保留13真实槽（4题）。
- `report.docx`：原生可编辑文字/表格，不是PPT、Pages或整页图片。
- `report.md`：同步文字源；`build_report.py`：自包含文档/图表生成脚本，不调用模型、不改仓库。
- `SOURCES.md`：带日期的历史锁定来源、当前main与四分支简写、现有证据、来源用途和副本SHA。
- `sources/local-verification/`：本机真实脱敏证据49文件及原SHA清单；不含权重、原数据正文或凭证。
- `qa/final-audit.json`：分页、边界、字体、12个可点击来源、77项JUnit、49文件校验及原结果不变核验。
- `pages/final-*.jpg`：最终11页逐页视觉检查图。
- `report-package.zip`：更新报告与来源的本地便携包，不等于已完成课程最终提交包。

## 本次实质更新
2026-11-21（北京时间/Asia/Shanghai）17:46:58–17:47:02，本机基于main `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4` 完整pytest收集77项、77项通过、0失败/0跳过、退出0，JUnit记录3.530秒。原先同一收集数下72过、5因缺NQ/分词器失败已在prepare配齐后解决。四阶段离线审计问答API调用均为0，非新推理，原方法EM/CI/预算/消融/效率未改。

本机离线环境Python 3.13.5 / tokenizers 0.22.1，与历史CUDA/NPU推理环境分开。官方公开DeepSeek-V4.1-Flash tokenizer固定revision `314113f8a7dadb388215396ba5fbee2c610a04d6`；tokenizer.json SHA-256 `c90dfa01249db1be4245780a052ede752e1361c612ac6d08e2bdada7d599476b`。报告编辑对真实六个公开资源只读计算SHA并与证据核对一致；未加载权重、未调用付费API、未额外重跑pytest。

43项保留为同日初版报告制作时历史回传（当时未在该报告环境亲跑）；31/36/43/44不冒充当前完整77项入口。

## 仍未完成
CUDA具体型号、阶段四CANN、阶段二/三/四完整逐条输出及压缩/问答缓存和校验和、受控Cursor回答、P号与四人登记信息、本人确认/自检、实际计时等仍缺。公开NQ与tokenizer已不是当前缺口。

课程占位资料包已生成，但登记信息仍待补，不能直接当最终提交包。50秒、1920×1200连续终端离线验收实录已完成并通过videoReview；随附`evidence/local-offline-evidence.mp4`与结果截图`evidence/local-offline-evidence-result.webp`。SHA、5项定向测试通过、77项进度100%、脚本退出0和无secret的复核范围见`qa/recording-verification.json`。不是新推理，也不等同真人讲述计时、成员本人参与或确认；不声称课程全部验收通过。

本次只编辑`/workspace/reports/g14-local-final/`，未修改repo工作树、原结果或旧报告，未上传。本次已同步录屏完成状态；真人讲述计时与成员本人确认仍未代勾。

## 只重建本文档
依赖：Python 3 + python-docx + Pillow；LibreOffice Writer；Noto CJK/DejaVu字体；Poppler。

```bash
python3 build_report.py
libreoffice -env:UserInstallation=file:///tmp/g14-local-report-rebuild --headless --convert-to pdf --outdir . report.docx
python3 qa/check_report.py
```

这不是模型/测试重跑命令。字体或Office版本变化可能改变分页，需重新视觉核验。阶段三实际pilot配置入口仍为仓库`reports/stage3-main/run.json`，不以默认main配置冒充。
