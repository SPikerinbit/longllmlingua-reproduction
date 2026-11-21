# 阶段三记录核对

没有新的问答调用。`scripts/audit_stage3_offline.py` 核对 `summary.json`、`coverage.json` 和 `stats.json`。

3500 槽全部成功。各方法 `mean_em` 与配对统计里的 `method_mean` 一致，对照基线都是 original 的 0.846。bootstrap 是 2000 次、seed 42、95%。LongLLMLingua 4x 的预算满足率是 0.964。

Cursor 配对比较没有做。设备记录仍然只有 `cuda:0`。
