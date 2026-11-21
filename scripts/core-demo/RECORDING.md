# 录制说明（desktop 安排，这里不启动 GUI）

请在本机桌面打开一个普通终端，16:9 窗口，例如 1920×1080。不要从本脚本去启动或操控终端、浏览器或 ffmpeg，以免和即将开始的录屏冲突。

## 最小命令

```bash
/workspace/g14-local-main/venv/bin/python /workspace/g14-core-demo/run_core_demo.py --all
```

每章结束会等待 Enter。操作员读完再按。不要用空循环或 sleep 去“做出很忙的样子”。压缩和评分本身只需不到一秒；该停的是读屏幕。

如需无暂停核对：

```bash
/workspace/g14-local-main/venv/bin/python /workspace/g14-core-demo/run_core_demo.py --all --no-pause
```

## 后期 60 秒

原始录制会长于 60 秒（因为要读表）。切到约 60 秒时可按 `logs/markers.tsv` 的 START/END epoch 对齐六段，每段约 8–12 秒。若使用变速，成品须标明倍速；把“等人读屏”标成省略，不要写成计算花了那么久。

环境：不需要外网，不需要 API 密钥，不加载大模型。仓库路径 `/workspace/g14-local-main/repo`，解释器 `/workspace/g14-local-main/venv/bin/python`。脚本不要求 HEAD 锁死在某一个提交，只要所需文件还在。

旧的 50 秒 pytest 录像不要改；本目录是新的录制准备。
