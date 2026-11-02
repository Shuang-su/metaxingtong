# 2026-11-02 第二批发布归档 HANDOFF

远端 payload 完整性核验实际完成于 2026-11-02T02:03:02.357708+00:00；本交接记录随后以真实当前时间正常提交。

## 接收与完整性

两个冻结输入已在本执行器通过当前Library正式流程物化、应用身份并核存在/大小/SHA256。廊架version1、环舞台version3均匹配。两bundle完整且fsck通过，确认是已归档CP01/R00的真实后继；没有消费此前已清理的4项或任何海港后继。

|Library身份/版本|文件|字节|SHA256|
|---|---|---:|---|
|`libfile_62d9c9703a6881918a21e7fc46d608a4` / 1|colonnade-Nov2-native-diagnostic.bundle|64013161|`e97129b108fab3d3e041c018aeb51f8bcbddfdd19fab01da331d7426e36d0633`|
|`libfile_627f3732be0c81919ddf72968e085879` / 3|festival-ring-remake-R01D-final-20261102.bundle|107894303|`196ccc8c7b85a6b2c03bafc0dfcf7313a0aea5ae78a7bc12fc0a81318b1ad7ee`|

最终250普通原件合计230,107,095字节；4个新归档说明后payload共254文件、230700177字节。两个回执文件另计，本批最终新增256路径。最大的普通原件12,028,656字节；107,894,303字节的运输bundle未提交、未切片，普通Git不用LFS。

独立新空bare仓从GitHub官方HTTPS正常fetch完整两条原history，再正常部分克隆获取两条上游归档分支。没有本地clone、复制对象或alternates。对所有254 payload路径实际读取字节核大小/SHA256/Git blob，核16个新归档阶段快照、22条完整原提交（6条此前已有+本批16条）以及全部379个独立可达原commit/tree/blob。fsck通过。第一批路径远端diff为0；无关main继承promisor blobs不在全量下载断言范围。

机器证据：[remote_verification.json](remote_verification.json)，含每项expected/remote_actual、各阶段路径、原始对象与fetch日志，明确分开树核验、实际字节取回和网页实显。

## 固定payload与对应PR

|范围|当前归档payload|Draft PR|普通原件|
|---|---|---|---|
|colonnade|[d82b53470e8cdeb1d047519256158a0557a6ce35](https://github.com/Shuang-su/metaxingtong/commit/d82b53470e8cdeb1d047519256158a0557a6ce35)|[#94](https://github.com/Shuang-su/metaxingtong/pull/94)|[85文件](https://github.com/Shuang-su/metaxingtong/tree/d82b53470e8cdeb1d047519256158a0557a6ce35/scenes/lantern-petal-stage/research/colonnade-remake-cp02-20261102/files)|
|festival|[a31c0458e00ac9d9435361ea8f3f67034bb692c6](https://github.com/Shuang-su/metaxingtong/commit/a31c0458e00ac9d9435361ea8f3f67034bb692c6)|[#95](https://github.com/Shuang-su/metaxingtong/pull/95)|[165文件](https://github.com/Shuang-su/metaxingtong/tree/a31c0458e00ac9d9435361ea8f3f67034bb692c6/scenes/festival-ring/research/remake-r01d-20261102/files)|

两PR沿既有分支追加，无重复场景PR。base均为main `6ad31e4b2fe8398060c33de20fc09f5edad427a7`。本回执在festival payload后另加正常metadata commit，PR95最终head因此不同于payload；不冒充新生产模型阶段。第一批文件/映射及旧原件丢失记录继续保留。

## 当前模型和报告入口

- [colonnade/models/NOV2_CP02_workcamera_material.blend](https://github.com/Shuang-su/metaxingtong/blob/d82b53470e8cdeb1d047519256158a0557a6ce35/scenes/lantern-petal-stage/research/colonnade-remake-cp02-20261102/files/models/NOV2_CP02_workcamera_material.blend)。
- [colonnade/models/NOV2_CP02_workcamera_white.blend](https://github.com/Shuang-su/metaxingtong/blob/d82b53470e8cdeb1d047519256158a0557a6ce35/scenes/lantern-petal-stage/research/colonnade-remake-cp02-20261102/files/models/NOV2_CP02_workcamera_white.blend)。
- [colonnade/models/NOV2_CP01_material.glb](https://github.com/Shuang-su/metaxingtong/blob/d82b53470e8cdeb1d047519256158a0557a6ce35/scenes/lantern-petal-stage/research/colonnade-remake-cp02-20261102/files/models/NOV2_CP01_material.glb)。
- [colonnade/models/NOV2_CP01_white.glb](https://github.com/Shuang-su/metaxingtong/blob/d82b53470e8cdeb1d047519256158a0557a6ce35/scenes/lantern-petal-stage/research/colonnade-remake-cp02-20261102/files/models/NOV2_CP01_white.glb)。
- [colonnade/docs/CP02-result.zh.md](https://github.com/Shuang-su/metaxingtong/blob/d82b53470e8cdeb1d047519256158a0557a6ce35/scenes/lantern-petal-stage/research/colonnade-remake-cp02-20261102/files/docs/CP02-result.zh.md)。
- [festival/versions/R01D/ring-remake-R01D-material.blend](https://github.com/Shuang-su/metaxingtong/blob/a31c0458e00ac9d9435361ea8f3f67034bb692c6/scenes/festival-ring/research/remake-r01d-20261102/files/versions/R01D/ring-remake-R01D-material.blend)。
- [festival/versions/R01D/ring-remake-R01D-white-same-geometry.blend](https://github.com/Shuang-su/metaxingtong/blob/a31c0458e00ac9d9435361ea8f3f67034bb692c6/scenes/festival-ring/research/remake-r01d-20261102/files/versions/R01D/ring-remake-R01D-white-same-geometry.blend)。
- [festival/versions/R01D/ring-remake-R01D-white-export-slots.blend](https://github.com/Shuang-su/metaxingtong/blob/a31c0458e00ac9d9435361ea8f3f67034bb692c6/scenes/festival-ring/research/remake-r01d-20261102/files/versions/R01D/ring-remake-R01D-white-export-slots.blend)。
- [festival/versions/R01D/ring-remake-R01D-material.glb](https://github.com/Shuang-su/metaxingtong/blob/a31c0458e00ac9d9435361ea8f3f67034bb692c6/scenes/festival-ring/research/remake-r01d-20261102/files/versions/R01D/ring-remake-R01D-material.glb)。
- [festival/versions/R01D/ring-remake-R01D-white.glb](https://github.com/Shuang-su/metaxingtong/blob/a31c0458e00ac9d9435361ea8f3f67034bb692c6/scenes/festival-ring/research/remake-r01d-20261102/files/versions/R01D/ring-remake-R01D-white.glb)。
- [festival/docs/R01D-current-delivery.zh.md](https://github.com/Shuang-su/metaxingtong/blob/a31c0458e00ac9d9435361ea8f3f67034bb692c6/scenes/festival-ring/research/remake-r01d-20261102/files/docs/R01D-current-delivery.zh.md)。
- [festival/qa/independent-review/R01D-final-independent-review.md](https://github.com/Shuang-su/metaxingtong/blob/a31c0458e00ac9d9435361ea8f3f67034bb692c6/scenes/festival-ring/research/remake-r01d-20261102/files/qa/independent-review/R01D-final-independent-review.md)。

## 逐版本记录

- cp01：[Issue 88 comment 6566746612](https://github.com/Shuang-su/metaxingtong/issues/88#issuecomment-6566746612)；append_existing。
- r00：[Issue 90 comment 6566747389](https://github.com/Shuang-su/metaxingtong/issues/90#issuecomment-6566747389)；append_existing。
- cp02：[Issue 88 comment 6567333363](https://github.com/Shuang-su/metaxingtong/issues/88#issuecomment-6567333363)；create。
- r01a：[Issue 90 comment 6567334126](https://github.com/Shuang-su/metaxingtong/issues/90#issuecomment-6567334126)；create。
- r01b：[Issue 90 comment 6567334920](https://github.com/Shuang-su/metaxingtong/issues/90#issuecomment-6567334920)；create。
- r01c：[Issue 90 comment 6567335632](https://github.com/Shuang-su/metaxingtong/issues/90#issuecomment-6567335632)；create。
- r01d：[Issue 90 comment 6567336611](https://github.com/Shuang-su/metaxingtong/issues/90#issuecomment-6567336611)；create。

CP01/R00在原评论追加真实后继检查，原正文完整保留；CP02、R01A/B/C/D各首次一条。B字镜像/低机位失败、C来源/负绕序失败及D有限修复分开，不把R00改写成D。

## 原历史与新归档逐阶段

### colonnade

原history `history/colonnade-cp01-original-20261102` 从 `b752755708fad0196306bc4da4e57aeb1b054964` 正常fast-forward至 `f42d2c5db04c430044a6327f08b5d1a93d7c215f`。原作者/提交者、真实日期与父链字节保留。

|原独立commit|原提交日期|新归档commit|
|---|---|---|
|[b742050a21631e97781fc7c083fe5f788d7f7c5f](https://github.com/Shuang-su/metaxingtong/commit/b742050a21631e97781fc7c083fe5f788d7f7c5f)|2026-11-02T09:59:59+09:00|[1c0684748e20987c1e5e17243567aad6c16129ca](https://github.com/Shuang-su/metaxingtong/commit/1c0684748e20987c1e5e17243567aad6c16129ca)|
|[95b11d4945167f2f07c0c47e83de50f05e9405b3](https://github.com/Shuang-su/metaxingtong/commit/95b11d4945167f2f07c0c47e83de50f05e9405b3)|2026-11-02T10:03:28+09:00|[b3f60e35c4f34c960689ce7cab9faf360aa30662](https://github.com/Shuang-su/metaxingtong/commit/b3f60e35c4f34c960689ce7cab9faf360aa30662)|
|[4f2743b6b068b6ae7a00d90f0cc61ae8cb97d7f4](https://github.com/Shuang-su/metaxingtong/commit/4f2743b6b068b6ae7a00d90f0cc61ae8cb97d7f4)|2026-11-02T10:12:05+09:00|[4230d84b02b500a9e141af818e07f3758301a560](https://github.com/Shuang-su/metaxingtong/commit/4230d84b02b500a9e141af818e07f3758301a560)|
|[07cdb99f6c4eb25f6d49fbb849b4103622c8494e](https://github.com/Shuang-su/metaxingtong/commit/07cdb99f6c4eb25f6d49fbb849b4103622c8494e)|2026-11-02T10:15:01+09:00|[0a9d39c7f4082105a5543b8bcf0d10d19469e6e8](https://github.com/Shuang-su/metaxingtong/commit/0a9d39c7f4082105a5543b8bcf0d10d19469e6e8)|
|[b9a44ac5d5c88c2b4b91ef1265787f16f0ed1a75](https://github.com/Shuang-su/metaxingtong/commit/b9a44ac5d5c88c2b4b91ef1265787f16f0ed1a75)|2026-11-02T10:18:03+09:00|[e5667de82d9f2fcfebd9f365b836d7631a13a147](https://github.com/Shuang-su/metaxingtong/commit/e5667de82d9f2fcfebd9f365b836d7631a13a147)|
|[f42d2c5db04c430044a6327f08b5d1a93d7c215f](https://github.com/Shuang-su/metaxingtong/commit/f42d2c5db04c430044a6327f08b5d1a93d7c215f)|2026-11-02T10:18:51+09:00|[7e458db5324c848c3195599b8d198d61a6417afe](https://github.com/Shuang-su/metaxingtong/commit/7e458db5324c848c3195599b8d198d61a6417afe)|

CP02 是 CP01 之后的有限 M03 廊架模块来源诊断：124 mesh 几何保持，新增条件机位、两新原生 4K 与实际相对深度、原生材白/直接50叠图。透视、梁带与柱脚对齐 FAILED。完整屋面、外列、栏杆、灯笼及圆台不在本模块；不能称整场恢复。CP01 主图像素和 GLB hash 的重现只是确定构造复现，旧 BLEND 未找回。

### festival

原history `history/festival-r00-original-20261102` 从 `1ccae9c211b54e63af7b1e49d8ab3d5996cd27d2` 正常fast-forward至 `45d07619525288c692f61ef3c202e268bfe1c69e`。原作者/提交者、真实日期与父链字节保留。

|原独立commit|原提交日期|新归档commit|
|---|---|---|
|[7000396777f8d57e7591184890282ba56d84ae14](https://github.com/Shuang-su/metaxingtong/commit/7000396777f8d57e7591184890282ba56d84ae14)|2026-11-02T10:01:09+09:00|[f0f193aa8d39529b6ee59d8a2e5308a1be10328b](https://github.com/Shuang-su/metaxingtong/commit/f0f193aa8d39529b6ee59d8a2e5308a1be10328b)|
|[8ca8a787af2b209389d3b3fdd0041cfdbb38ab4b](https://github.com/Shuang-su/metaxingtong/commit/8ca8a787af2b209389d3b3fdd0041cfdbb38ab4b)|2026-11-02T10:02:13+09:00|[85521e2e1c0635e5f400096b6d1f5f1f46637edf](https://github.com/Shuang-su/metaxingtong/commit/85521e2e1c0635e5f400096b6d1f5f1f46637edf)|
|[74edf0b13581c8f2eeb1da9c13c58255d145a221](https://github.com/Shuang-su/metaxingtong/commit/74edf0b13581c8f2eeb1da9c13c58255d145a221)|2026-11-02T10:05:04+09:00|[dabb3a2b06de786b5a58e34dccb35544491204ae](https://github.com/Shuang-su/metaxingtong/commit/dabb3a2b06de786b5a58e34dccb35544491204ae)|
|[62b9f21c6a85470da0ffc6aad2769e3ade1e727a](https://github.com/Shuang-su/metaxingtong/commit/62b9f21c6a85470da0ffc6aad2769e3ade1e727a)|2026-11-02T10:12:19+09:00|[ed767c0f09217ea84a53596c0ae2970ddf0fa846](https://github.com/Shuang-su/metaxingtong/commit/ed767c0f09217ea84a53596c0ae2970ddf0fa846)|
|[0a71ed79b700b9c98fbdef6190ec080ecd25ccb5](https://github.com/Shuang-su/metaxingtong/commit/0a71ed79b700b9c98fbdef6190ec080ecd25ccb5)|2026-11-02T10:15:38+09:00|[82879380291ead58a962fbce2a82a9aec2a4fcb8](https://github.com/Shuang-su/metaxingtong/commit/82879380291ead58a962fbce2a82a9aec2a4fcb8)|
|[691112c8c47490efaa53ef648447219ab606990e](https://github.com/Shuang-su/metaxingtong/commit/691112c8c47490efaa53ef648447219ab606990e)|2026-11-02T10:15:58+09:00|[f563be1e70608930da999cdf526c4265527346be](https://github.com/Shuang-su/metaxingtong/commit/f563be1e70608930da999cdf526c4265527346be)|
|[49027b03759cb062eb08d190b9b7bb4e7e9f543c](https://github.com/Shuang-su/metaxingtong/commit/49027b03759cb062eb08d190b9b7bb4e7e9f543c)|2026-11-02T10:18:14+09:00|[fa186e76276760291e0479a14ddbbe1f5ecc75b5](https://github.com/Shuang-su/metaxingtong/commit/fa186e76276760291e0479a14ddbbe1f5ecc75b5)|
|[5d1b4a6e547669cd9b0efb5ac1a672a96800a839](https://github.com/Shuang-su/metaxingtong/commit/5d1b4a6e547669cd9b0efb5ac1a672a96800a839)|2026-11-02T10:20:06+09:00|[26a7e8e2004f4e966cba708e3fc88031031fafba](https://github.com/Shuang-su/metaxingtong/commit/26a7e8e2004f4e966cba708e3fc88031031fafba)|
|[e8996ddd5d4347977f858054b13c1f17de7b9835](https://github.com/Shuang-su/metaxingtong/commit/e8996ddd5d4347977f858054b13c1f17de7b9835)|2026-11-02T10:23:01+09:00|[30211c0be578b053146b9b80d4211fdd431f5821](https://github.com/Shuang-su/metaxingtong/commit/30211c0be578b053146b9b80d4211fdd431f5821)|
|[45d07619525288c692f61ef3c202e268bfe1c69e](https://github.com/Shuang-su/metaxingtong/commit/45d07619525288c692f61ef3c202e268bfe1c69e)|2026-11-02T10:49:39+09:00|[4b710022a2c7321df41802f36ad5d87c97439568](https://github.com/Shuang-su/metaxingtong/commit/4b710022a2c7321df41802f36ad5d87c97439568)|

当前 R01D 为旧环舞台重制作未验收候选，269 mesh，保存5个最终材白BLEND/实灰槽/GLB和完整图证。R01B 字镜像/低机位失败及 R01C 剩余来源/负绕序失败保留；D只修23闭合体绕序和2饰带+.012径向去共面，不重新拟合主体。左右粗弧、星链、第三机位、支承仍 FAILED/未证；12后亮件+0.001728间隙、2暗楔-0.000272轻穿保留，不称完整工程通过。不是旧 F07 恢复或新场景。

## 检查边界与剩余

- 文件/原对象/阶段快照的远端字节失败数0。91张图解码及API img/href属性通过，网页实际视口显示0/91。已知Chromium GitHub net::ERR_CERT_AUTHORITY_INVALID路线未重试、未绕过，不能把解码或HTML当显示成功。
- 发布执行器仅读取/归档，未执行包内生成脚本、Blender、渲染或深度推理。另对收到的8张native direct50做纯RGB数组全像素floor((source+render)/2)比较，最大误差0、异常通道0；这不是来源对齐验收。原几何/回导报告只核字节和阅读，不冒称重跑。
- 廊架CP02透视、梁带、后柱脚仍FAILED，模块不含完整廊架/舞台。原生新时间不冒旧图恢复，主图像素/GLB hash重复不证明旧BLEND取回。
- R01D只是23绕序及2饰条共面限定修复。左右粗弧、星链、第三机位、基础支承仍FAILED/未知；12后亮件间隙约0.001728、2暗楔轻穿约0.000272工作单位未解除。不能称整场工程/来源通过。
- 三环舞台源与两廊架源为本轮新补采训练资料，未建立后续独立回放验收。相对深度原网格924×518，高分显示是派生，非米制、隐藏结构或接触真值。
- CI需以最终精确head单列检查；本记录不把无检查称为CI通过。main未变，无强推/LFS/新PR/合并/批准/权限修改/凭据读取或Space删除。
- 此两Space身份保持不动，母任务按冻结版本和远端核验统一决定清理。正在制作的海港后继没有查找或接收。

本回执与HANDOFF推送后会另从远端fetch读回自身字节；实际结果在最终报告给出，本文件不预先声明该后续动作完成。
