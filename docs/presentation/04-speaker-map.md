# 发言对照

总时长 8 分钟：PPT 5 分钟，运行证据 1 分钟，老师提问 1 分 30 秒，换人 30 秒。四人在 PPT 和证据里各讲 90 秒。提问的 90 秒由老师点名，不摊进每人 90 秒。页码是功能占位，等幻灯片定稿后再填实际页码。现在不能把某一版页数当成已经批准。

| 顺序 | 成员 | 占位 | 秒 | 要打开的文件 | 准备的问题 |
| --- | --- | --- | ---: | --- | --- |
| 1 | 一 | P1 题目和范围 | 25 | `manifests/resources.json`，`docs/experiments.md` | 为什么只做五个位置 |
| 1 | 一 | P2 问题与基线 | 35 | `reports/stage1-acceptance/acceptance.json`，`reports/stage1-supplement/offline-audit.json` | 首行评分会不会把否认句记成对 |
| 2 | 二 | P3 方法 | 45 | `docs/stage2-parameter-map.md` | k=2 为什么不能做消融 |
| 2 | 二 | P4 设置差异 | 45 | `reports/stage2-smoke/verification.json` | 4 条超预算为什么留着 |
| 3 | 三 | P5 主比较 | 60 | `reports/stage3-main/summary.json`，`stats.json` | 2x 的区间为什么跨过 0 |
| 3 | 三 | 证据前半 | 30 | `python -m reproduction.stage3` 的帮助，`coverage.json` 的 3500 | 为什么 `configs/stage3.json` 的 split 不是这次结果 |
| 4 | 四 | P6 消融与案例 | 60 | `reports/stage4-ablation-efficiency/ablation.csv`，`inputs/recovery-cases.json` | 为什么 82.6 和 83.2 不是同一次实验 |
| 4 | 四 | 证据后半 | 30 | `python scripts/audit_stage4_offline.py`，`environment-current.json` | tokenizers 0.21.4 和 0.21.0 哪一份是现场环境 |
| 5 | 一 | P7 结论 | 30 | `docs/presentation/01-number-registry.md` | 哪些结论还不能说 |

每人另备至少 5 个问题，答案只引用上表文件。成员一的 10 题在 `docs/presentation/members/member1/qa.md`。成员二、三、四的题目在各自 `task.md`，那些“已复核”勾选仍然空着，要本人读过文件再勾。

现场不要训练，不要把 Cursor 会话时间说成 API 延迟。证据备份是打开已经提交的 json。录屏还没有，不能写成已经备好。
