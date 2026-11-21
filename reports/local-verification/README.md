# 本机离线核验记录（2026-11-21）

时区均为 Asia/Shanghai（UTC+8）。对应已推 `main` 提交 `bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4`。

本目录保存脱敏后的命令、日志、JUnit、环境与依赖清单、数据/分词器哈希、四阶段离线审计和本地作图。它不是新的模型推理，也不包含 `data/raw/*.jsonl.gz`、`data/tokenizer/tokenizer.json`、虚拟环境或密钥。

## 当前验收口径

在仓库根目录先执行 `python -m reproduction prepare`（只下载公开 NQ 五个 jsonl.gz 和官方 `tokenizer.json`，不下载大模型、不调用问答 API），再执行完整 `python -m pytest`。

- 环境：Python 3.13.5，`tokenizers==0.22.1`（`requirements-lock.txt`）。这与阶段四实测记录中的 Python 3.12.0 / tokenizers 0.21.4 不是同一次环境，不能合并。
- 分词器：`deepseek-ai/DeepSeek-V4.1-Flash` revision `314113f8a7dadb388215396ba5fbee2c610a04d6` 的 `tokenizer.json`，sha256 `c90dfa01249db1be4245780a052ede752e1361c612ac6d08e2bdada7d599476b`。
- 五个 NQ 文件的 sha256 与已提交 `manifests/resources.json` 一致，见 `data-tokenizer-sha256.txt`。
- 17:45:50–17:45:51，数据尚未就位：收集 77 项，72 通过、5 失败，退出码 1。见 `pytest-baseline.stdout`、`junit-baseline.xml`。
- 17:46:00–17:46:07，`python -m reproduction prepare` 退出码 0。见 `prepare.stdout`。
- 17:46:58–17:47:02，全套 77 项通过，0 失败，退出码 0，约 3.53 秒。见 `pytest-full.stdout`、`junit-full.xml`。JUnit 时戳带 `+08:00`。
- 四阶段离线审计的 `api_calls` 均为 0；已发表官方分数未改（阶段二仍为 396/400；阶段一官方 EM 仍为 0.92 / 0.87 / 0.64；主比较与消融均值与已提交 JSON 一致）。
- 历史子集“5 个文件共 31 项”仍然成立，但不是当前全套验收入口。较早过程回传中的 36 / 39 / 43 / 44 项应保留为标明日期的历史口径，不要直接改写成 77 而不加说明。

可移植复查（需已准备数据；不联网、不打印环境变量值）：

```bash
# 在仓库根目录
bash reports/local-verification/recheck.sh
```

## 路径说明

原始运行发生在 `/workspace/g14-local-main/repo`，解释器为 `/workspace/g14-local-main/venv/bin/python`。这是普通工作区路径，不是密钥。`*.as-run.txt` 与部分 pytest/JUnit 日志保留当时的绝对路径；`full-pytest.command.relative.txt` 与 `data-tokenizer-sha256.txt` 使用仓库相对路径。JUnit 的 `hostname` 为执行机名 `grok-bot-vm-532414443`，不是凭证。

原始环境快照里曾有两个“某环境变量是否已设置”的布尔标记。凭证值从未写入任何日志；本目录的 `environment.txt` 已去掉这两个标记。

## 仍未解决

阶段二/三/四完整 `results.jsonl`、压缩/问答缓存及其 sha256 仍缺，不能编造。CUDA 具体型号、阶段四 CANN、受控 Cursor 结果仍缺。本目录的图是从已提交轻量指标在 CPU 上重建的，没有覆盖 `reports/stage3-main/positions.*` 或 `reports/stage4-ablation-efficiency/figures/` 里的已发表文件。
