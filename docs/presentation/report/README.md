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

课程占位资料包已生成，但登记信息仍待补，不能直接当最终提交包。当前媒体替换为60秒1920×1080核心实录`evidence/core-evidence-60s.mp4`（视频SHA见SOURCES），配中文讲解和中文字幕；音轨采用TTS制作，最终顶栏使用普通标题。随附海报、SRT、解说文稿与EDIT-MAP。

真实GUI终端素材经剪辑，样本独立补拍；展示入口配置、样本字段隔离、已完成CPU BM25 3289→1644→822及gold丢失、保存回答评分边界、历史CUDA/NPU表。无现场GPU/NPU/Long新推理，非六章连续完整实时演算。真人讲述计时与成员本人确认仍缺。PPT内嵌正在另行制作，本包不收PPT或旧外链版，不宣称Windows已播放。旧50秒测试视频不收入新包。

本次只编辑`/workspace/reports/g14-core-final/`，未修改repo工作树、原结果或旧报告，未上传。本次仅同步新60秒核心实录的真实范围；真人讲述计时与成员本人确认仍未代勾。

## 只重建本文档
依赖：Python 3 + python-docx + Pillow；LibreOffice Writer；Noto CJK/DejaVu字体；Poppler。

```bash
python3 build_report.py
libreoffice -env:UserInstallation=file:///tmp/g14-local-report-rebuild --headless --convert-to pdf --outdir . report.docx
python3 qa/check_report.py
```

这不是模型/测试重跑命令。字体或Office版本变化可能改变分页，需重新视觉核验。阶段三实际pilot配置入口仍为仓库`reports/stage3-main/run.json`，不以默认main配置冒充。

最终媒体同步：2026-11-21 21:46（Asia/Shanghai），包内五项素材均来自`/workspace/g14-core-demo/final/`；GPU/NPU历史结果、CPU重算/保存回答评分及独立补拍/剪辑事实不变。

## 仓库同步说明（2026-11-21 21:52，Asia/Shanghai）

以上是报告包原文。本目录正式文件已与核验副本对齐，哈希不变：

- `report.pdf` `c22fdba0788021c922433eec6bdad154f52e564c7ee0dabd0a2d2fd36bde4c3e`
- `report.docx` `d6ba258e81b9ad032b5ec4b662ddd8b48834a6c1bf2b83eccaa49765279ac8e3`
- `report.md` `fca54af48b1394b860be7f9b4f102c4a11bbbe49e3daaffbf146a36891b84bd4`
- `SOURCES.md` `59a8a858ce4f92d64bdf782b9b3c47b0d64968638aaf34f431f5f1d4a3acef36`

`evidence/` 仍是指向仓库根 `evidence/` 的符号链接。SOURCES 引用的 `core-evidence-60s.mp4`、`core-evidence-60s.srt`、`poster.png`、`EDIT-MAP.md`、`voice/NARRATION.md` 已按原哈希放入该目录。`sources/local-verification/` 仍指向 `reports/local-verification/`；报告包内 50 个文件与该目录对应文件哈希一致，目录中另外多出的 `VIDEO.md`、`POST-INTEGRATION.md` 是仓库侧说明，不是另一份运行。未纳入报告包 zip，以免与课程最终包混淆。

当前 `docs/presentation/final/slides.pptx` 已替换为 v7，P9 内嵌上述 60 秒成片。本说明只记录报告文件同步关系，不把课程包或本人确认标成已经完成。
