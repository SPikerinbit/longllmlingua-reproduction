# 阶段一离线审计说明

动机：在不新增 API 调用的前提下，检查固定题单、五位置是否对齐、BM25 预算是否守住，以及首行评分的边界。主指标仍是 `best_subspan_em`。

控制：只读 `reports/stage1-acceptance/predictions.jsonl` 和五个公开 gz。不改原验收文件。不读 `.env`。

命令：

```bash
python scripts/audit_stage1_offline.py --raw-dir /path/to/raw
```

本次 raw 目录是临时下载。五个 gz 与 tokenizer 的 sha256 都与 `manifests/resources.json` 相同。审计耗时 2.055 秒，Python 3.12.3，平台 Linux 6.12，API 调用 0。

结果：隔离失败 0，预算违规 0，重评分不一致 0。官方均值 0.92、0.87、0.64。诊断有 2 条首行漏分和 4 条否认句仍得 1 分，见 `offline-audit.json`。它们不改变已经公布的 EM。

局限：没有组内完整提示，不能重跑 `accept_stage1.py`。诊断正则只覆盖强否认句，不是人工复核全部 300 槽。

对幻灯片：P2 仍可使用 92.0 / 87.0 / 64.0，并说明这是 20 题。不要把诊断条数画成新的主结果。Cursor 对话还没有数字，不要加进表。
