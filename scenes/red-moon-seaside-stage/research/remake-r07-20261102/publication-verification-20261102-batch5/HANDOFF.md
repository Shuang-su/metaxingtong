# Nov2 红月旧场重制发布归档 HANDOFF

远端独立 payload 字节核验完成于 2026-11-02T04:32:11.099317+00:00。本回执以实际当前时间正常Git提交，不回填原制作日期。

**254普通原件和2归档说明已正常Git发布并逐字节回读一致；8条阶段评论已发布；[Draft PR #99](https://github.com/Shuang-su/metaxingtong/pull/99) 已单独创建成功，open/draft/未合并。** 这是旧红月洞屏海景场重新制作，新场景计数0；不是旧R10/R11原件取回。source FAILED，用户未验收。

## 输入与普通原件

|冻结Library身份/版本|bundle|字节|SHA256|
|---|---|---:|---|
|`libfile_3139fcba10f08191bd92b502b3c491da` / 4|red-moon-remake-R07-final.bundle|152040597|`1ff541fad70d1455006b5a10b8a1afb10f66eea8d66c2652219fc0c72f2768a3`|

通过当前Library正式流程在本消费执行器实际物化，大小/SHA256/bundle verify/fsck一致。152040597字节bundle仅运输，不上传容器、ZIP、分片或LFS；最大普通历史blob11945865字节，低于100MiB。未读取此前已trash输入。

254输入原件共225471618字节；加2归档说明后256 payload路径共226209503字节。本机器回执与HANDOFF另计2文件，最终本批258新增路径。

普通原件固定payload commit：[a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff](https://github.com/Shuang-su/metaxingtong/commit/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff)；[254原件目录](https://github.com/Shuang-su/metaxingtong/tree/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files)；[逐文件大小/SHA256/Git blob与全部阶段映射](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/provenance.json)。归档分支 `archive/redmoon-remake-r07-20261102` 以真实main `6ad31e4b2fe8398060c33de20fc09f5edad427a7` 为祖先；本回执将新增一个真实metadata commit，最终head与固定payload不同，不冒充新模型阶段。

## 实际远端回读

从此前不存在的新空bare仓开始，检查初始对象库为空、无alternates。通过GitHub官方HTTPS正常Git fetch完整原history，再正常fetch真实upstream归档refs；对全部本批文件和阶段实际git show读取字节。没有本地clone、复制或共享对象库。

256最终payload路径、12原始commit和320全部可达原commit/tree/blob、12个归档阶段快照逐项大小/SHA256/Git blob或对象身份一致；failed_files=0，fsck通过，main未改、旧路径未变。无关继承main的promisor blob不在全量下载断言范围。原delivery-manifest的253行（不含自身）均一致；15正式图及sidecar绑定当前BLEND SHA、6组source/render/overlay哈希均核对。

[机器回执](remote_verification.json) 含完整逐项expected/remote_actual、原对象、阶段快照、fetch日志、输入身份、120图片位置、APIHTML核验和单独PR创建结果。未重新运行模型或原独立技术验证。此后回执两文件自身另行正常push并远端读回；本文件不提前宣称该后续动作已完成，最终交接另报真实结果。

## CURRENT 原件与报告

旧红月洞屏海景场Nov2重新制作，非新scene、非旧R10/R11原件找回。CURRENT R07有限后半场；3新原生源时间/尺寸独立，P1实际1080、P2真4K，三源全训练，source FAILED且后续独立回放缺。R06扩有限工作地坪、R07正确evaluated导出纸伞Solidify厚度；436对象与6.85e-7回导/15正式图/6原尺寸direct50技术记录不等于完整工程或来源验收。台瓣、白框、屏层、伞姿态仍不符，近框地下矩形和地面相切为推断，柱帽-band仅部分交叠。失败、中断和误锚保留。

- [models/R07_material.blend](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/models/R07_material.blend)。
- [models/R07_white.blend](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/models/R07_white.blend)。
- [models/R07_material.glb](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/models/R07_material.glb)。
- [models/R07_white.glb](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/models/R07_white.glb)。
- [models/R07-artifacts.json](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/models/R07-artifacts.json)。
- [docs/R07-final-delivery.md](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/docs/R07-final-delivery.md)。
- [docs/SOURCE-VALIDATION-FAILED.md](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/docs/SOURCE-VALIDATION-FAILED.md)。
- [qa/independent-R07/FINAL-R07-independent-review.md](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/qa/independent-R07/FINAL-R07-independent-review.md)。
- [renders/final-R07/R07_MAIN_material.png](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/renders/final-R07/R07_MAIN_material.png)。
- [renders/final-R07/native-comparison-manifest.json](https://github.com/Shuang-su/metaxingtong/blob/a5ebd6e5f2f869a1b405fe2dea58aa4e3d380eff/scenes/red-moon-seaside-stage/research/remake-r07-20261102/files/renders/final-R07/native-comparison-manifest.json)。

## Issue89 逐阶段记录

保留旧R10/R11记录和Nov1丢失声明；新重制按真实语义阶段首次记录，QA并入所属版本，不改写旧成果。

- 红月重制 R00：3张新原生来源与旧原件缺口：[comment 6569130177](https://github.com/Shuang-su/metaxingtong/issues/89#issuecomment-6569130177)。
- 红月 R01：首可编辑共享舞台、相对深度与初始失败：[comment 6569131477](https://github.com/Shuang-su/metaxingtong/issues/89#issuecomment-6569131477)。
- 红月 R02：条件三相机拟合、误锚与拓扑失败：[comment 6569132594](https://github.com/Shuang-su/metaxingtong/issues/89#issuecomment-6569132594)。
- 红月 R03：补两前凹屏边界与推定伞接地：[comment 6569133501](https://github.com/Shuang-su/metaxingtong/issues/89#issuecomment-6569133501)。
- 红月 R04：显式工作相机距离与共享台瓣条件轮廓：[comment 6569134940](https://github.com/Shuang-su/metaxingtong/issues/89#issuecomment-6569134940)。
- 红月 R05：有限白近框修正、画外工作闭口与明确失败：[comment 6569136244](https://github.com/Shuang-su/metaxingtong/issues/89#issuecomment-6569136244)。
- 红月 R06：仅扩有限工作地坪，导出漏层尚未修复：[comment 6569166838](https://github.com/Shuang-su/metaxingtong/issues/89#issuecomment-6569166838)。
- 红月 CURRENT R07：evaluated导出修复与完整技术套件，来源FAILED：[comment 6569168047](https://github.com/Shuang-su/metaxingtong/issues/89#issuecomment-6569168047)。

## 原始提交与当前归档映射

原history分支 `history/redmoon-remake-original-20261102` → `49ddb25bb362420b92e93b3993a1ef61abdc70d2`。保留原commit对象、作者/提交者身份、真实时间和父链；新归档提交使用当前真实时间，不伪造原历史。

|原提交|原提交时间|upstream归档提交|
|---|---|---|
|[2ada1dfd56b0bda0a124cd31c19d34b8b77f066b](https://github.com/Shuang-su/metaxingtong/commit/2ada1dfd56b0bda0a124cd31c19d34b8b77f066b)|2026-11-02T12:42:54+09:00|[56ec0021050caa7d0a36f61005081c7b53788f32](https://github.com/Shuang-su/metaxingtong/commit/56ec0021050caa7d0a36f61005081c7b53788f32)|
|[532f96d46e17a3128af2a301a8888a0eed8f34fe](https://github.com/Shuang-su/metaxingtong/commit/532f96d46e17a3128af2a301a8888a0eed8f34fe)|2026-11-02T12:49:06+09:00|[8cdedd8b2c48a2f5d992051546daa782779e5f8a](https://github.com/Shuang-su/metaxingtong/commit/8cdedd8b2c48a2f5d992051546daa782779e5f8a)|
|[dd8cf6c9d306e20f494db540319a78c92df44b2f](https://github.com/Shuang-su/metaxingtong/commit/dd8cf6c9d306e20f494db540319a78c92df44b2f)|2026-11-02T12:49:47+09:00|[85ebefc81869b54d0c5a95c729caf8c8b0f964a4](https://github.com/Shuang-su/metaxingtong/commit/85ebefc81869b54d0c5a95c729caf8c8b0f964a4)|
|[5418f46fe5d5606d95146fda8a552b6957607476](https://github.com/Shuang-su/metaxingtong/commit/5418f46fe5d5606d95146fda8a552b6957607476)|2026-11-02T12:50:56+09:00|[8bfaed666c49e275c4eb536d2985c794fefca681](https://github.com/Shuang-su/metaxingtong/commit/8bfaed666c49e275c4eb536d2985c794fefca681)|
|[9bd9b42f9d6cde99065458ef716661be5dfb681f](https://github.com/Shuang-su/metaxingtong/commit/9bd9b42f9d6cde99065458ef716661be5dfb681f)|2026-11-02T12:57:17+09:00|[77d25a068df96ae31056af5db8871fd0467fbe36](https://github.com/Shuang-su/metaxingtong/commit/77d25a068df96ae31056af5db8871fd0467fbe36)|
|[57d5961baf0b1bbd45ca51b47a0a2e25548fcfd1](https://github.com/Shuang-su/metaxingtong/commit/57d5961baf0b1bbd45ca51b47a0a2e25548fcfd1)|2026-11-02T13:01:04+09:00|[d207553f302d0e7c5d735de74cf0655b9389a394](https://github.com/Shuang-su/metaxingtong/commit/d207553f302d0e7c5d735de74cf0655b9389a394)|
|[ac49ec3ddf8d9d5a2b0cf6be7c849752692eb316](https://github.com/Shuang-su/metaxingtong/commit/ac49ec3ddf8d9d5a2b0cf6be7c849752692eb316)|2026-11-02T13:03:36+09:00|[ee5d20288a196c81ada1aedb8ca5d14f8679667c](https://github.com/Shuang-su/metaxingtong/commit/ee5d20288a196c81ada1aedb8ca5d14f8679667c)|
|[f03fbf08f1450518c6b2c8c284cf477674797fd1](https://github.com/Shuang-su/metaxingtong/commit/f03fbf08f1450518c6b2c8c284cf477674797fd1)|2026-11-02T13:06:11+09:00|[859e30fe92dce40851f46ef3899e02745981410c](https://github.com/Shuang-su/metaxingtong/commit/859e30fe92dce40851f46ef3899e02745981410c)|
|[edf8acf75fa935588bdd735ab50f4ef61c532cef](https://github.com/Shuang-su/metaxingtong/commit/edf8acf75fa935588bdd735ab50f4ef61c532cef)|2026-11-02T13:09:53+09:00|[4bdbf1d784918a35853a8e81a17b83c274d13625](https://github.com/Shuang-su/metaxingtong/commit/4bdbf1d784918a35853a8e81a17b83c274d13625)|
|[f042678ba52a2b2797b795372c10551a858b722e](https://github.com/Shuang-su/metaxingtong/commit/f042678ba52a2b2797b795372c10551a858b722e)|2026-11-02T13:10:52+09:00|[ff170ec7c66f469f45ff459452a1ec68224f11be](https://github.com/Shuang-su/metaxingtong/commit/ff170ec7c66f469f45ff459452a1ec68224f11be)|
|[979eda37e6dde81778e42365f1dd6d07314d9c09](https://github.com/Shuang-su/metaxingtong/commit/979eda37e6dde81778e42365f1dd6d07314d9c09)|2026-11-02T13:22:18+09:00|[f7324016d5bfac059e1d79b1863ae6f00938c2a5](https://github.com/Shuang-su/metaxingtong/commit/f7324016d5bfac059e1d79b1863ae6f00938c2a5)|
|[49ddb25bb362420b92e93b3993a1ef61abdc70d2](https://github.com/Shuang-su/metaxingtong/commit/49ddb25bb362420b92e93b3993a1ef61abdc70d2)|2026-11-02T13:23:49+09:00|[ce8867e8747f1748a97e7aa284377b1bee611729](https://github.com/Shuang-su/metaxingtong/commit/ce8867e8747f1748a97e7aa284377b1bee611729)|

## 来源与技术结论边界

- 三新原生源为BV1DZ4y1U71V P1 t45.013436与15.116586实际1920×1080、P2 t32.024562实际3840×2160。P1本次4K菜单尝试未稳定，不能冒称4K或沿用旧时间/哈希。3源全训练，后续独立回放缺。三份真实相对逆深度原grid924×518，源尺寸显示为派生，不是原生4K深度或度量。
- R02 LB/RI遮挡或实体误配使锚点无效，近共面相机触界不是标定；R04明确y约−9工作先验。R05近框朝向和推定前闭口只限定有限工作边界，不是观察到前厅。R03前屏重复顶点修复和所有失败/中断记录保留。
- R05地坪1057样本107漏覆盖经R06工作地坪扩展后为0；R07修GLB遗漏纸伞Solidify背层，原独立review记436对象/世界顶点双向max6.85e-7/三角连接一致。内存normal-seam去重仅QA，叶片有意开放，不证明所有几何或数学全水密。材白同evaluated几何。
- 两柱帽-band仅部分交叠：225采样92重叠、133未中，不是全接触或承载证明。地下完整矩形近框及伞rim工程地面相切均为推断，不是来源观察/真实接地。
- R07冻结15正式图（3源材白6+主图1+检查8），6原尺寸direct50在原独立报告中全像素0差。发布端只核实际字节、哈希和当前模型绑定，没有重跑Blender、生成脚本、深度推理或叠图算术。
- 台瓣曲线/白框/屏层遮挡/伞姿态等仍明显不符，所有来源对齐FAILED；没有全仓规范通过、整场工程验收或用户接受结论。

## 发布与剩余事项

- 红月新目标Draft PR99单独创建一次成功，完整非秘密结果在机器回执；工具未提供运行时调用ID，不虚构。此前音游厅/营地/摩天轮3个被拒PR创建保持暂停，未重试、代建、换工具/执行器或改权限认证。
- 120远端图片原字节可解码，8评论正文、PR链接和120个APIHTML图片属性一致；网页实际视口显示0/120。已知GitHub浏览器证书错误路线未重试或绕过，解码/APIHTML不冒充网页实显。
- Draft保持未合并/未批准，main不变。最终精确head status/check-run/workflow另读；0检查不是CI通过。
- Space本项临备保持冻结未删，未另传模型/预览；由母任务独立核验后决定可恢复清理。
