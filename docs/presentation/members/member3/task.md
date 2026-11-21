# 成员三：任务、证据和验收

继续在 `stage3-main-comparison` 上推进。`stage_3` 保留不删，不再往该分支加新提交。当前演示稿里，成员三讲物理页 5（P5，60 秒）和页 8（B1，30 秒）。讲稿在 `docs/presentation/final/member3-script.md`。登记表上的姓名待本人填写；课程原文没有单独要求“法定姓名”。主比较是 CUDA 上的 pilot 100 题，不是 `configs/stage3.json` 里那个 split=main 的 500 题配置。页 8 的命令是 `python -m json.tool reports/stage3-main/run.json`，只读查看已保存快照。仓库里仍然没有 `configs/stage3-pilot-as-run.json`。

本推荐分支上的 `reports/smoke-stage2-acceptance.json` 与 `main` 相同：硬预算 396/400，`accepted_run` 为 `outputs/stage2/a1bd26fe3d82dea3f65d`。只有兼容分支 `stage_3` 仍保留历史副本 394/400 和 `outputs/stage2/875ddf42e70e37db8455`。对外讲阶段二超标时，推荐分支用 396/400，不要把 `stage_3` 的旧副本说成当前结果。主比较数字仍以 `reports/stage3-main/` 为准。

## 课程五项里由成员三讲解的证据

对照 `docs/presentation/02-score-evidence.md`。被点名时按这个顺序打开文件。未勾选项不能说成已经复核。

| 项 | 打开什么 | 8 分目标下还缺的 |
| --- | --- | --- |
| 理解与范围 | `docs/experiments.md` 的 100 题范围；`run.json` 的 split=pilot | P 编号 |
| 数据与实现 | `run.json` 的 run_id、config_hash、`cuda:0`；`manifests/pilot.json` | 本机 GPU 型号和包版本。没有写出之前不能勾 |
| 对照与消融 | `summary.json` 七行；`stats.json` 的 2000 次、seed 42、100 题 | `configs/stage3-pilot-as-run.json` 尚未从 run.json 抽出 |
| 错误分析 | 还没有 M3-01 至 M3-03 | 从组内 `results.jsonl` 摘 3 条后再勾 |
| 交付与答问 | `coverage.json` 的 3500/3500。2026-11-21 较早回传的 31 项是完整测试集子集；当前验收入口为同日稍后本机完整 pytest 77 项通过，见 `reports/local-verification/`。这只说明代码和轻量结果，不是重新跑了 API | 正式报告 PDF 与 50 秒组内离线实录已有；真人讲述计时与本人确认未做 |

真实运行入口是 `python -m reproduction.stage3 run --config <与 run.json 一致的配置>`。离线检查是 `python -m pytest tests/test_stage3.py tests/test_final_delivery.py`。后者不需要密钥。密钥不要写入配置或日志。

## 验收标准

- [ ] P5 七行与 README 主比较表一致：84.6、72.4、55.8、46.8、35.6、83.2、79.0，压缩比 1.00x、2.00x、4.01x、2.04x、4.17x、2.08x、4.09x。
- [ ] 口播说出 2x 相对原始提示 −1.4 个百分点，区间 [−6.2, 3.0]，跨过 0。来源 `stats.json` 的 mean −0.014、ci_low −0.062、ci_high 0.030。
- [ ] 说出 4x 区间不跨 0，以及预算满足率 0.964 即 18/500，成功槽仍是 500/500。
- [ ] 表字号 ≥18 磅，标题 ≥28 磅。样本范围写在页上：100 题 × 五位置，run `e8f151b9c286648caf98`。
- [ ] 30 秒证据按顺序打开：入口命令、`run.json` 的 run_id 和 split=pilot、`coverage.json` 的 3500、`summary.json` 里 longllmlingua_2x 的 `mean_em` 0.832。
- [ ] 现场不跑矩阵，不训练。
- [ ] 口头说明 `configs/stage3.json` 的 split 是 main，不能把它当成这次结果的配置文件。
- [ ] 不说 GPU 型号。记录只有 `cuda:0`。
- [ ] 报告第 6 节约 0.9 页，含一张位置图或说明图在 `positions.png`，图题写单位是 EM（%）和每格 100 题。
- [ ] 案例 M3-01 到 M3-03 来自组内逐条文件，并给出 sha256。仓库里的 `summary.json` 没有单题输出。
- [ ] QA 至少 5 题。`contributions.md` 成员三段已替换。

## (a) 实验证据清单

| 项 | 命令或入口 | 配置 | 记录 | 对应数字 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 入口 | `python -m reproduction.stage3 plan` 与 `run` | 实际快照在 `reports/stage3-main/run.json`，不是单独再猜一个 json | run_id `e8f151b9c286648caf98`，split=pilot，config_hash `eb38ed81b0640f81954c37f1e288dae15b4f45ca15fc294b20d507c2b5e3266e` | 3500 槽 | 快照已有。`configs/stage3.json` 的 split 是 main，需整理时从 run.json 抽出一份 `configs/stage3-pilot-as-run.json` 放进 zip，并注明它是快照副本 |
| 覆盖 | 打开即可 | — | `coverage.json`：expected 3500，success 3500，failed 0，missing 0 | 证据页第 3 步 | 已有 |
| 主表 | 打开即可 | — | `summary.json` 的 `methods` | P5 七行 | 已有 |
| 位置曲线 | `python scripts/plot_results.py` 会重写 png | — | 已提交的 `positions.png`、`positions.pdf` | 报告图。LongLLMLingua 2x 五位置 EM 83、83、82、84、84 | 图已有。不要为了现场重画而覆盖仓库 |
| 配对区间 | 阶段三统计子命令见 `reproduction/stage3.py` 的 stats | bootstrap 2000，seed 42，按问题绑住五位置 | `stats.json` | −1.4 pp 与 [−6.2, 3.0] | 已有 |
| 独立核验 | `python scripts/verify_member3_handoff.py` | 需要组内原始包 | `verification.json`：`passed: true`，baseline 提示重建 1500，恢复重放 1000，summary、coverage、配对统计均 reproduced | 证明汇总不是手填 | 核验结论已有。脚本要原始回答才能再跑 |
| 逐条全文 | 组内 stage3 的 `results.jsonl` | run 目录按 `docs/experiments.md` 的最终包布局类推，阶段三原文路径要成员三自己写死 | 每条应有问题 ID、位置、方法、参考答案、输出、配置 | 案例和“逐样本输出” | 缺失。仓库没有这 3500 行 |
| 种子 | run.json 与清单 | seed 42，问题 ID 与 `manifests/pilot.json` 的前若干个一致（run.json 开头的 ID 与 smoke/pilot 相同） | — | 划分 | 已有于 run.json 的 `question_ids`。打包时不要只写“seed 42”而不附清单 |
| 调用 | API cache 在组内 | 不含密钥 | summary 里的 api_input_tokens。original 为 1,472,015 / 输出 38,435 | 只报 token | 汇总已有。原始请求不在 git |
| 环境 | run.json 的 compressor.device | `cuda:0`，模型名 `NousResearch/Llama-2-7b-chat-hf` | 无 GPU 型号 | P4 已替成员二写了“无型号”，成员三在证据页重复这句 | 已有，而且就是“没有型号” |

30 秒现场顺序已经写在模板第 8 页左侧。备份录屏按同样四步，文件 TODO：`results/demo/member3-evidence.mp4`。录屏里不要出现密钥或 `.env`。

独立核验：在不重新请求 API 的前提下，打开 `verification.json` 的 `summary_reproduced`、`coverage_reproduced`、`paired_statistics_reproduced`，都应为 true。若要自己再跑 `verify_member3_handoff.py`，先拿到原始包，把命令和耗时写进贡献段。没有跑过就不要写“我重新核验通过”。

## (b) 需制作材料明细

| 交付物 | zip 位置 | 格式和篇幅 | 截止（北京时间） | 核验人 | 验收 |
| --- | --- | --- | --- | --- | --- |
| P5 | `slides.pptx` 第 5 页 | 60 秒；表 ≥18 磅 | 11-22 12:00 | 成员四对照 `summary.json` | 七个 EM 与 README 一致 |
| 证据前 30 秒 | 同一 pptx 的运行证据页左栏，加可选 mp4 | 30 秒 | 11-22 18:00 前录好或确认能现场打开 | 成员四 | 30 秒内能指到 0.832 |
| 报告第 6 节 | `report.pdf` | 约 0.9 页，含图题 | 11-22 12:00 | 成员四 | 区间和 18/500 都在 |
| 配置副本 | `configs/stage3-pilot-as-run.json` | 从 run.json 抽出的配置对象，文件头注释 run_id | 11-22 12:00 | 成员二看 reorder 仍是 original | hash 与 run.json 的 config_hash 说明一致；若抽不出字节级原文件，就在注释里写“摘自 run.json，不是独立配置文件” |
| 案例 3 条 | `results/cases/M3-01.md` 起 | 含样本 ID、标签、输出、对错、配置 | 11-22 12:00 | 成员一看有没有把 gold 写进“模型输入” | 每条能在组内 jsonl 找到同一 slot_id |
| 逐条输出 | `results/stage3/SOURCE.txt` 加可选抽样 | 全文若太大，写路径、字节数、sha256，并至少附 10 行以外的索引 | 11-22 12:00 | 成员四 | 课程要逐样本。只有汇总表算缺失 |
| 贡献段 | `contributions.md` | 替换占位 | 11-22 12:00 | 成员四 | 写明 cuda:0 无型号 |
| QA | 不进 zip | 至少 5 题 | 11-22 12:00 | 本人 | 见下 |

## QA

Q1 为什么不是 500 题？15 秒：课程范围固定为 pilot 100。`configs/stage3.json` 虽是 split=main，这次 run.json 的 split 是 pilot，3500 槽等于 100×5×7。不能说：500 题跑了一半。

Q2 2x 有没有显著低于原始提示？15 秒：点估计低 1.4 个百分点，95% 区间 [−6.2, 3.0] 跨过 0。不能说：显著下降。4x 的区间不跨 0，可以分开说。

Q3 18 条超预算算不算失败？15 秒：不算缺失。success 仍是 500，`budget_satisfied_rate` 是 0.964。比较时不能把它说成严格等预算。依据 `summary.json`。

Q4 位置效应还在吗？15 秒：原始提示五位置 EM 是 84、84、84、85、86，每格 100 题。LongLLMLingua 2x 是 83、83、82、84、84。差不大。图是 `positions.png`。不能说：复现了论文里的 U 形曲线，除非自己先把这五个数念出来。

Q5 统计怎么配的？15 秒：按问题 ID 配对，五位置绑在一起重采样，2000 次，seed 42，95% 区间，分母 100 题，coverage 1.0。依据 `stats.json` 文件头。

Q6 能不能和 910B 的 82.6 比速度？15 秒：不能。主比较只记到 cuda:0，没有耗时表。效率是另一台 910B 上另一批 99 个样本。成员四讲延迟。
