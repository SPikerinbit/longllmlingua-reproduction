# 成员一自检

检查时间：2026-11-21。对照 `task.md`。勾选表示文件已经在本分支，不表示成员二已经复核。

## 口播和幻灯片

- [x] P1、P2、P7 在 `slides-P1-P2-P7.pptx`，并已放进九页模板。
- [x] LibreOffice 导出的 `previews/slide-1.png` 到 `slide-3.png` 中文可读，页脚没有挡住正文。
- [x] P2 的 92.0 / 87.0 / 64.0 来自 `acceptance.json`，84.6 来自阶段三 `summary.json`。
- [x] 讲稿分秒写在 `script.md`。P1+P2 按 4.2 字/秒约 57 秒。
- [ ] 没有用手机实讲。留到 11-22 20:00。

## 证据清单

- [x] 打开过 `acceptance.json`、`predictions.jsonl`、`summary.md`、`manifests/smoke.json`。
- [x] 用 300 行预测重算 EM：original 0.92，bm25_2x 0.87，bm25_4x 0.64。
- [x] 用锁定 sha256 的 gold_at_0 对齐了 20 个 smoke 问题，三条案例的问题和参考答案来自这次对齐。gz 没有提交。
- [ ] `outputs/stage1/d54b3118c61ea4930624` 不在本工作区，sha256 仍缺。
- [ ] `python -m reproduction plan` 没有跑，因为没有原始数据。
- [ ] `accept_stage1.py` 不能在本仓库单独跑通，缺 prompt 和 cache。验收报告里的 `offline_rescore_identical: true` 是当时的记录，不是这次重跑。

## 材料清单

- [x] 报告第 1、2、3、8 节初稿。
- [x] `data/README.md` 与成员一的 `contributions.md` 段。
- [x] QA 10 题，案例 3 条。
- [ ] 成员二、三、四还没有把他们的两句交回第 8 节。
- [ ] `report.pdf`、终稿 `slides.pdf`、zip 都还没有。这三项在分工表里属于 11-22 16:00 之后的汇编。
- [ ] 录屏未做。任务书把成员一的录屏标成可选。

## 未完成

1. 组内运行目录的 sha256 和可下载路径要由成员一在有那份目录的机器上补进 `results/stage1/SOURCE.txt`。
2. 第 8 节的另外三段不能代写。
3. 实讲计时还没做。P1 稳速会到约 27 秒，稿里已经写了删哪半句。
