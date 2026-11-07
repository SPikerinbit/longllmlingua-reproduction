# 第二阶段交接记录（成员二 → 成员三/四）

分支：`stage2-compression`（基于 `stage1-foundation`）。本记录在本地运行完成后填写；
未复核前不创建 `stage2-ready` 标签。

## 1. 本阶段交付物

| 产物 | 路径 |
| --- | --- |
| 压缩适配与追踪 | `reproduction/compression.py`、`reproduction/llmlingua_pkg.py` |
| 子序列恢复 | `reproduction/recovery.py` |
| 第二阶段运行入口 | `reproduction/stage2.py`（`plan` / `run` / `summarize` / `casebook`） |
| 配置 | `configs/stage2.json`（主矩阵 4 方法 × 5 位置 × smoke） |
| 测试 | `tests/test_stage2.py`（11 项，离线） |
| 验收脚本 | `scripts/accept_stage2.py`（离线，不调 API） |
| 开关探针 | `scripts/npu_switch_probe.py`（需压缩模型，仅主机上运行） |
| 参数映射与差异表 | `docs/stage2-parameter-map.md` |
| 实现说明 | `docs/stage2-implementation.md` |
| 答辩材料 | `docs/stage2-defense-notes.md` |
| smoke 结果与报告 | `outputs/stage2/a1bd26fe3d82dea3f65d/`、`reports/stage2-smoke/` |
| 服务器依赖 | `requirements-stage2.txt` |

## 2. 对第一阶段接口的影响

- 修复 `reproduction/runner.py:verify_resources()` 的跨平台问题：清单里的路径反斜杠归一化，
  文本文件 sha256 兼容 CRLF/LF（`vendor/deepseek_tokenizer/LICENSE` 在 Linux 检出后按 LF 校验）；
  未改动数据文件与清单内容。
- 第二阶段未修改阶段一的 `methods.build_prompt`、答案缓存、评分入口；`build_prompt` 之外的
  压缩入口为 `reproduction.stage2`，逐槽位结果字段见 `docs/stage2-implementation.md`。
- `reports/smoke-plan.json` 因实现哈希变化重新生成（`config_hash` 变化、`cache_hits` 归零），
  属于可重建产物。

## 3. 运行方式（第三阶段）

同一套缓存与重跑语义：

```bash
PYTHONPATH=. python -m reproduction.stage2 plan
PYTHONPATH=. python -m reproduction.stage2 run --limit 3   # 小样本真实调用
PYTHONPATH=. python -m reproduction.stage2 run             # 矩阵，断点续跑
PYTHONPATH=. python -m reproduction.stage2 summarize outputs/stage2/<run_id>
PYTHONPATH=. python -m reproduction.stage2 casebook outputs/stage2/<run_id>
PYTHONPATH=. python scripts/accept_stage2.py outputs/stage2/<run_id>
```

- 压缩缓存 `cache/compress2/<key>.json` 与问答缓存 `cache/api/<key>.json` 分开；只改恢复配置时
  复用原始回答、不重调 API，也不重跑压缩。
- 运行目录 `outputs/stage2/<run_id>/results.jsonl` 追加写；中断后重跑按 `slot_id` 续跑。
- 问答请求仍走 `max_requests_per_run` 上限与阶段一缓存口径；`DeepSeekClient` 未改动。

## 4. 验收证据（详见 `reports/stage2-smoke/REPORT.md`）

- 2026-11-07 02:04:10–02:51:19 在 Ascend 910B4 上完成 400 槽（run_id
  `a1bd26fe3d82dea3f65d`，config_hash `bbaa854bd830f8e1…`、impl_hash `b9de0421e01d1439…`）；
  success 400、failed 0、missing 0。
- 主结果：llmlingua_2x EM 0.620 / 2.05x、llmlingua_4x 0.460 / 4.17x、
  longllmlingua_2x 0.940 / 2.09x、longllmlingua_4x 0.880 / 4.10x（5 位置平均）。
- 预算：硬约束满足 396/400（99.0%），4 条轻微超标（同一题 longllmlingua_4x，超标 0.9%–1.6%）
  已如实记录，未改写；自然单轮结果保留在 `trace.attempts[0]`。
- 开关：`scripts/npu_switch_probe.py` 六组对比（restrict / 问题感知细粒度 / 动态预算 / 重排序 /
  LLMLingua 对照）均观察到对应变化；问题感知排名在 100/100 样本改变保留文档。
- 恢复：LongLLMLingua 2x/4x 改变回答比例 9%/12%，恢复前后 EM 相同；10 条离线重放一致。
- 验收脚本 `scripts/accept_stage2.py` 7 项检查全部通过（`reports/smoke-stage2-acceptance.json`）。
- 无 gold 泄漏：方法层只接收 `visible_sample` 字段，验收脚本检查生成链路；
- 第三阶段可直接消费：`results.jsonl` 字段清单与阶段一兼容并扩展。

## 5. 已知差异与未实现项（不冒充消融）

| 项 | 状态 |
| --- | --- |
| τ_ins=0.85、τ_que=0.9 | 固定提交的 `compress_prompt` 路径未暴露；如实登记，未自实现 |
| k=2（粗细粒度控制系数） | 用 `context_level_target_token=2×target_token` 近似，已在差异表说明 |
| restrict | 官方硬编码在文档级 ranker 内、不进入最终提示；本项目开关化后语义一致 |
| 恢复分词器 | 论文用 LLaMA-2 tokenizer，本项目用 DeepSeek 分词器（用户已确认） |
| 压缩模型 | 论文 LLaMA-2-7B-Chat；本项目用 `NousResearch/Llama-2-7b-chat-hf` 镜像（同权重，ungated） |
| 问答模型 | 论文 GPT-3.5-Turbo；本项目沿用阶段一 deepseek-flash |
| 硬件 | 论文 V100-32G；本项目 Ascend 910B4 32GB（fp16、eager attention） |
| 重排序 | 主矩阵关闭（AGENTS §3），`reorder_context` 开关留给阶段四 |

## 6. 资源与成本

- ModelArts Ascend 910B4 Notebook（`/cache` 18TB，32GB HBM），模型 13.48GB fp16；
  压缩峰值显存约 16.7GB，加载 ~2s、移动到 NPU ~5s，单槽压缩 3–7s（2x/4x 与重试次数相关）。
- cache：13 组跨位置提示完全相同（4x 压缩未保留 gold 文档、保留的 6 篇非 gold 文档相对顺序不变，共 27 槽），其中 14 槽复用缓存回答；
  因此 400 槽对应 386 个唯一提示；第三阶段做位置配对统计时须按提示哈希识别这些退化槽位。
- API：本阶段 smoke 400 槽中 386 条为本轮新请求、14 条提示内容与更早槽位相同而命中问答缓存
  （复用真实回答、未重复计费）；合计输入 437,149 token、输出 30,655 token，问答模型与阶段一相同。
- 运行环境：CANN 8.5.2、torch 2.7.1 + torch_npu 2.7.1.post2、transformers 4.53.1；
  模型完整性（sha256、tensor 数、index 校验）由独立复核确认。
- 轻量产物已入库：`reports/stage2-smoke/{REPORT.md,summary.md,summary.json,casebook.md,run.json,accepted-sample.jsonl}`。
- 完整 `results.jsonl`（8.4MB，400 槽）、`cache/api`、`cache/compress2`、运行日志与 npu 探针脚本
  已从运行机器拷回成员二本地的 `data/scratch/modelarts/`（gitignored）；模型权重与机器自身文件未拷。
  仓库按约定只保留轻量产物；组员做作业/报告/复核/答辩需要逐槽文件时向成员二索取。

## 7. 待办

- [ ] 队友复核第二阶段入口、配置与产物；
- [ ] 复核通过后创建 `stage2-ready` 标签；
- [ ] 阶段三在 main 集上复用本阶段入口；
- [ ] 阶段四基于开关清单做单机制消融（含重排序单独实验）。
