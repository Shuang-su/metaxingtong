# 2026-11-02 第四批旧场重制发布归档 HANDOFF

独立远端 payload 字节核验完成于 2026-11-02T04:15:46.333529+00:00。本回执随后以真实当前时间正常Git提交，不回填旧制作时间。

## 实际完成与尚未完成

**657普通原件和6归档说明已正常Git推送并远端逐字节核验；17条版本评论已发布。三个Draft PR未建立。** 三场均为旧场重制，不计新scene，不是原R07–R10/R08/R08b文件或Git对象找回，来源仍FAIL、用户未验收。

原PR创建批次被中断：父线程报告连续3次自动审批拒绝，当前可见外层仅为 `aborted by user after 16.1s`，没有逐项理由/调用ID，不能把外层字符串解释为用户主动取消或虚构缺少哪项权限。被拒PR创建没有重试，没有浏览器代建、认证/权限更改或执行器替换。对三个精确head作all-state查询均无PR。普通Git和此前未尝试的Issue评论是独立已授权步骤，实际继续完成。

## 正式输入

|Library身份/冻结版本|bundle|字节|SHA256|
|---|---|---:|---|
|`libfile_10d3e0c1c9c0819199fec60b0cd36164` / 5|arcade-remake-final-0f3ff79-20261102.bundle|115027687|`bacaa50874dc8f0b365551bd8a98728f4b6ba030128699631c08947f811b8c76`|
|`libfile_016d1cf1e61c8191bb0b68ad9486cf88` / 3|camp-remake-C06-verified-20261102.bundle|152870485|`76ae58b2ed5cde03a0b84027fd65aece280066fab680b48b8717bfa02df8e999`|
|`libfile_41b3a37b4f488191bedba6a4def1d962` / 2|ferris-remake-R05-final-20261102.bundle|155941575|`7538f9c0823fb80e85f38991210b017d316c08a99dba9a44dd6df52b8ac80066`|

三项均在本消费执行器通过当前Library正式流程物化，身份/版本、大小/SHA256、bundle verify/fsck匹配。未消费此前已trash输入或未交付红月资料。三个bundle均>100MB，仅作运输，没有上传bundle本体、ZIP、分片或LFS。最大普通历史blob为10,001,620字节。

657原件总594,055,842字节；加6说明后payload 663文件、595896386字节。回执和HANDOFF两文件另计，本批665新增最终路径。

从不存在的新空bare仓开始，确认初始object store为空且无alternates；通过GitHub官方HTTPS正常fetch三个完整原history，再fetch真实upstream归档分支。未本地clone、复制或共享对象库。663最终路径实际取回大小/SHA256/Git blob全相等，28阶段快照、28原始commit和全部844独立可达原commit/tree/blob逐字节相等。失败数0、fsck通过；无关main继承promisor blobs不在全量下载断言范围。

[机器回执](remote_verification.json) 保存完整每项expected/remote_actual、原对象、阶段快照、实际fetch日志、图片位置及PR中断事实。沿用第一次启动fetch至完成，没有启动重复空仓冒充验证。

## 固定原件与已发Issue记录

|范围|普通原件payload commit|文件数|Issue / PR状态|
|---|---|---:|---|
|arcade|[0c04106befa187ecd93df089fc9cc78a4db48616](https://github.com/Shuang-su/metaxingtong/commit/0c04106befa187ecd93df089fc9cc78a4db48616)|196|[Issue 85](https://github.com/Shuang-su/metaxingtong/issues/85)；PR未建立|
|camp|[a29113af80eb2902368562455823b1a7b1713f30](https://github.com/Shuang-su/metaxingtong/commit/a29113af80eb2902368562455823b1a7b1713f30)|254|[Issue 87](https://github.com/Shuang-su/metaxingtong/issues/87)；PR未建立|
|ferris|[9ee35d1d83b3ff9151ed64821d09ff4cfe6de901](https://github.com/Shuang-su/metaxingtong/commit/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901)|207|[Issue 86](https://github.com/Shuang-su/metaxingtong/issues/86)；PR未建立|

全部归档分支以真实 main `6ad31e4b2fe8398060c33de20fc09f5edad427a7` 为祖先。当前回执在arcade payload之后新增真实metadata commit，最终arcade head与表中固定payload不同；不冒充新模型阶段。main未改，未合并/批准；此前路径和旧丢失/失败记录保留。

## CURRENT与原件/报告链接

### arcade

旧音游厅重新制作，非新scene，原R07–R10未找回。CURRENT R03只M01局部source-lit海报/新UV，未知保持灰、无inpaint；共享1134mesh和R02整场图准确继承，R03只8局部回归。R00/R01/R02失败保留。新高码率三原生帧时间独立，不冒旧帧；camera-only三焦距初始化诊断FAILED、坏pose不晋升CURRENT。来源FAIL、后续独立回放缺。

[196普通原件目录](https://github.com/Shuang-su/metaxingtong/tree/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/files) · [精确身份及全阶段映射](https://github.com/Shuang-su/metaxingtong/blob/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/provenance.json)

- [models/arcade_remake_R03_material.blend](https://github.com/Shuang-su/metaxingtong/blob/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/files/models/arcade_remake_R03_material.blend)。
- [models/arcade_remake_R03_white.blend](https://github.com/Shuang-su/metaxingtong/blob/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/files/models/arcade_remake_R03_white.blend)。
- [models/arcade_remake_R03_material.glb](https://github.com/Shuang-su/metaxingtong/blob/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/files/models/arcade_remake_R03_material.glb)。
- [models/arcade_remake_R03_white.glb](https://github.com/Shuang-su/metaxingtong/blob/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/files/models/arcade_remake_R03_white.glb)。
- [qa/R03/R03_RENDER_REVIEW.md](https://github.com/Shuang-su/metaxingtong/blob/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/files/qa/R03/R03_RENDER_REVIEW.md)。
- [qa/R02_FINAL_REVIEW.md](https://github.com/Shuang-su/metaxingtong/blob/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/files/qa/R02_FINAL_REVIEW.md)。
- [qa/camera-new-source/RESULT.md](https://github.com/Shuang-su/metaxingtong/blob/0c04106befa187ecd93df089fc9cc78a4db48616/scenes/arcade-dance-machine-room/research/remake-r03-20261102/files/qa/camera-new-source/RESULT.md)。

### camp

旧营地C01–C06真实新重制，非旧R08原件恢复、非新scene。CURRENT C06为两固定训练相机下卷毯局部候选，软端/纵向提带仍缺。147对象28232tri、GLB回导/10简单材质参数技术记录不等于来源通过。第三源早已看过，三焦距后箱与右檐仍FAIL；左檐/后顶/植被岩代理和后续回放缺口保留。最后纯QA提交新增5记录不改模型，6当前native50与扩20像素记录范围分开。

[254普通原件目录](https://github.com/Shuang-su/metaxingtong/tree/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/files) · [精确身份及全阶段映射](https://github.com/Shuang-su/metaxingtong/blob/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/provenance.json)

- [CURRENT.json](https://github.com/Shuang-su/metaxingtong/blob/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/files/CURRENT.json)。
- [models/C06_remade_materials.blend](https://github.com/Shuang-su/metaxingtong/blob/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/files/models/C06_remade_materials.blend)。
- [models/C06_remade_white.blend](https://github.com/Shuang-su/metaxingtong/blob/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/files/models/C06_remade_white.blend)。
- [models/C06_remade.glb](https://github.com/Shuang-su/metaxingtong/blob/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/files/models/C06_remade.glb)。
- [models/C06_actual_reimport.blend](https://github.com/Shuang-su/metaxingtong/blob/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/files/models/C06_actual_reimport.blend)。
- [C06_REVIEW.md](https://github.com/Shuang-su/metaxingtong/blob/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/files/C06_REVIEW.md)。
- [qa/final_verification/README.md](https://github.com/Shuang-su/metaxingtong/blob/a29113af80eb2902368562455823b1a7b1713f30/scenes/desert-tent-camp/research/remake-c06-20261102/files/qa/final_verification/README.md)。

### ferris

旧摩天轮舱真实重制，非原R08b找回、非新scene。CURRENT R04几何+R05仅front条件相机，其他3source/MAIN/10CHECK准确继承R04。R01漏洞、R02/R03绕序/装配错误及exit130失败保留；R04有限支脚顶/灯座推断连接修复。176mesh技术/有限射线不证明数学水密，.001亚网格圆角等未测。R05只门平面训练，留出窗174–193px仍FAIL，前门遮挡及其余来源未通过；灰外景未做。

[207普通原件目录](https://github.com/Shuang-su/metaxingtong/tree/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files) · [精确身份及全阶段映射](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/provenance.json)

- [scenes/ferris-wheel-cabin-remake/CURRENT.json](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/CURRENT.json)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_material.blend](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_material.blend)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_white.blend](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_white.blend)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_material.glb](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_material.glb)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_white.glb](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R04_white.glb)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_material.blend](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_material.blend)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_white.blend](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_white.blend)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_material.glb](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_material.glb)。
- [scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_white.glb](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/models/ferris_remake_R05_white.glb)。
- [scenes/ferris-wheel-cabin-remake/docs/remake-report.md](https://github.com/Shuang-su/metaxingtong/blob/9ee35d1d83b3ff9151ed64821d09ff4cfe6de901/scenes/ferris-wheel-cabin/research/remake-r05-20261102/files/scenes/ferris-wheel-cabin-remake/docs/remake-report.md)。

## 逐版本评论

真实模型/失败试验按语义版本组织，QA提交并入对应版本，不将每条QA都堆为独立评论。原Issue85/86/87损失声明及旧评论保留。

- 音游厅重制 R00：新可编辑起点与来源失败：[Issue 85 / comment 6568929064](https://github.com/Shuang-su/metaxingtong/issues/85#issuecomment-6568929064)。
- 音游厅 R01：四向箭头与低柜金印，环越界失败：[Issue 85 / comment 6568932315](https://github.com/Shuang-su/metaxingtong/issues/85#issuecomment-6568932315)。
- 音游厅 R02：裁切下环、整场套件和3张新原生高码率源：[Issue 85 / comment 6568933505](https://github.com/Shuang-su/metaxingtong/issues/85#issuecomment-6568933505)。
- 音游厅 CURRENT R03：单柜条件海报，准确继承R02整场图：[Issue 85 / comment 6568934455](https://github.com/Shuang-su/metaxingtong/issues/85#issuecomment-6568934455)。
- 音游厅新源 camera-only 条件诊断：明确拒绝，不晋升CURRENT：[Issue 85 / comment 6568936179](https://github.com/Shuang-su/metaxingtong/issues/85#issuecomment-6568936179)。
- 营地重制 C01：新基础原件，旧历史缺口保持：[Issue 87 / comment 6568937327](https://github.com/Shuang-su/metaxingtong/issues/87#issuecomment-6568937327)。
- 营地 C02：箱姿态、脚接触和重复端点修正：[Issue 87 / comment 6568938275](https://github.com/Shuang-su/metaxingtong/issues/87#issuecomment-6568938275)。
- 营地 C03：右檐两源条件改善，第三图失败：[Issue 87 / comment 6568939683](https://github.com/Shuang-su/metaxingtong/issues/87#issuecomment-6568939683)。
- 营地 C04：有限户外代理与真实相对深度：[Issue 87 / comment 6568940668](https://github.com/Shuang-su/metaxingtong/issues/87#issuecomment-6568940668)。
- 营地 C05：完整候选套件冻结，来源仍FAIL：[Issue 87 / comment 6568943523](https://github.com/Shuang-su/metaxingtong/issues/87#issuecomment-6568943523)。
- 营地 CURRENT C06：卷毯有限改善与纯QA冻结：[Issue 87 / comment 6568944452](https://github.com/Shuang-su/metaxingtong/issues/87#issuecomment-6568944452)。
- 摩天轮舱重制 R00：真实来源恢复与独立新历史：[Issue 86 / comment 6568945381](https://github.com/Shuang-su/metaxingtong/issues/86#issuecomment-6568945381)。
- 摩天轮舱 R01：共享有限内舱与10处拼接漏：[Issue 86 / comment 6568946646](https://github.com/Shuang-su/metaxingtong/issues/86#issuecomment-6568946646)。
- 摩天轮舱 R02：实体补角，反绕序与中断保留：[Issue 86 / comment 6568947991](https://github.com/Shuang-su/metaxingtong/issues/86#issuecomment-6568947991)。
- 摩天轮舱 R03：158面组绕序修正，支承顶隙失败：[Issue 86 / comment 6568948966](https://github.com/Shuang-su/metaxingtong/issues/86#issuecomment-6568948966)。
- 摩天轮舱 R04：支脚顶/灯座有限修复与四源套件：[Issue 86 / comment 6568949966](https://github.com/Shuang-su/metaxingtong/issues/86#issuecomment-6568949966)。
- 摩天轮舱 CURRENT R05：仅front条件相机，其余准确继承R04：[Issue 86 / comment 6568951151](https://github.com/Shuang-su/metaxingtong/issues/86#issuecomment-6568951151)。

## 原始提交与当前归档映射

### arcade

`history/arcade-remake-original-20261102` → `0f3ff79c2f7388f148ce9f87810a28d26439b874`；原对象/作者日期/提交者日期/父链完整保留，新upstream归档使用实际新时间。

|原提交|原提交时间|当前归档提交|
|---|---|---|
|[e8b466c9790c442342b1961110d6e36e0c1852f0](https://github.com/Shuang-su/metaxingtong/commit/e8b466c9790c442342b1961110d6e36e0c1852f0)|2026-11-02T12:06:32+09:00|[d6c981974a74fab64be6e02d30d91701d66e6003](https://github.com/Shuang-su/metaxingtong/commit/d6c981974a74fab64be6e02d30d91701d66e6003)|
|[a681671fdc78bc268cfd92281f0bace379057dd0](https://github.com/Shuang-su/metaxingtong/commit/a681671fdc78bc268cfd92281f0bace379057dd0)|2026-11-02T12:06:54+09:00|[9bdc5d5c43ce3af6aa752cc1e7ed77614470e020](https://github.com/Shuang-su/metaxingtong/commit/9bdc5d5c43ce3af6aa752cc1e7ed77614470e020)|
|[180690364f59fb9ddcf40e1e69034fb1f6060a3c](https://github.com/Shuang-su/metaxingtong/commit/180690364f59fb9ddcf40e1e69034fb1f6060a3c)|2026-11-02T12:15:03+09:00|[0ab8ce9af0e4944ba7003c3da36eec086dbc9c31](https://github.com/Shuang-su/metaxingtong/commit/0ab8ce9af0e4944ba7003c3da36eec086dbc9c31)|
|[9c7a4b61352cb466173952e83889cf84d8ba4314](https://github.com/Shuang-su/metaxingtong/commit/9c7a4b61352cb466173952e83889cf84d8ba4314)|2026-11-02T12:16:28+09:00|[c9a14021ed5e656f71f6ab4cf026657daac5c3d1](https://github.com/Shuang-su/metaxingtong/commit/c9a14021ed5e656f71f6ab4cf026657daac5c3d1)|
|[588f27afe1008e6f592780ecf317d8aa8d948468](https://github.com/Shuang-su/metaxingtong/commit/588f27afe1008e6f592780ecf317d8aa8d948468)|2026-11-02T12:19:23+09:00|[6d3601200c7499cc390be389929dd22fcedcb713](https://github.com/Shuang-su/metaxingtong/commit/6d3601200c7499cc390be389929dd22fcedcb713)|
|[4e5a4d1aeef92b0076be1a54d2de0462d78f4659](https://github.com/Shuang-su/metaxingtong/commit/4e5a4d1aeef92b0076be1a54d2de0462d78f4659)|2026-11-02T12:29:19+09:00|[76e8c95fd09786b6bd478ed84179b6204f71850e](https://github.com/Shuang-su/metaxingtong/commit/76e8c95fd09786b6bd478ed84179b6204f71850e)|
|[ff169f7e070e98a44bf6c971e898d41e4b0c33f7](https://github.com/Shuang-su/metaxingtong/commit/ff169f7e070e98a44bf6c971e898d41e4b0c33f7)|2026-11-02T12:36:29+09:00|[56bf014a1ad8460578287ef27adbf681f92f0026](https://github.com/Shuang-su/metaxingtong/commit/56bf014a1ad8460578287ef27adbf681f92f0026)|
|[cabaf79582bf92e5939a4745ec7ba72911be11ff](https://github.com/Shuang-su/metaxingtong/commit/cabaf79582bf92e5939a4745ec7ba72911be11ff)|2026-11-02T12:42:28+09:00|[8ba263dd8d365d2d13434429cfb89c4a59c3d092](https://github.com/Shuang-su/metaxingtong/commit/8ba263dd8d365d2d13434429cfb89c4a59c3d092)|
|[4103d72a857a02ece928a098d024c46e7d1cebdd](https://github.com/Shuang-su/metaxingtong/commit/4103d72a857a02ece928a098d024c46e7d1cebdd)|2026-11-02T12:50:31+09:00|[dfc9e66965cc078757fd881c297de46d301ba8bf](https://github.com/Shuang-su/metaxingtong/commit/dfc9e66965cc078757fd881c297de46d301ba8bf)|
|[a614a54611407629874e72bdb3a9d874644e7cfa](https://github.com/Shuang-su/metaxingtong/commit/a614a54611407629874e72bdb3a9d874644e7cfa)|2026-11-02T12:55:22+09:00|[0023b07ed527e7460068b3ff95dcac2c5c7d6d67](https://github.com/Shuang-su/metaxingtong/commit/0023b07ed527e7460068b3ff95dcac2c5c7d6d67)|
|[a5596234ba0cd9b41ea2403a8ca741907efacb3b](https://github.com/Shuang-su/metaxingtong/commit/a5596234ba0cd9b41ea2403a8ca741907efacb3b)|2026-11-02T12:58:19+09:00|[01a3d15c31f308014811a8f04013f0cc35fbb46c](https://github.com/Shuang-su/metaxingtong/commit/01a3d15c31f308014811a8f04013f0cc35fbb46c)|
|[0f3ff79c2f7388f148ce9f87810a28d26439b874](https://github.com/Shuang-su/metaxingtong/commit/0f3ff79c2f7388f148ce9f87810a28d26439b874)|2026-11-02T13:00:38+09:00|[f6503d871a908ec68f0aa28fd7836c8198028d60](https://github.com/Shuang-su/metaxingtong/commit/f6503d871a908ec68f0aa28fd7836c8198028d60)|

### camp

`history/camp-remake-original-20261102` → `8f2f66e0877dd72494077d3d8ee70730a95254eb`；原对象/作者日期/提交者日期/父链完整保留，新upstream归档使用实际新时间。

|原提交|原提交时间|当前归档提交|
|---|---|---|
|[9af4716b553e3c90dbbe3176354296f637d429f6](https://github.com/Shuang-su/metaxingtong/commit/9af4716b553e3c90dbbe3176354296f637d429f6)|2026-11-02T12:05:04+09:00|[a3ee7b7ba888776da2f09a759570bf9286e83f71](https://github.com/Shuang-su/metaxingtong/commit/a3ee7b7ba888776da2f09a759570bf9286e83f71)|
|[fbfb6f0f300a2e5f5e9916e61db3c8b57b624b16](https://github.com/Shuang-su/metaxingtong/commit/fbfb6f0f300a2e5f5e9916e61db3c8b57b624b16)|2026-11-02T12:11:00+09:00|[80dbfd958f7b04decd7a2059ac76e8bec03c51b0](https://github.com/Shuang-su/metaxingtong/commit/80dbfd958f7b04decd7a2059ac76e8bec03c51b0)|
|[f667c1d50f7e8cf945342c8a7e13aa02f1b6cd09](https://github.com/Shuang-su/metaxingtong/commit/f667c1d50f7e8cf945342c8a7e13aa02f1b6cd09)|2026-11-02T12:19:50+09:00|[8de116812af5028439f49000c03ed25190e2f836](https://github.com/Shuang-su/metaxingtong/commit/8de116812af5028439f49000c03ed25190e2f836)|
|[426f0258de859251de3de081a1d3a8f43379c4c1](https://github.com/Shuang-su/metaxingtong/commit/426f0258de859251de3de081a1d3a8f43379c4c1)|2026-11-02T12:19:51+09:00|[2459576a4f6e9acd25a168f60962e7076de90b46](https://github.com/Shuang-su/metaxingtong/commit/2459576a4f6e9acd25a168f60962e7076de90b46)|
|[6589cbbc391f1a4aba04bc570df87a82751d3ab8](https://github.com/Shuang-su/metaxingtong/commit/6589cbbc391f1a4aba04bc570df87a82751d3ab8)|2026-11-02T12:28:09+09:00|[2323476940ae1f39d144fd69f6ed23f8f2ec6a1c](https://github.com/Shuang-su/metaxingtong/commit/2323476940ae1f39d144fd69f6ed23f8f2ec6a1c)|
|[9053a288eaef94f482fe551fa641fe6155aa3f9b](https://github.com/Shuang-su/metaxingtong/commit/9053a288eaef94f482fe551fa641fe6155aa3f9b)|2026-11-02T12:38:04+09:00|[8ce410a8783fce26cf7eb589689df283437e0001](https://github.com/Shuang-su/metaxingtong/commit/8ce410a8783fce26cf7eb589689df283437e0001)|
|[c9a1647fe88dd26a312d58183212a16c65b12521](https://github.com/Shuang-su/metaxingtong/commit/c9a1647fe88dd26a312d58183212a16c65b12521)|2026-11-02T12:45:16+09:00|[5ddb96f5627db9ef83be627ad8629a93cd4146c3](https://github.com/Shuang-su/metaxingtong/commit/5ddb96f5627db9ef83be627ad8629a93cd4146c3)|
|[82694151a2af4f3761325ab34296bd00464322ae](https://github.com/Shuang-su/metaxingtong/commit/82694151a2af4f3761325ab34296bd00464322ae)|2026-11-02T12:45:16+09:00|[61a0de5943e34cbdf08e284717ae6a5376f23171](https://github.com/Shuang-su/metaxingtong/commit/61a0de5943e34cbdf08e284717ae6a5376f23171)|
|[8f2f66e0877dd72494077d3d8ee70730a95254eb](https://github.com/Shuang-su/metaxingtong/commit/8f2f66e0877dd72494077d3d8ee70730a95254eb)|2026-11-02T12:51:15+09:00|[d4034e3630c3bcc7546ecaf2c319b4b80a1f2d2c](https://github.com/Shuang-su/metaxingtong/commit/d4034e3630c3bcc7546ecaf2c319b4b80a1f2d2c)|

### ferris

`history/ferris-remake-original-20261102` → `9d779065e7b3f56fc0228e4d26f16a29564aeee1`；原对象/作者日期/提交者日期/父链完整保留，新upstream归档使用实际新时间。

|原提交|原提交时间|当前归档提交|
|---|---|---|
|[ab44cbed30fb6eb19b85fb5eb54353fd30d96941](https://github.com/Shuang-su/metaxingtong/commit/ab44cbed30fb6eb19b85fb5eb54353fd30d96941)|2026-11-02T12:03:18+09:00|[a552be386031deff9dd4a6bc2e51be45f8ce268a](https://github.com/Shuang-su/metaxingtong/commit/a552be386031deff9dd4a6bc2e51be45f8ce268a)|
|[2f053bb0770f3708e364981cf137c0c69e78fe6f](https://github.com/Shuang-su/metaxingtong/commit/2f053bb0770f3708e364981cf137c0c69e78fe6f)|2026-11-02T12:05:02+09:00|[d4db22801cb2352cdc0f31fbcb088b3d135b0331](https://github.com/Shuang-su/metaxingtong/commit/d4db22801cb2352cdc0f31fbcb088b3d135b0331)|
|[92457bc3a3fd0799d880b2319baffcbddc6b1835](https://github.com/Shuang-su/metaxingtong/commit/92457bc3a3fd0799d880b2319baffcbddc6b1835)|2026-11-02T12:08:08+09:00|[bb5b480d6979972f475b01a05f6d637d805f7e57](https://github.com/Shuang-su/metaxingtong/commit/bb5b480d6979972f475b01a05f6d637d805f7e57)|
|[77b0a1c1100ce85f2a311a023592490d453fca3a](https://github.com/Shuang-su/metaxingtong/commit/77b0a1c1100ce85f2a311a023592490d453fca3a)|2026-11-02T12:19:41+09:00|[977a4c872bcabfbf5285d95b5822c024e8ae0b20](https://github.com/Shuang-su/metaxingtong/commit/977a4c872bcabfbf5285d95b5822c024e8ae0b20)|
|[a295a5ff904b98bb283b36c35351f3f3c7459b0c](https://github.com/Shuang-su/metaxingtong/commit/a295a5ff904b98bb283b36c35351f3f3c7459b0c)|2026-11-02T12:29:43+09:00|[e0f05fa5ffb534dc4d7940e8be003a0173e2e9c2](https://github.com/Shuang-su/metaxingtong/commit/e0f05fa5ffb534dc4d7940e8be003a0173e2e9c2)|
|[25bdcafa6b0ec8ecdb00b371c4ca203431e29038](https://github.com/Shuang-su/metaxingtong/commit/25bdcafa6b0ec8ecdb00b371c4ca203431e29038)|2026-11-02T12:47:46+09:00|[fd099f2728ac77b5937e580f84bf2f1fc07dbfaa](https://github.com/Shuang-su/metaxingtong/commit/fd099f2728ac77b5937e580f84bf2f1fc07dbfaa)|
|[9d779065e7b3f56fc0228e4d26f16a29564aeee1](https://github.com/Shuang-su/metaxingtong/commit/9d779065e7b3f56fc0228e4d26f16a29564aeee1)|2026-11-02T12:58:10+09:00|[92f45209ac1871101de8d1733eb5d14ec3ff8ce1](https://github.com/Shuang-su/metaxingtong/commit/92f45209ac1871101de8d1733eb5d14ec3ff8ce1)|

## 验证边界与剩余

- 308图片远端原字节可解码；17评论正文/API图片属性核对通过。网页实际视口显示0/308；已知GitHub Chromium证书错误路线未重试或绕过，不能把解码/HTML当网页实显。
- 发布端未运行输入脚本、建模、渲染、Blender回导、深度推理或叠图算术。模型/像素/独立review结论按原包记载，发布端只核字节、清单与文字，不能冒称重跑。
- 音游厅R03仅M01有条件源光照纹理，未知灰、无inpaint；不是完整albedo。原R02整场图与R03局部8回归分开，失败camera-only从未写进CURRENT。新源不是旧时刻，前screen约150px/留出低板金条52–123px等FAIL，后续独立回放缺。
- 营地C06卷毯仅两固定训练机位局部改善，柔软端/纵提带未还原。3源同BV、第三早已见；后箱三f和右檐第三10.93–26.45px仍FAIL。原C05全部172路径保留，8269415冻结后仅新增5QA记录；最终6张原生叠图与扩20范围分别记录，不能互换计数。
- 摩天轮R05仅front条件相机，R04其它3source/MAIN/10CHECK准确继承。门训练mean.539px不能抵消保留窗174–193px及前门遮挡失败；176mesh和115168/8192有限射线不证明数学全水密，.001亚网格角隙/动态扫掠未测。R02/03 exit130失败保存，灰外景未做。
- 没有三个Draft PR，也没有merge/approval。最终精确head的status/check-run/workflow另读，0检查不称CI通过。机器回执/HANDOFF自身将正常push后另从远端取回核验，最终报告记真实结果，本文件不提前宣称后续动作完成。
- Space三项临备仍冻结未删，未上传用户预览或模型到其他服务；由母任务独立核验后决定清理。红月未交本端消费，未查找或拉取。
