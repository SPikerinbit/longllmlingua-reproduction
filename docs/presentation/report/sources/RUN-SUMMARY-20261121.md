# 本阶段本地运行摘要

时区：Asia/Shanghai（UTC+8）。仓库提交始终是已推 main `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4`。未推送，未改测试或评分，未覆盖已发表结果文件。工作树在运行后保持干净（`data/raw` 与 `data/tokenizer` 被 gitignore）。

## 路径

- 隔离工作根目录：`/workspace/g14-local-main`
- 本地仓库：`/workspace/g14-local-main/repo`（从 `/tmp/ll-upload-bare2.git` checkout，不是重新拉云端）
- 虚拟环境：`/workspace/g14-local-main/venv`
- 日志与产物：`/workspace/g14-local-main/runs`

## 时间线

见 `runs/timeline.txt`。要点：

- 17:45:50 收集 77 项；无数据基线 72 通过 / 5 失败，退出码 1。
- 17:46:00–17:46:07 `python -m reproduction prepare` 成功，退出码 0。下载五个公开 NQ gz（约 15MB×5）和官方 `tokenizer.json`（6,367,257 字节）。Hugging Face 模型 `deepseek-ai/DeepSeek-V4.1-Flash` revision `314113f8a7dadb388215396ba5fbee2c610a04d6` 为 public、gated=false。未下载 LLaMA 或其它大权重，未使用付费 API 或用户凭证。
- 五个 gz 与 tokenizer 的 sha256 / git blob 与已提交 `manifests/resources.json` 一致。
- 17:46:58–17:47:02 全套 pytest 77 通过，退出码 0。
- 17:47:50 起阶段一至四离线审计写入 `runs/audits/`，与已发表 JSON 在剔除耗时后一致（官方 EM、396/400、消融数字均未变）。`api_calls` 均为 0。
- 17:48:03 `python -m reproduction plan` 的预算数字与已发表 `smoke-plan.json` 一致（slots 与 token 合计相同）。仅 `config_hash` 不同，因为它纳入了实现文件哈希；Linux 检出的 LF 与当初 Windows 记录不同。已发表 plan 文件已恢复，未被覆盖。
- `analyze_stage4.py` 重建到 `runs/stage4-rebuild/`：JSON 与 RESULTS.md 字节级匹配已发表文件；两个 CSV 只差 CRLF/LF，规范化后内容相同。

## 5 个原先失败的测试

1. `test_real_tokenizer_budget_and_order[original-1]`
2. `test_real_tokenizer_budget_and_order[bm25_2x-2]`
3. `test_real_tokenizer_budget_and_order[bm25_4x-4]`
4. `test_full_real_data_nested_manifests`
5. `test_runner_interrupt_resume_and_cache_rebuild`

失败原因都是缺少 pinned `tokenizer.json` 或五个 NQ 原始 gz，不是测试写错。

## 未解决

- 组内阶段二/三/四完整 `results.jsonl`、问答/压缩缓存及其 sha256：在 `/workspace` 与本 bot 授权 store 中未找到可恢复的原始缓存（只有仓库里已提交的轻量结果，以及无关的 `/workspace/yh1` 模拟文件）。不能编造。
- CUDA 具体型号、阶段四 CANN、Cursor 受控问答、P 编号、登记表四人信息、本人确认、录屏与计时：仍缺。
- 课程占位 zip 仍不能直接提交。
- 未更新报告正文和 PPT，也未推 main。

`prepare` 曾把 `manifests/resources.json` 的键改成 POSIX 路径，并把 DeepSeek LICENSE 的摘要改成当前 LF 文件的 1064 字节哈希。已恢复已提交清单。已提交清单里 LICENSE 为 1084 字节的 CRLF 摘要；工作区 LF 文件 1064 字节，`verify_resources` 已按设计接受换行等价。此项可列为文档说明，不是测试失败。
