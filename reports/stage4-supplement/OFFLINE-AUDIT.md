# 阶段四记录核对

没有重新压缩，也没有改 `ablation.csv` 或 `efficiency.csv`。`scripts/audit_stage4_offline.py` 核对覆盖率、csv 和 `ablation-statistics.json`。

消融 3500，效率 1200，效率表每行 n=99。统计里的方法均值与 csv 的 EM 一致，参照是 0.826。`recovery-cases.json` 仍是 3 条由对变错。

新的机制实验要有 910B 和权重。现在没有，所以不能加新的消融数字。
