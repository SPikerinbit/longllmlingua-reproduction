# cursor_dialogue 协议

这是一个新的问答设置，不是 DeepSeek API，也不能写成 API 延迟。压缩模型仍然是 LLaMA-2-7B-Chat。Cursor 对话不能代替压缩。

## 2026-11-21 可行性关卡：未通过

本机没有 `agent`、`cursor` 或 `cursor-agent` 可执行文件。公开文档说明 Cursor CLI 可以 `agent -p` 打印回答，也可以 `--mode=ask`，但 Ask 模式仍会读仓库、搜索，print 模式还能使用 shell。[Using Agent in CLI](https://cursor.com/docs/cli/using) 写明 Agent 有文件、搜索、shell 和网页工具。社区记录也说明 `--mode ask` 不是无工具隔离（https://forum.cursor.com/t/ask-mode-terminal-commands/164600/16）。

当前 Cloud Agent 的 Task 子代理同样带工具。在本仓库里启动时，它能看到参考答案、分数和其他条件的结果。文档没有提供关闭全部工具、固定 temperature、或锁定模型快照的开关。`create-chat` 只能新建会话，不能把上面这些条件变成受控实验。

因此没有执行任何 cursor_dialogue 回答。下面的试跑文件只是输入。`reports/cursor_dialogue/` 里没有回复，也没有分数。

## 受控条件

每条槽必须是新的会话，不能 `--resume` 或接着上一题。回答者只能看到该槽的盲提示。不能把 `trial/gold/`、`reports/stage1-acceptance/`、`reports/stage3-main/` 或其他条件的回答交给回答者。不能让回答者搜索网页或打开本仓库。

如果产品做不到“无工具、无仓库、固定采样、可记录模型版本”，这次运行就只是受限环境里的探索，不能用来证明方法更好，也不能和 DeepSeek 的 EM 放在同一张比较表里。

## 最小试跑

固定清单仍是 smoke 20 题 × 位置 1/5/10/15/20 × original、bm25_2x、bm25_4x，共 300 槽，见 `design-slots.json`。这个文件只有 ID，没有问题和答案。

实际准备的试跑只有 3 槽：smoke 第一题、位置 1、三种方法。提示由 `configs/stage1.json`、上游 `qa.prompt` 和已校验的 DeepSeek tokenizer 重建。三种提示的原始/压缩/目标 token 与 `predictions.jsonl` 里同一 slot 的数字一致。这只说明预算重建一致，不是说 Cursor 已经回答了这些题。

300 槽不要启动。先用这 3 槽确认会话是否截断、是否调用工具、能否留下 session 和 model。只要观察到工具或仓库访问，就停止，并把该次记为关卡失败。

## 人怎么跑

1. 在一个空目录里打开新的 Cursor 会话，不要打开本仓库。
2. 只粘贴 `trial/blind/` 里的一个文件。一个文件一个新会话。
3. 保存完整回答、开始和结束时间、界面上能看到的模型名。看不到就写 `unknown`。如果出现工具调用，把工具名记下来，并把 `tools_used` 设为 true。
4. 三条都做完后，把 JSONL 放到本仓库以外的地方再评分。评分命令：

```bash
python scripts/score_cursor_dialogue.py \
  --replies /path/to/replies.jsonl \
  --gold reports/cursor_dialogue/trial/gold/labels.json \
  --out reports/cursor_dialogue/trial/scored.json
```

每行回复至少要有 `slot_id` 和 `answer`。失败或截断也要留行，`answer` 用 null，`status` 写 `failed` 或 `truncated`。没有回复文件时，评分脚本退出码是 2，不会编造分数。

`trial/gold/labels.json` 只给评分用。不要把它放进回答者的会话。
