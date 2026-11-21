# 核心证据演示入口

这段工程演示走可追溯链：核心代码入口 → 锁定配置与真实样本 → CPU 实测 BM25 压缩与 token 预算 → 对已保存的 DeepSeek 回答做官方首行评分 → 宣读已提交的主比较、消融与效率表。

不是把整个项目实验再跑一遍。不调用问答 API，不加载 LLaMA / LongLLMLingua 权重，不补造缺失的阶段二、三、四完整缓存。阶段一 smoke 有完整 300 条 `predictions.jsonl`；13 条案例是其中的子集。

已完成的 60 秒成片、海报、字幕、解说文稿和剪辑说明在仓库根目录 `evidence/`（`core-evidence-60s.mp4` 等）。本目录只提供可再次在本机终端复现该演示的入口，供核验或补拍；轻量课程汇报 zip 不收入这些演示代码。

## 最小命令

在仓库根目录。交互（每章结束按 Enter 继续，输入 q 结束）：

```bash
./scripts/core-demo/run_all.sh
```

只跑某一章：

```bash
./scripts/core-demo/run_chapter.sh 3
```

无暂停彩排：

```bash
./scripts/core-demo/run_all.sh --no-pause
```

解释器优先使用 `G14_PYTHON`，否则尝试 `/workspace/g14-local-main/venv/bin/python`，再退回 `python3`。仓库路径默认从本脚本向上查找，也可用 `G14_REPO` 或 `--repo` 指定。不要在命令里打印密钥或环境值。日志写在 `scripts/core-demo/logs/`（含 `markers.tsv`），不入库。

章节、停留建议见 `CHAPTERS.md`。录制安排见 `RECORDING.md`；若只是复查已完成的成片，直接打开 `evidence/core-evidence-60s.mp4` 即可，不必重录。剪辑对照以 `evidence/EDIT-MAP.md` 为准，不要把后期处理叠回演示画面。
