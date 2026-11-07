# LongLLMLingua 小组复现

四人接力完成 NaturalQuestions 多文档问答上的 LongLLMLingua 方法复现。**第一阶段已通过本机技术验收，300 个真实结果全部完成，等待队友复核和 GitHub 交接。**

## 从这里开始

1. 阅读 [AGENTS.md](AGENTS.md)：四人分工、实验口径、接口、验收和 GitHub 规则。
2. 第一阶段负责人按 [阶段一清单](docs/stage1-checklist.md) 推进环境、数据、原始提示与 BM25 基线。
3. 每次交接复制并填写 [交接模板](docs/handoff-template.md)，提交本阶段代码、结果和材料供下一位成员复核。

| 阶段 | 主责 | 核心产物 |
| --- | --- | --- |
| 一：数据与基线 | 项目发起人 | 数据清单、实验底座、原始提示/BM25 真实结果 |
| 二：压缩方法 | 成员二 | LLMLingua/LongLLMLingua、机制开关、过程案例 |
| 三：主实验 | 成员三 | 批量运行、正式主表、位置曲线与统计分析 |
| 四：消融与效率 | 成员四 | 消融、效率、错误分析与最终汇编 |

## 当前状态

已建立独立 `.venv`，下载五份 NQ 数据和官方 DeepSeek 分词器，完成原始提示、BM25、API 适配、缓存与评分。已验证 2,655 题 × 五位置全部对齐，通过 22 项离线测试与依赖检查，完成 300 个真实结果的提示、缓存、预算和重评分复核。未下载大模型权重。

结果入口：[验收报告](reports/stage1-acceptance/REPORT.md)、[五位置结果表](reports/stage1-acceptance/summary.md)、[机器可读验收记录](reports/stage1-acceptance/acceptance.json)。原始提示、BM25 2x、BM25 4x 平均 EM 分别为 92%、87%、64%；这是 20 题的流程验收，不能替代正式 500 题实验。

成员姓名与小组服务器配置待登记。第一阶段已通过本机验收；上传后由队友复核 PR，复核通过后再合并并标记 `stage1-ready`。

远程仓库：[SPikerinbit/longllmlingua-reproduction](https://github.com/SPikerinbit/longllmlingua-reproduction)（私有）。完整第一阶段交付在 `stage1-foundation` 分支，按 Pull Request 复核后合并至 `main`；队友复核前不创建 `stage1-ready` 标签。

首次克隆请指定阶段一分支：

```powershell
git clone --branch stage1-foundation https://github.com/SPikerinbit/longllmlingua-reproduction.git
cd longllmlingua-reproduction
```

## 第二阶段：压缩方法与机制验证

第二阶段在 `stage2-compression` 分支进行，承接第一阶段的数据、模板、分词器、API 缓存与评分流程：

- 固定官方提交的 `PromptCompressor` 通过适配层接入（`reproduction/compression.py`），LLMLingua 与
  LongLLMLingua 共用同一 LLaMA-2-7B-Chat 压缩模型；
- 2x/4x 主表使用硬预算（按固定 DeepSeek 分词器实测完整提示），同时保留库自然压缩结果用于差异说明；
- `restrict`、问题感知粗粒度、问题感知细粒度、动态预算、重排序与子序列恢复都是独立开关，逐项对照见
  [参数映射与差异表](docs/stage2-parameter-map.md)；
- 子序列恢复在问答之后执行，恢复前后回答都保存并都评分；逐槽位输出文档分数、保留文档、预算、
  文本变化追踪与压缩耗时。

在 Linux GPU 或 NPU 机器上运行（本机 CPU 只跑离线测试与 `plan`）：

```bash
PYTHONPATH=. python -m reproduction.stage2 plan
PYTHONPATH=. python -m reproduction.stage2 run --limit 3
PYTHONPATH=. python -m reproduction.stage2 run
PYTHONPATH=. python -m reproduction.stage2 summarize outputs/stage2/<运行ID>
PYTHONPATH=. python -m reproduction.stage2 casebook outputs/stage2/<运行ID>
```

接口、产物与已知差异见 [第二阶段实现说明](docs/stage2-implementation.md)；服务器依赖见
[requirements-stage2.txt](requirements-stage2.txt)。模型权重不入库，路径由
[configs/stage2.json](configs/stage2.json) 的 `compressor.model_path` 指定。

本阶段 smoke 的完整逐槽记录（`results.jsonl`，约 8.6MB）、压缩/问答缓存与运行日志不进入 Git：
仓库只保留 `reports/stage2-smoke/` 下的轻量汇总与样例。完整文件保存在成员二本地的
`data/scratch/modelarts/`（已被 `.gitignore` 忽略）。后续组员做作业、准备报告、复核或答辩如果
需要逐槽文件、缓存或日志，可向成员二索取。

## 填入密钥并开始运行

打开根目录 **`.env`**，在 `DEEPSEEK_API_KEY=` 后填入自己的密钥。该文件已被 Git 忽略，不要把密钥写进公共配置或报告。环境变量优先于 `.env`；如存在同名旧环境变量，应先更新。

[configs/stage1.json](configs/stage1.json) 已预填：供应商 DeepSeek、官方地址 `https://api.deepseek.com`、模型 `deepseek-flash`、非思考模式、temperature=0、最大输出 512 token。当前对应模型版本记录为 `DeepSeek-V4.1-Flash-1017`；这是调研记录，不是服务商保证的固定快照。运行另存 API 返回的 model、fingerprint（如提供）及时间。

在项目根目录的 PowerShell 执行：

```powershell
# 仅检查配置和密钥是否存在，不发送请求
.\.venv\Scripts\python.exe -m reproduction check
# 先做 3 个新逻辑请求，产生真实费用
.\.venv\Scripts\python.exe -m reproduction run --limit 3
# 续跑整个 smoke，复用已成功结果
.\.venv\Scripts\python.exe -m reproduction run
```

未完成整个矩阵时退出码为 2，限量试运行返回 2 属正常情况。默认 smoke 为 20 题 × 五位置 × 三种基线，共 300 个结果槽位。同一运行不要同时开两个进程。

离线操作：

```powershell
# 下载/验证固定版本的数据、参考源码和分词器，不下载权重
.\.venv\Scripts\python.exe -m reproduction prepare
# 对整个 smoke 做 token 预算统计，不调用 API
.\.venv\Scripts\python.exe -m reproduction plan
# 离线测试，模拟响应只写临时目录，不作为实验结果
.\.venv\Scripts\python.exe -m pytest
```

真实运行后按输出的运行目录重新评分，不再调用 API：

```powershell
# 将 <运行ID> 替换为 run 命令实际打印的目录名
.\.venv\Scripts\python.exe -m reproduction summarize outputs/stage1/<运行ID>
```

完整本机技术验收也可离线复查，不调用 API：

```powershell
.\.venv\Scripts\python.exe scripts\accept_stage1.py outputs/stage1/d54b3118c61ea4930624
```

## 在另一台电脑重建环境

本机 Python 3.12.7；先在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
# 仅首次配置时复制；不要覆盖已有密钥文件
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m reproduction prepare
```

`requirements-lock.txt` 固定本机完整依赖；跨系统可先用 `requirements.txt` 的直接依赖并保存新解析结果。Linux 使用 `python3 -m venv .venv`，随后用 `.venv/bin/python` 替换 Windows Python 路径；小组服务器尚未实测。第一阶段 CPU 足够，不安装 PyTorch/CUDA。

## 数据和输出

- `manifests/`：可入库的来源、校验值及 smoke/pilot/main 嵌套 ID 清单，seed=42。
- `data/raw/`：五份完整 NQ 数据，不入库。`data/tokenizer/`：固定官方分词器，不含权重。
- `vendor/`：固定上游模板、评分函数、参考源码和许可证；评分直接调用上游函数。
- `reports/data-validation.json`：全部五位置数据校验。`reports/smoke-plan.json`：离线预算，不是真实问答结果。
- `cache/api/`：成功响应缓存，不入库，不含 API 密钥。
- `outputs/stage1/<运行ID>/`：配置、逐样本 `results.jsonl`、可重新生成的 `summary.json` / `summary.md`，不自动发布。

当前 smoke 本地预算为 **524,775 输入文本 token**、最多 **153,600 输出 token**，不包括重试；实际通常远低于输出上限。最初 128 上限导致部分回答截断，验收已统一改为 512，旧试运行记录保留但不混入最终矩阵。本地只计提示文本，不计服务端聊天封装；公开分词器与在线服务可能有版本差异，费用以 API usage 为准。

每次 run 最多 300 个新逻辑调用，每个调用最多 3 次网络尝试，最坏 900 次尝试；`--limit` 限制本次逻辑调用数。网络超时时服务端可能已计费，重试可能重复计费。401/402/403 会停止本轮；空回答和输出截断不计成功、不缓存。

成功响应先落缓存再写结果；重跑跳过成功槽位并补跑失败。修改配置/实现产生新运行目录，相同提示和生成配置可复用原缓存，并记录其来源。完整预测和提示留在忽略目录；GitHub 仅提交经检查的轻量汇总与必要案例。

普通退出自动清理 `.running` 标记。强制结束若留标记，确认旧进程已停止后再手动删除该输出目录的标记并续跑。

接口、预算策略与差异见 [实现说明](docs/stage1-implementation.md)；当前待验收项见 [阶段一交接](docs/handoff-stage1.md)，本阶段讲解提纲见 [答辩笔记](docs/stage1-defense-notes.md)。

## 资源

- [论文](https://arxiv.org/abs/2310.06839v2)，本机可选源码位于 `arXiv-2310.06839v2/`，不随仓库分发，可从 arXiv 获取。
- [微软官方实现](https://github.com/microsoft/LLMLingua)，固定版本和复用边界见 AGENTS.md。
- [NQ 多文档数据及评估](https://github.com/nelson-liu/lost-in-the-middle)。
- [官方 DeepSeek 分词器](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/tree/314113f8a7dadb388215396ba5fbee2c610a04d6)，许可保存在 vendor/deepseek_tokenizer/LICENSE。
- [DeepSeek 官方模型与价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)、[思考模式](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode/)。

范围为 NQ 20 文档、五种答案位置、2x/4x 压缩、四种方法及关键消融。使用现有 API 的结果属于方法级复现，需明确与论文历史问答模型的差异。
