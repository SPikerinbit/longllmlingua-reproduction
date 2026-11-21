# 成员一：任务、证据和验收

成员一负责阶段一，并口播 P1、P2 和 P7。用户本人即成员一。法定姓名以登记表为准，仓库没有写。

已交在本分支的成品：

- `slides-P1-P2-P7.pptx` 与 `previews/`
- `script.md`
- `report-draft.md`
- `cases.md`
- `qa.md`
- 仓库根目录 `data/README.md` 与 `contributions.md` 里的成员一段
- `self-check.md`

## 验收标准

每一条都要能指出文件，不能只答“已完成”。

### 幻灯片

- [x] P1 含论文编号 2310.06839v2、提交 `5a4c78ae`、数据提交 `29b8a6d`、seed 42、100 题、deepseek-flash、temperature 0、max_tokens 512。来源写在页底。
- [x] P1 标题 36 磅，卡片正文 20 磅。P 编号写成 Pxx，没有编造。
- [x] P2 表为 92.0%、87.0%、64.0% 和 1.000x、2.001x、4.007x，样本各 100 槽。来源 `REPORT.md` 与 `acceptance.json`。
- [x] P2 写明 20 题不是主结果，并给出阶段三 original 84.6%（500 槽）。
- [x] P7 写 83.2 对 84.6、区间 [−6.2, 3.0]、粗粒度 45.0%、6.45 秒对 1.12 秒，并分开两台机器。
- [x] 表内文字不低于 18 磅。页脚 14 磅，已在用法说明里标明不是正文。

### 讲稿

- [x] `script.md` 分成 25 秒、35 秒、30 秒。P1+P2 字符数 239，按 4.2 字/秒约 57 秒。
- [x] P1 稳速约 27 秒，稿内写了可删的半句。
- [ ] 尚未用手机实讲计时。走表安排在 11-22 20:00。

### 报告、数据和贡献

- [x] 报告第 1、2、3、8 节初稿在 `report-draft.md`，每节有数字和路径。
- [ ] 第 8 节里成员二、三、四的两句仍是待写。本人不代写。
- [ ] 全文 `report.pdf` 未排版。这是成员四 11-22 16:00 的汇编，不是阶段一单独能交的 PDF。
- [x] `data/README.md` 写了五个 gz 的 sha256、2655 题、嵌套清单和许可边界。
- [x] `contributions.md` 有成员一的运行目录、配置哈希和核验边界。

### 案例和 QA

- [x] M1-01、M1-02、M1-03 有问题 ID、问题、参考答案、首行行为、score 和 token。
- [x] QA 10 题，每题有 15 秒答案和不能说的话。
- [ ] 成员二尚未在分支上复核这三条的 ID。截止 11-22 12:00 之后由他勾。

### 现场

- [x] 成员一不占用那 1 分钟运行证据。提问备用文件写在证据清单里。
- [ ] 备份录屏未做。成员一不是这 60 秒的主讲，录屏列为可选；若做，文件名仍是 TODO。

## (a) 实验证据清单

| 项 | 代码或命令 | 配置 | 记录 | 和哪一个数字对应 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 取数 | `python -m reproduction prepare` | 无单独配置，提交号写在 `reproduction/data.py` | 下载后应与 `manifests/resources.json` 的 sha256 一致 | 2,655 题；五个位置文件 | 命令已有。本工作区没有 `data/raw/`。不要把 gz 打进 zip |
| 样本清单 | 无命令，直接打开 json | `manifests/smoke.json`、`pilot.json`、`main.json` | seed 42，population 2655 | 20/100/500 嵌套。已在本环境核对前缀关系为真 | 已有 |
| 离线预算计划 | `python -m reproduction plan --config configs/stage1.json` | `configs/stage1.json` | 打印槽数，应为 300 | smoke 矩阵 | 需在有数据的机器上跑。本环境缺原始数据，未跑 |
| 正式运行 | `python -m reproduction run --config configs/stage1.json` | 同上 | 运行目录 `outputs/stage1/d54b3118c61ea4930624` | 300/300 | 缺失于仓库。组内路径就是验收报告里的这个目录。sha256 未在仓库中，成员一补 |
| 配置哈希 | 写在 `acceptance.json` 的 `config_hash` | `621ac92b0374e28d2773616142ea7949288aea0f2d5571a812e93289b7364667` | 与 run 绑定 | 防止现在的 `stage1.json` 被说成后来改过仍同一轮 | 已有 |
| 逐条轻量输出 | 无新命令 | — | `reports/stage1-acceptance/predictions.jsonl`，300 行 | 案例三条；EM 可由此重算为 0.92、0.87、0.64 | 已有。不含问题文本和完整提示 |
| 逐条全文 | `python scripts/accept_stage1.py outputs/stage1/d54b3118c61ea4930624` | 需要当时的 run.json、results.jsonl、cache 和数据 | 脚本会重评分并核对提示 | `acceptance.json` 里 `offline_rescore_identical: true` | 缺失于仓库。预计耗时仓库没有写。不要在没有 cache 的机器上假装跑过 |
| 汇总 | 打开即可 | — | `summary.json`、`summary.md`、`REPORT.md` | P2 的表；位置 EM 95/95/90/90/90 | 已有 |
| 种子 | 配置和清单里的 seed 42 | `configs/stage1.json` | 清单的 `selection` 字段 | 划分可重复 | 已有 |
| 调用记录 | 成功响应在 `cache/api/` | cache key 不含密钥 | `predictions.jsonl` 里有 cache_key、usage、fingerprint、时间 | Q7、Q10 | 缓存目录被 gitignore。成员一列出组内 cache 根路径，不把 key 写进文档 |
| 图 | 阶段一没有单独的位置图 | — | 位置数字在 `summary.md` | P2 不放图 | 不需要补画。主比较图是成员三的 `positions.png` |

现场 1 分钟不由成员一讲。提问时按这个顺序打开，控制在 20 秒：

1. `reports/stage1-acceptance/acceptance.json` 的 success 300、failed 0、missing 0。
2. `predictions.jsonl` 里 M1-01 的 `...:1:bm25_4x`，指出 score 0.0 和 compressed_tokens 822。
3. `manifests/smoke.json` 的第一个 ID，它就是 M1-01 的问题 ID。

独立核验，不调用 API：用 300 行预测按方法求 score 均值，应得到 0.92、0.87、0.64，与 `acceptance.json` 的 `em_percent` 一致。本环境已经对过这 300 行。完整提示重放做不到，因为 `accept_stage1.py` 还要组内的 prompt 和 cache。

## (b) 需制作材料明细

| 交付物 | zip 位置 | 格式和篇幅 | 截止（北京时间） | 核验人 | 怎么验收 |
| --- | --- | --- | --- | --- | --- |
| P1、P2 | `slides.pptx` 第 1–2 页 | 16:9；标题 ≥28 磅；表 ≥18 磅；口播 60 秒 | 已交初稿；11-22 16:00 前确认没被改数 | 成员二看 ID 和 92/84.6 没有混用 | 打开 pptx，对照 `01-number-registry.md` |
| P7 | `slides.pptx` 最后一页主讲 | 30 秒 | 同上 | 成员三看区间，成员四看 45.0 和 6.45 | 页上同时出现 83.2 和 45.0，且写明不是同一台机器 |
| 讲稿 | 不进 zip，答辩用 | `script.md` | 已交 | 成员四在 20:00 走表 | 手机计时 P1+P2 ≤60 秒，P7 ≤30 秒 |
| 报告 1–3、8 节 | `report.pdf` 对应节 | 合计约 2.2 页，正文 11–12 磅 | 初稿已交；12:00 前不再加新数 | 成员二核第 2 节，成员四核第 8 节的别人句子 | 每个百分数能指回 registry |
| 数据说明 | `data/README.md` | 来源、许可、划分、ID，不附带 gz | 已交初稿 | 成员二 | sha256 与 `resources.json` 逐条一致 |
| 贡献段 | `contributions.md` 成员一 | 一段，含 run_id 和做不到的核验 | 已交 | 成员四 | 没有把阶段三的 3500 槽写进成员一 |
| 案例 | `results/cases/M1-01.md` 至 `M1-03.md` | 三条；打包时从 `cases.md` 拆出 | 已交内容；16:00 由成员四拆文件 | 成员二 | 问题 ID 出现在 `manifests/smoke.json` |
| QA | 不进 zip | 10 题 | 已交 | 本人 20:00 前各自读一遍 | 答案里的路径能打开 |
| 阶段一结果 | `results/stage1/` | 复制 `REPORT.md`、`summary.md`、`summary.json`、`acceptance.json`、`predictions.jsonl` | 11-22 16:00 打包时复制 | 成员四 | 复制后 300 行仍在 |
| 组内全文路径 | `results/stage1/SOURCE.txt` | 路径加 sha256，不放全文 | 11-22 12:00，成员一补 sha256 | 成员二 | 文件不存在则 SOURCE.txt 写明未取得，不留空 |
| 录屏 | 可选 `results/demo/member1-qa.mp4` | 不超过 20 秒，无密钥 | 11-22 18:00 前若要做 | 成员四 | 不做也可以，因为 60 秒证据不是成员一的 |

## 课程五项里由成员一讲解的证据

继续在 `stage1-foundation` 上推进。对照 `docs/presentation/02-score-evidence.md`。被点名时按这个顺序打开文件。未勾选项不能说成已经复核。

| 项 | 打开什么 | 8 分目标下还缺的 |
| --- | --- | --- |
| 理解与范围 | `manifests/resources.json` 的两个提交号；`docs/experiments.md` 的 100 题范围 | P 编号仍是 Pxx |
| 数据与实现 | `data/README.md` 的 sha256；`reproduction/data.py` 的 `question_id`；`configs/stage1.json` | `python -m reproduction prepare` 后的 sha256 输出还没写入 `results/stage1/SOURCE.txt` |
| 对照与消融 | 阶段一 smoke 的 92.0/87.0/64.0 在 `reports/stage1-acceptance/acceptance.json`；主比较 84.6 在 `reports/stage3-main/summary.json` | 这两个分母不同，口播不能合成一个“退步” |
| 错误分析 | `docs/presentation/members/member1/cases.md` 的 M1-01 至 M1-03 | 全组还缺成员二、三的案例才到 10 条 |
| 交付与答问 | `predictions.jsonl` 300 行；`qa.md` 10 题 | 组内 run 目录 `outputs/stage1/d54b3118c61ea4930624` 的 sha256 未记录。手机实讲未做 |

离线检查是重算 `predictions.jsonl` 的三个 EM，应得到 0.92、0.87、0.64。`python scripts/accept_stage1.py outputs/stage1/d54b3118c61ea4930624` 才是带完整提示的复核，仓库里没有该目录，不能勾成这次已跑。密钥不进入 `data/README.md` 或案例。

2026-11-21 已额外跑通 `scripts/audit_stage1_offline.py`：隔离失败 0、预算违规 0、重评分不一致 0，见 `reports/stage1-supplement/offline-audit.json`。13 条真实槽在 `reports/stage1-supplement/cases.md`。这仍是 DeepSeek 记录，不是 Cursor。cursor_dialogue 关卡未通过，不能勾“已有受控对话基线”。
