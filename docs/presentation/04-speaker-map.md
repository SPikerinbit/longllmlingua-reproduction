# 发言对照

当前提交用的演示稿在 `docs/presentation/final/slides.pptx`（v6）。物理顺序是 P1、P2、P3、P4、P5、P6、P7、B1、B2。演讲顺序是 1、2、3、4、5、8、6、9、7。这 9 页就是现在的 slides。P8（B1）是历史 CUDA 记录，P9（B2）是历史 NPU 记录加本机 50 秒实录。`docs/presentation/slides/G14-LongLLMLingua-template.pptx` 是早期骨架。P1、P2、P7 保留结论横幅。

四人各 90 秒。PPT 主讲合计 300 秒，B1 与 B2 合计 60 秒。提问 90 秒和换人 30 秒另计。这是安排，不是已经用秒表量过的时间。

| 演讲次序 | 物理页 | 成员 | 秒 | 现场打开 |
| --- | --- | --- | ---: | --- |
| 1 | 1 P1 | 一 | 25 | `manifests/resources.json` |
| 2 | 2 P2 | 一 | 35 | `reports/stage1-acceptance/acceptance.json`；`reports/stage1-supplement/offline-audit.json` |
| 3 | 3 P3 | 二 | 45 | `reproduction/compression.py` 第 176–187 行；`docs/stage2-parameter-map.md` |
| 4 | 4 P4 | 二 | 45 | `reports/smoke-stage2-acceptance.json`；`reports/stage2-smoke/verification.json` |
| 5 | 5 P5 | 三 | 60 | `reports/stage3-main/summary.json`；`reports/stage3-main/stats.json` |
| 6 | 8 B1 | 三 | 30 | `python -m json.tool reports/stage3-main/run.json`。只读查看已保存 pilot 快照，不是现场推理 |
| 7 | 6 P6 | 四 | 60 | `reports/stage4-ablation-efficiency/ablation.csv`；`figures/ablation.png` |
| 8 | 9 B2 | 四 | 30 | `environment/environment-current.json`；`inputs/efficiency-run.json` |
| 9 | 7 P7 | 一 | 30 | `reports/stage1-supplement/cases.md` 的 S1 否定句案例 |

提问另计 90 秒。每人至少准备 5 题，题目在 `docs/presentation/final/QA.md` 和各自 `task.md`。本人没有把这些题当众答过，自检不能因此勾选。

旧骨架 `docs/presentation/slides/G14-LongLLMLingua-template.pptx` 不是这版讲稿。
