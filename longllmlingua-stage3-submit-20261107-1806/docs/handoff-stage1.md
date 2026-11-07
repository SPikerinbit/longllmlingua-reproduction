# 第一阶段交接记录（本机技术验收通过，待队友复核）

负责人：项目发起人。接收人：成员二，姓名待登记。私有仓库为 https://github.com/SPikerinbit/longllmlingua-reproduction ，完整交付分支 stage1-foundation；通过 PR 交接，尚无验收标签。

## 已交付

- CPU 工程、独立 .venv、直接依赖与完整锁定清单。
- 五份固定 NQ 数据和校验，2,655 题 × 五位置全部对齐。
- seed=42 的 20/100/500 嵌套 ID 清单及资源来源校验值。
- 原始提示、BM25 两档预算、DeepSeek 非思考问答、缓存、失败记录、上游评分与汇总。
- 22 项离线测试通过，smoke 离线输入文本预算 524,775 token。
- 接口与答辩说明；密钥文件 .env，供应商与模型已配置。
- 真实 smoke 验收：300/300 槽位成功，失败 0、缺失 0；原始提示/BM25 2x/BM25 4x 平均 EM 为 92%/87%/64%。
- 最终运行：outputs/stage1/d54b3118c61ea4930624；配置摘要 621ac92b0374e28d2773616142ea7949288aea0f2d5571a812e93289b7364667。
- reports/stage1-acceptance/ 包含验收报告、15 组位置汇总、轻量预测和机器可读验收记录。
- 全部提示、预算、缓存请求与回答逐项核对通过，离线重新评分与原汇总一致；实际密钥字符串扫描未发现泄漏。

## 待完成，不能标记 stage1-ready

- [x] 填入密钥后执行 check。
- [x] run --limit 3 验证真实服务端模型别名、fingerprint、usage、输出与配置。
- [x] 完成 run 的 300 个结果槽位，失败/缺失均为 0。
- [x] 从真实预测重建 summary，登记得分、用量、费用估算与耗时；实际扣费以平台账单为准。
- [ ] 成员二按 README 复核，补充成员资料及服务器环境。
- [ ] 核验第二阶段 LLaMA-2 权限；目前没有下载或加载权重。
- [x] 创建私有 GitHub 仓库；完整交付推送至 stage1-foundation。
- [ ] 阶段一 PR 由成员二复核、合并，验收后标记 stage1-ready。

## 接手入口

先阅读 README 和 docs/stage1-implementation.md。第二阶段从 visible_sample/build_prompt 接口接入 LLMLingua/LongLLMLingua，不得把原始 data 行中的答案或 gold 标签传给压缩器。

真实预测已导出为 reports/stage1-acceptance/predictions.jsonl。300 槽位对应 228 个独立成功响应，相同请求复用缓存；按记录用量估算最终矩阵约 0.2385 元。包括早期试运行，成功响应的估算合计约 0.4668 元，另有少量旧版截断及可能的在途请求未完整计量，不能把估算写成平台账单。

首次 128 token 输出上限导致少量截断，已停止该轮并保留旧记录；最终矩阵统一 512 token，不混入旧设置。真实响应返回模型别名 deepseek-flash 和 fingerprint，无法单凭别名证明官方具体快照。

上传 GitHub 时提交轻量汇总、预测和必要案例；完整提示、缓存和旧轮次留在忽略目录。服务器及 LLaMA-2 访问准备归第二阶段，小组成员信息和独立复核仍待登记。
