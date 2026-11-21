# G14报告来源清单（本机核验更新版）

更新日期：2026-11-21（Asia/Shanghai）。仅编辑`/workspace/reports/g14-core-final/`报告产物；未修改repo工作树、原始结果或测试，未上传。

## 当前代码与证据基线

- 本机被测main：`bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4`；环境、时间线、命令和JUnit均指向此代码。
- 用户17:56（Asia/Shanghai）回传当前四头：stage1-foundation `a485190`；stage2-compression `93f74bc`；stage3-main-comparison `32f7b6e`；stage4-ablation-efficiency `6fe6274`。这些是当前分支简写，不拿它们冒充初版文件的取样提交。
- `sources/report-repo-source-20261121.md`来自此次指定的最新版仓库报告；与初版报告Markdown字节相同，后按精确建议更新本文。
- `sources/KNOWLEDGEWORK-SUGGESTIONS-20261121.md`、`sources/RUN-SUMMARY-20261121.md`：此次修改要求及真实运行摘要。

## 本机真实离线核验（当前77项入口）

- `sources/local-verification/`：脱敏命令、stdout/stderr、JUnit、环境与依赖、资源SHA、四阶段审计、plan与阶段四独立重建。证据副本不包含权重、公开数据正文、tokenizer本体、虚拟环境或凭证。
- 2026-11-21 17:45:50–17:45:51（Asia/Shanghai）：完整收集77项，72通过、5因缺公开NQ或固定tokenizer失败，退出1；见baseline日志与JUnit。
- 17:46:00–17:46:07（同日Asia/Shanghai）：prepare成功，只配公开五gz及官方tokenizer.json；不下载LLaMA权重，不调用付费问答API。
- 17:46:58–17:47:02（同日Asia/Shanghai）：完整pytest 77/77、0失败/0跳过、退出0，JUnit耗时3.530秒。见`pytest-full.stdout`、`junit-full.xml`、`timeline.txt`。报告编辑本轮只读检查该证据，没有额外重跑pytest或模型。
- 当前离线环境Python 3.13.5 / tokenizers 0.22.1；不是历史CUDA/NPU推理环境。历史阶段四仍为Python 3.12.0 / tokenizers 0.21.4，历史0.21.0也不合并。
- 官方公开DeepSeek-V4.1-Flash tokenizer固定revision `314113f8a7dadb388215396ba5fbee2c610a04d6`；tokenizer.json SHA-256 `c90dfa01249db1be4245780a052ede752e1361c612ac6d08e2bdada7d599476b`，6,367,257字节。五NQ gz SHA与原清单一致。
- `sources/local-resource-readonly-check.json`：报告编辑对实际六个公开资源只读计算SHA，与脱敏证据逐项一致；未复制原始资源进包。
- 四阶段本机审计均api_calls=0；CUDA主比较、396/400、NPU消融与效率原数不变。阶段四重建写独立目录；JSON/RESULTS.md一致，CSV仅CRLF/LF换行差异。
- `plan/smoke-plan.rerun.json`与published版slots/token合计一致，仅config_hash不同（实现文件换行LF/CRLF）；DeepSeek LICENSE亦有1064/1084字节LF/CRLF等价差异，原清单未覆盖。
- 43项为2026-11-21初版报告制作时历史回传，当时未在该报告环境亲跑。31/36/43/44属历史子集或回传口径，当前不再作为完整验收入口，不据数量差异认定造假。
- 2026-11-21 21:46（Asia/Shanghai）同步最终60秒核心视频：`evidence/core-evidence-60s.mp4`，60.000秒、1920×1080、H.264视频及AAC音轨；SHA-256为`e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e`，与用户给定值和实际源文件一致。旧50秒测试视频不收入本包，也不把旧片videoReview结果套用到新片。
- 讲解音轨采用TTS制作，配中文字幕；最终画面顶栏为普通标题，历史GPU/NPU结果标签保留，不声称真人现场口播。随附`evidence/core-evidence-60s.srt`、`evidence/voice/NARRATION.md`、`evidence/EDIT-MAP.md`与`evidence/poster.png`；语音软件/音色、语速、剪辑和补拍时间轴均有披露。
- 真实GUI终端素材经剪辑并含已披露定格，样本章独立补拍且有镜头调序。展示入口配置、样本可见字段隔离、已完成CPU BM25结果3289→1644→822与gold丢失、对已保存回答评分及首行指标边界、历史CUDA/NPU表。不是六章连续完整实时演算，无现场GPU/NPU/Long新推理，视频不新增问答模型分数。
- 本轮报告编辑读取解说/字幕/剪辑对照，并核对ffprobe元数据、给定视频SHA和所有包内副本；不冒称重新执行整套实验或新片videoReview。PPT内嵌工作另行制作，本报告包不含任何PPT或旧外链版，不宣称Windows已播放。
- 录屏完成不等同真人讲述计时、成员本人参与/确认或新模型实验，这些缺口仍保留；视频不提供新的方法分数。
- 占位资料包已生成，尚缺P号、四人登记信息与本人确认等；不再写zip未打，也不宣称可直接最终提交。

## 初版历史资料锁定头（2026-11-21 16:25–16:34，Asia/Shanghai）

- [stage1-foundation历史快照](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/fba1b896f889d30087280cbe57f8e5c0d161ac03)：`fba1b896f889d30087280cbe57f8e5c0d161ac03`。正文原方法数字继续引用该锁定资料，不伪称这仍是当前分支头。
- [stage2-compression历史快照](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/a64294fe86584395e87a33867261094ff4cbf596)：`a64294fe86584395e87a33867261094ff4cbf596`。正文原方法数字继续引用该锁定资料，不伪称这仍是当前分支头。
- [stage3-main-comparison历史快照](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/e07ac7726faa364e15b1ff6b2ab0299c0aa84883)：`e07ac7726faa364e15b1ff6b2ab0299c0aa84883`。正文原方法数字继续引用该锁定资料，不伪称这仍是当前分支头。
- [stage4-ablation-efficiency历史快照](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/f08b229b3b650ab7c82aa366ba83a895d87f5fe9)：`f08b229b3b650ab7c82aa366ba83a895d87f5fe9`。正文原方法数字继续引用该锁定资料，不伪称这仍是当前分支头。

## 原方法资料用途

- `canonical-stage1/`与`cases-verified.json`：300槽canonical预测、原审计及13真实槽（4题）；此次更新未改首行、分数、token或原始时间。
- `stage1-cases.md`、`stage2-acceptance-remote.json`、`stage3-stats-remote.json`与`stage4-ablation-remote.csv`：初版通过GitHub只读取得的来源快照，不冒称此次重新抓取。
- `g1/summary.json`、`g1/run.json`：CUDA主比较；`g1/parameter-map.md`：有效/无效参数差异；396/400以canonical验收为准。
- `g2/ablation.csv`、`efficiency.csv`及run/coverage/environment/恢复案例：独立NPU批次；完整输出/压缩缓存及其SHA仍未取得，不用新资源哈希冒充。
- `g2/analyze_stage4.py`为原文档制作时源码快照；无恢复行从已有score_before_recovery派生。本机此次真实重建证据另存local-verification/stage4-rebuild/，未覆盖原表。
- 原源稿、五项证据、验收矩阵与`report-source-updated.md`为历史材料，只作变化对照，其中旧的未完成状态不当作当前结论。
- 图1：随附原论文PDF的图2原图截取，`figures/paper-figure2.png`；图2：真实CUDA summary.groups重绘，`figures/stage3-position.png`。原始分数不变，无模拟点。
- 真实pilot配置快照是`reports/stage3-main/run.json`；默认stage3配置是main。不存在的独立pilot-as-run配置不作入口。

## 参考文献与可点击来源（作者在初版已从ACL官方页核对）

- [[1] Jiang, H., Wu, Q., Luo, X., Li, D., Lin, C.-Y., Yang, Y., & Qiu, L. 2024. LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression. ACL 2024 (Long Papers). 本报告对照arXiv:2310.06839v2。](https://aclanthology.org/2024.acl-long.91/)
- [[2] Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. 2024. Lost in the Middle: How Language Models Use Long Contexts. Transactions of the Association for Computational Linguistics, 12:157–173.](https://aclanthology.org/2024.tacl-1.9/)
- [[3] Kwiatkowski, T., et al. 2019. Natural Questions: A Benchmark for Question Answering Research. Transactions of the Association for Computational Linguistics, 7:453–466.](https://aclanthology.org/Q19-1026/)
- [[4] Jiang, H., Wu, Q., Lin, C.-Y., Yang, Y., & Qiu, L. 2023. LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models. EMNLP 2023.](https://aclanthology.org/2023.emnlp-main.825/)
- [[5] G14. 论文参数与固定实现对照（stage2-parameter-map.md）；记录k映射、预压缩、计数和恢复的差异。](https://github.com/SPikerinbit/longllmlingua-reproduction/blob/a64294fe86584395e87a33867261094ff4cbf596/docs/stage2-parameter-map.md)
- [[6] G14. 阶段一离线审计、canonical预测与13槽案例；stage1-foundation公开记录。](https://github.com/SPikerinbit/longllmlingua-reproduction/blob/fba1b896f889d30087280cbe57f8e5c0d161ac03/reports/stage1-supplement/cases.md)
- [[7] G14. CUDA pilot主比较：run.json、summary.json与stats.json；stage3-main-comparison公开记录。](https://github.com/SPikerinbit/longllmlingua-reproduction/blob/e07ac7726faa364e15b1ff6b2ab0299c0aa84883/reports/stage3-main/stats.json)
- [[8] G14. 独立NPU消融、效率与恢复负例；stage4-ablation-efficiency公开记录。](https://github.com/SPikerinbit/longllmlingua-reproduction/tree/f08b229b3b650ab7c82aa366ba83a895d87f5fe9/reports/stage4-ablation-efficiency)
- [[9] Microsoft. LLMLingua公开实现，锁定提交5a4c78ae18ab17a98cf997e8259354e546081d64。](https://github.com/microsoft/LLMLingua/tree/5a4c78ae18ab17a98cf997e8259354e546081d64)
- [[10] Lost in the Middle. 数据、问答模板及评分代码，锁定提交29b8a6d042ce29abccee3db1a73171a107d7e6af。](https://github.com/nelson-liu/lost-in-the-middle/tree/29b8a6d042ce29abccee3db1a73171a107d7e6af)
- [[11] BIT自然语言处理课程. 2026年课程要求，第七节。验收由课程方判定，本文不推定评分。](https://nlp.hltbit.top/2026/materials/w01/classroom/requirements.html)
- [[12] G14. 2026-11-21本机离线核验记录：命令、JUnit、资源SHA与四阶段审计随附sources/local-verification/。被测代码为main bdb11d3；链接指向代码提交，不冒充已推送的证据目录。](https://github.com/SPikerinbit/longllmlingua-reproduction/commit/bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4)

## 随附来源副本SHA-256

这些是资料副本校验和，不冒充缺失的阶段二/三/四完整输出缓存校验和。

- `sources/KNOWLEDGEWORK-SUGGESTIONS-20261121.md`  `b5619ec65ec5a16e02b25d27d688929562b0374f8fe58e862b4034a3c68cfc76`
- `sources/RUN-SUMMARY-20261121.md`  `ff4d39280f3d436d15297c10e8f3fb66e17c73ce87e3823616d28d40bcec076e`
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
- `sources/local-resource-readonly-check.json`  `c0fd40c55b505dda0e3c8375daa027712df0c269ef5e010b38316b73ca6134eb`
- `sources/local-verification/README.md`  `0b1e560e640986b9b72646cc8f9921a0d9718a18dd49d1a9c220c29163a176ff`
- `sources/local-verification/SHA256SUMS.txt`  `890c334a2f5dfa453bea7cc4bc2458e353d567da3892262eee60c069e2e0cd60`
- `sources/local-verification/audits/stage1/cases.md`  `df985056154d41d8f2e0dec34bd753b49b703908b5110cdb325b45b97badfbee`
- `sources/local-verification/audits/stage1/isolation-witness.json`  `cd298b2ff8fa011bf51b51047b8147efd6daa93601dbb25068c0524a4dc7cf84`
- `sources/local-verification/audits/stage1/offline-audit.json`  `abd0e9cb0d479dd859406924d503e7f7a722fe0c8089adf11e714954861573cb`
- `sources/local-verification/audits/stage1/smoke-labels.json`  `8398ac7cd5bf883330311111e41d002194e8dd1d500e6f066d043d0c250974b4`
- `sources/local-verification/audits/stage1/stderr.txt`  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `sources/local-verification/audits/stage1/stdout.txt`  `3b2adacc47263af7690abde561e092c9391337cfdd449cc1ef6c74e4c9ceadba`
- `sources/local-verification/audits/stage2/offline-audit.json`  `6024030a10a7e1c57bc062b6e0d7dbf9dab04944b46368b3d64180800e23a09c`
- `sources/local-verification/audits/stage3/offline-audit.json`  `255fa51b1d92db37dae59336e1eb9113490a4f077b83ea8a14fef2ecfab5c34e`
- `sources/local-verification/audits/stage4/offline-audit.json`  `a5037bf12b2b5b0190aca41767fbc4bf169daee81cb68ead0baede248820d669`
- `sources/local-verification/data-tokenizer-sha256.as-recorded.txt`  `d74051bb6107dc8a298dfb72326750adace3647be0a9299fd8ba6be3fc764fd6`
- `sources/local-verification/data-tokenizer-sha256.txt`  `2a81905a48d1f676f8c885cb96fb9257493424dc229445da3c19bad35399f445`
- `sources/local-verification/demo-rehearsal.stderr`  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `sources/local-verification/demo-rehearsal.stdout`  `69fed1ba7f40c1655086f5d7098d13a05471842fc878ae52163e9f71f2e79e4f`
- `sources/local-verification/environment.txt`  `b7e1b5064a89016fb13c5064e1e7a841903d0371b90dc4494a0428fa99ed3496`
- `sources/local-verification/figures/ablation.pdf`  `5da5668224808db957ff14075bb677df34ee536730144be035c1ce89cf4a3113`
- `sources/local-verification/figures/ablation.png`  `4c1b1735c2fcf903dad2f5610f95fb53c5c7a9377b704f0a767085826396896a`
- `sources/local-verification/figures/efficiency.pdf`  `df43ece8237b159d54cd89151cd37ea61434a8e7fb19559cb50b42c05ed96e8c`
- `sources/local-verification/figures/efficiency.png`  `aa200cbc099281df93a1023c5720cf0c8a4c52d7a303e225d161a8348e309d4d`
- `sources/local-verification/figures/positions.pdf`  `d90fd7f55b907e336126df92a17cf223f93615cf7bc8c19c112379609e3181d4`
- `sources/local-verification/figures/positions.png`  `97078c82edc2b18fc7e4029263f1f6fd8bafd3b74dbe71a94cb275f9a4800060`
- `sources/local-verification/full-pytest.command.as-run.txt`  `b20dbe863af1b5bbf846edc2d02416d8887c704da2c2b2fc0a3d1194dd7a2845`
- `sources/local-verification/full-pytest.command.relative.txt`  `8a7b0e00878548d280b066758d4cd7ded70adc842d5b78f9bc2284e604aa83ba`
- `sources/local-verification/junit-baseline.xml`  `cdb282689cc3d2758e99e8a5da875df87a1fa4f7fb9d658cf706b59b476a38b0`
- `sources/local-verification/junit-full.xml`  `26d3340efcd8754d9615fe4e6801b4a4ce31ce485f4f14d7ad2f6e57123a5180`
- `sources/local-verification/pip-freeze-post.txt`  `5382f1cec3ff1ae8fb412db98ef6a70b781079825d9b31fb3b8b3e2d413b3cc4`
- `sources/local-verification/pip-freeze-pre.txt`  `00bd7757511e1b04d42ba0f3eb947b8069472adbc8a898c20109242d4d047ce0`
- `sources/local-verification/plan/smoke-plan.published.json`  `3252de327d83dd0fd6aa641a05246c5a9a1e28c33c96bbc437940f249fb3dcae`
- `sources/local-verification/plan/smoke-plan.rerun.json`  `b67fcdbaaef2879fa5595bf57075fe69fb2468772efa689d1eb9a78ea0a0f892`
- `sources/local-verification/plan/stderr.txt`  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `sources/local-verification/plan/stdout.txt`  `b67fcdbaaef2879fa5595bf57075fe69fb2468772efa689d1eb9a78ea0a0f892`
- `sources/local-verification/prepare.stderr`  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `sources/local-verification/prepare.stdout`  `a9eacca720d23c8132196a21efa7e096a4c4a845de5e352218d2e2214d025318`
- `sources/local-verification/pytest-baseline.stderr`  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `sources/local-verification/pytest-baseline.stdout`  `fa80da536c080d94828e587dca83f5c5dbd5ceff5e5aaad787f62ac95fe2fbd4`
- `sources/local-verification/pytest-collect.txt`  `fdd8369facb1081b62ad418edb381fdab03f16b0dddd304626ef166d578154d0`
- `sources/local-verification/pytest-full.stderr`  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `sources/local-verification/pytest-full.stdout`  `28b60c6a168a8993128a6bc81adfe79cb8544715d8856b218fd02ac67552a954`
- `sources/local-verification/recheck.sh`  `e10642266f9011fe67bf86981c723936332620f217704d11d4b64b1e1fb9527c`
- `sources/local-verification/stage4-rebuild/RESULTS.md`  `7819b7ec7434d4459398a7d5beae8b73642e6ce00cb1d5fd985b50e4b2f68c0c`
- `sources/local-verification/stage4-rebuild/ablation-statistics.json`  `37f8951f647cf355405050e48efafb7ec0624322c110b620f5f03bc31dddea63`
- `sources/local-verification/stage4-rebuild/ablation.csv`  `5b15dcb2de6378bb6933cff11b3c8f8e7c3daca29469f9d6abb56e3d1161430d`
- `sources/local-verification/stage4-rebuild/coverage.json`  `d361c2795af955238012c7f087cf07b658ad3fcb9879ddc8da3f2d7fed905ed9`
- `sources/local-verification/stage4-rebuild/efficiency.csv`  `356db59ae9d0c8e112a74503d22bcb1e97023011feceefa2205142989c49009c`
- `sources/local-verification/stage4-rebuild/efficiency.json`  `4096d7bbc21c2b7dab161e6218369d916827f6dca9c42ef22bba1756e92aeb44`
- `sources/local-verification/stage4-rebuild/stderr.txt`  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `sources/local-verification/stage4-rebuild/stdout.txt`  `8e9b90a2759e2dbcc46982d39a9968f7d1434c267447afdd0614552c350d51d0`
- `sources/local-verification/stage4-rebuild/usage.json`  `e5803c538ef8236e9c2ab57fe94c7a7b5d46deb226dbd57b705fb194610c8ef6`
- `sources/local-verification/timeline.txt`  `990a2eaf194e0c1db3a703b43ea63c64af9272690d2a1f9a28a8264bb0c9b76e`
- `sources/paper/LongLLMLingua.pdf`  `a81090e2589fcef37f310ee2a265076e4560a296a59864c9d43a6e9b62fe3997`
- `sources/report-draft.md`  `d773e490aa6d0a2854098eacdd6d0dd53456e6a1828f828643ca7a20a5b0e9c8`
- `sources/report-repo-source-20261121.md`  `f1de4c2fad67490f22d49d95fd0608c1ff46f6bca65d32447493ab0c10df626e`
- `sources/report-source-updated.md`  `3d7ef940c1bc5201c0325ab79656cb00da369b2b254a92d4ecce2a1ac3312939`
- `sources/stage1-cases.md`  `df985056154d41d8f2e0dec34bd753b49b703908b5110cdb325b45b97badfbee`
- `sources/stage2-acceptance-remote.json`  `f60582980375114a606c87a6f3b2c8f6f484c44e0880b289e295312f4d28a77f`
- `sources/stage3-stats-remote.json`  `d8e110232901480083806003e648d7b8fa278cdce3d24ade7d77c167e2275aae`
- `sources/stage4-ablation-remote.csv`  `d23b63dc6450bf6eecf4e00caa504f3a50ca19ce9516dee98dfc82fa9d6612d0`

## 核心视频及配套素材SHA-256（课程包相对路径）

- `evidence/EDIT-MAP.md`  `b686af47c6b966a96dbab80dd48521b12a6a104d0746771db3e15f8bab910192`  4416 bytes
- `evidence/core-evidence-60s.mp4`  `e3be31222267724b62bc9b9d1e0c4c8026902acde62edac488f342a6e7dbee8e`  11550287 bytes
- `evidence/core-evidence-60s.srt`  `c5032092117b79f7e90428af2b7e5f5e10a89923410042f8004e22be770a51b7`  1246 bytes
- `evidence/poster.png`  `f0dcb9d32a98ee4822c44712450664f993b59d8a1553ddea65b8f5c86447b5a8`  419251 bytes
- `evidence/voice/NARRATION.md`  `4776b7f27b57316e7aaf8a83d88e7fd7a6d4cc9d01cc49e7f8a5ea500788e085`  1076 bytes
- 录屏元数据、复核来源和范围：`qa/recording-verification.json`。未声称真人口播计时/成员确认已完成。
