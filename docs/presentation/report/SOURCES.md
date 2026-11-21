# G14报告来源清单

核对日期：2026-11-21（Asia/Shanghai）。本目录未上传、未checkout仓库、未修改源代码/原结果。报告来源为既有实验记录及本次只读核验。

## 分支头（本次观测，不保证后续不移动）

- [stage1-foundation](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/fba1b896f889d30087280cbe57f8e5c0d161ac03)：`fba1b896f889d30087280cbe57f8e5c0d161ac03`
- [stage2-compression](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/a64294fe86584395e87a33867261094ff4cbf596)：`a64294fe86584395e87a33867261094ff4cbf596`
- [stage3-main-comparison](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/e07ac7726faa364e15b1ff6b2ab0299c0aa84883)：`e07ac7726faa364e15b1ff6b2ab0299c0aa84883`
- [stage4-ablation-efficiency](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/f08b229b3b650ab7c82aa366ba83a895d87f5fe9)：`f08b229b3b650ab7c82aa366ba83a895d87f5fe9`

## 来源用途

- `report-source-updated.md`：仓库侧最终源稿回传；旧稿、五项证据和矩阵保留作变更对照，不视为最新完成状态。
- `canonical-stage1/`：阶段一真实预测、清单、验收与先前离线审计；13案例首行和score本轮逐条核验。
- `stage1-cases.md`：本轮GitHub只读工具取得的13槽原文；`cases-verified.json`含完整ID、参考、首行、token、原始带区时间。
- `stage2-acceptance-remote.json`：本轮只读取得396/400；`g1/verification-stage2.json`与REPORT提供历史压缩记录，若有旧副本不覆盖canonical。
- `g1/summary.json`、`g1/run.json`：CUDA主比较；`stage3-stats-remote.json`本轮取得，且与既有`g2/stats.json`对象一致。
- `g1/parameter-map.md`：方法与固定实现差异。文中§编号以论文PDF为准，不机械沿用映射表旧节号。
- `g2/ablation.csv`、`g2/efficiency.csv`、`g2/coverage.json`、`g2/*-run.json`：NPU消融与效率独立批次；远端ablation表与本地CSV一致。
- `g2/analyze_stage4.py`：只读核对no_recovery由score_before_recovery派生，未执行；不作为新代码或新模型结果。
- `g2/recovery-cases.json`：3条恢复负例，来自2题；不补造参考答案。
- `g2/environment-current.json`：阶段四Python、torch、torch-npu等环境；不含CANN。
- 图1：用户指定论文PDF `/workspace/slides/g14-member1-NrWZBb/sources/paper/LongLLMLingua.pdf` 的图2；实际裁图取自已有本地`paper/figure2.png`，保存`figures/paper-figure2.png`。
- 图2：本报告依据CUDA summary.json 的真实groups绘制，保存`figures/stage3-position.png`。
- PPT来源核验参考：`/workspace/slides/g14-full-Kgr53d/deliverables/G14-LongLLMLingua-sources-verification-v3.md`；不编辑或另制PPT。
- `configs/stage3-pilot-as-run.json`不存在于推荐仓库分支，本轮只读请求404；本报告不使用该路径。真实pilot快照为`reports/stage3-main/run.json`。
- 最新43项离线测试通过由父任务回传；本报告生成未执行该测试集，未新增推理。

## 正规文献页（本轮已打开核对）

- [[1] Jiang, H., Wu, Q., Luo, X., Li, D., Lin, C.-Y., Yang, Y., & Qiu, L. 2024. LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression. ACL 2024 (Long Papers). 本报告对照arXiv:2310.06839v2。](https://aclanthology.org/2024.acl-long.91/)
- [[2] Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. 2024. Lost in the Middle: How Language Models Use Long Contexts. Transactions of the Association for Computational Linguistics, 12:157–173.](https://aclanthology.org/2024.tacl-1.9/)
- [[3] Kwiatkowski, T., et al. 2019. Natural Questions: A Benchmark for Question Answering Research. Transactions of the Association for Computational Linguistics, 7:453–466.](https://aclanthology.org/Q19-1026/)
- [[4] Jiang, H., Wu, Q., Lin, C.-Y., Yang, Y., & Qiu, L. 2023. LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models. EMNLP 2023.](https://aclanthology.org/2023.emnlp-main.825/)

## 随附来源快照 SHA-256（本地副本）

这些校验和不冒充尚未取得的stage2/3/4完整输出缓存校验和。

- `sources/acceptance-matrix.md`  `8b6f420d19fa4928fc2607ccb9f31e677d943153a6e1d0eaf3c6c6a8d892ef30`
- `sources/branch-heads.json`  `7435e4d514ce5756c9c9768c7148c918a1bd3ca6430382cd66fababd6d127659`
- `sources/canonical-stage1/acceptance.json`  `ff0f76de6d5805961e943a72c694d7ef9c374ccd03b5687554956d5c5d0b1ad2`
- `sources/canonical-stage1/offline-audit.json`  `cb82a0de26abc42fa31d9cf404354e2649d4e94819668784c79be9418ced612f`
- `sources/canonical-stage1/predictions.jsonl`  `cac37c9e84678f2f591af8c4f6ccdb7a69d010cf71eae5678b85109bcb27bd62`
- `sources/canonical-stage1/smoke.json`  `19adc9f2419d458733ceda7fe903f375a5f7f449d37ae037a7ae77048320ffc7`
- `sources/canonical-stage1/source-refs.json`  `0ff822600fa12ce031d05732ca5adc903425f3867a8fc6ea015426d201488355`
- `sources/canonical-stage1/stage1.json`  `45870fb32fc3d603a0fd9408a33e6a2dfdefe64c5dd876b2240893fc162d5dd6`
- `sources/cases-verified.json`  `5627c2f6ed3188bcf4c6b61619d79661d42917a9dd09b53637b9ab5d6020b8a1`
- `sources/docs/presentation/01-number-registry.md`  `c12fce7551765680bab457f2dd791bbe3827cc89142c5e79b3ff282cbd056d71`
- `sources/five-evidence.md`  `ade99fb2a58dabe62d44ae767bb4f2d10316e209acaf416ab188ec0db2ee75b4`
- `sources/g1/REPORT-stage2.md`  `7dc9d1df13bcea9ed0d9c504cf28122ea349ef3be70a340f3cf6be0d1fd2c988`
- `sources/g1/acceptance-stage2.json`  `f60582980375114a606c87a6f3b2c8f6f484c44e0880b289e295312f4d28a77f`
- `sources/g1/parameter-map.md`  `dc70be7a39306986397ee88778212b60b43f592ea4e2dc43f352a602ce891843`
- `sources/g1/run.json`  `433eb590541e62b4e402fc8d8d1c09570a5b26a7f533f150f7ea29ff03ef3ffd`
- `sources/g1/summary.json`  `435043bf6971bb3cd2bfbf2d1a26045b33378658453a82343ab411a27cef8a02`
- `sources/g1/verification-stage2.json`  `095a6e9cc8c3d6b7194b05287088c8d438f3a038ad278a3d523f46770dc86db3`
- `sources/g2/RESULTS.md`  `7819b7ec7434d4459398a7d5beae8b73642e6ce00cb1d5fd985b50e4b2f68c0c`
- `sources/g2/ablation-run.json`  `0b7c5f8c10a25ad569b73067d0f12c002c4591a705d3e048799db291b9cf5e71`
- `sources/g2/ablation.csv`  `d23b63dc6450bf6eecf4e00caa504f3a50ca19ce9516dee98dfc82fa9d6612d0`
- `sources/g2/analyze_stage4.py`  `58d7adb7a18a8ee612d82093186129b39b84c5ca324c8d1810710591fdae7032`
- `sources/g2/coverage.json`  `d361c2795af955238012c7f087cf07b658ad3fcb9879ddc8da3f2d7fed905ed9`
- `sources/g2/efficiency-run.json`  `1778446711a293fc1e3c1ab2a3ea2821078661be565d26f1de7e3afac70f24fe`
- `sources/g2/efficiency.csv`  `3b27422a7552c44ff164448adf822ff402256786ba502de42ffb10f0292942aa`
- `sources/g2/environment-current.json`  `dd35590d77323e6e2bf27e276e77e2bbb11d990bdc8c1347f2fc01092e62a6b1`
- `sources/g2/recovery-cases.json`  `fb7c4a8d4f53e2048eab1a9d3595941d1b0f26acd244f705986f72e745c4d780`
- `sources/g2/stats.json`  `d8e110232901480083806003e648d7b8fa278cdce3d24ade7d77c167e2275aae`
- `sources/paper/LongLLMLingua.pdf`  `a81090e2589fcef37f310ee2a265076e4560a296a59864c9d43a6e9b62fe3997`
- `sources/report-draft.md`  `d773e490aa6d0a2854098eacdd6d0dd53456e6a1828f828643ca7a20a5b0e9c8`
- `sources/report-source-updated.md`  `3d7ef940c1bc5201c0325ab79656cb00da369b2b254a92d4ecce2a1ac3312939`
- `sources/stage1-cases.md`  `df985056154d41d8f2e0dec34bd753b49b703908b5110cdb325b45b97badfbee`
- `sources/stage2-acceptance-remote.json`  `f60582980375114a606c87a6f3b2c8f6f484c44e0880b289e295312f4d28a77f`
- `sources/stage3-stats-remote.json`  `d8e110232901480083806003e648d7b8fa278cdce3d24ade7d77c167e2275aae`
- `sources/stage4-ablation-remote.csv`  `d23b63dc6450bf6eecf4e00caa504f3a50ca19ce9516dee98dfc82fa9d6612d0`
- 论文PDF SHA-256：`a81090e2589fcef37f310ee2a265076e4560a296a59864c9d43a6e9b62fe3997`
