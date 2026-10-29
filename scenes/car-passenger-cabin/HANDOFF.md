# car-passenger-cabin 本地交接

结果：第三个有边界的新局部候选已实际制作；不是完整第三场已验收场景。四张原生来源已经本环境通过当前官方 Library 流程物化、逐张实际查看并核对 1920×1080、字节数和 SHA256。范围是现代汽车副驾门板/窗/镜、A柱/顶棚/遮阳板、仪表台右端风口及有限座椅边缘。前向 S04 仅条件性上下文，不重建整车或未知驾驶台。

工作树：`/workspace/metaxingtong`；分支：`scene/car-passenger-cabin`；基线：`6ad31e4b2fe8398060c33de20fc09f5edad427a7`。没有 push、新建 PR/Issue、修改 main/archive/history、校园或钢琴任务，没有新 ZIP、LFS 或凭据/安全设置变更。

真实本地阶段：

1. `13c70e7` 来源范围与原件核验。
2. `d4732d0` 共享白模、门状态、初次白模图。
3. `03a68b8` 材质试验与初版几何失败记录。
4. `f68fcb3` 流形/法线/退化面修复、镜支撑连接、GLB真实回导。
5. `32591b5dfc1096e344db4eada7d20eff5587fe5b` 完整对照、九张检查、证据表及交付。
6. 最后另提交本交接及本地 commit 全字节读回报告。

核心交付：

| 文件 | 字节 | SHA256 |
|---|---:|---|
| models/car_passenger_cabin_material.blend | 2834652 | 2b2dbba578bd2ae5127b10a4a5946ab2a9d72ade08f9467210ff4105ed35ab8f |
| models/car_passenger_cabin_white.blend | 1492640 | a40ce69724df0b97ab3e0562934be905689bfcf1ddb026a317545fea840080fc |
| models/car_passenger_cabin.glb | 1361400 | 9c9abc8767002fa189e954b0ff05403750aa8e2b886eb85acaf99ef3194a5fb2 |
| renders/main/car_passenger_cabin_main.png | 2304946 | fe63ae730fe91f5dff839b1296f09493fb2d30f44fa62506d3c3093b956eab0c |
| renders/main/car_passenger_cabin_main.jpg | 252883 | 1d343f2d932c8f332390094cef9766e5422a38a5741d9b666cce607e089ca9a6 |

JPEG 与 PNG 都是 1920×1080，JPEG 未缩放，约247 KiB。材质 BLEND 已打包3张合成纹理，外部 PNG 同时保留。另有4张源机位渲染、4张直接50%叠图、7组同原生坐标的三联物件裁切、8方位+1开门检查、45物件证据表及完整脚本。14张最终渲染和全部原件、叠图经过本地自动校验；9张任意角原图及主图/源对照已实际查看。接触/背面/镜反射等限制见 REVIEW，检查图不是来源新增角度。

检查：45网格闭合流形、正体积、零退化面；400窗孔+200槽体+208风口间隙射线通过局部允许域。白模和材质版在帧1关门、帧2开门几何一致；GLB实际导出、清空场景、重新导入45网格，关门/开门最大顶点差分别1.19e-7/4.92e-7模型单位。回导场景 qa/glb_actual_reimport.blend 保留。99个文件共70,291,793字节已从本地提交32591b5逐blob全字节读回并与工作文件一致；不是远端读回证明。

来源仍明显未对齐：圆风口手工中心残差约146/133/120px（±15px选点不确定性），A柱斜率、遮阳板范围、门板比例与材质夜景差异继续存在。没有跨BV新角度、完整回放检查、最高可用画质完整证明、完整内舱或连续门运动防碰撞验收。用户未接受。未知玻璃升降状态、厚度、支撑和被角色遮挡部件均标为推断/未见。

阻塞：当前官方 `library_upload.py` 对83个有序交付文件（47,908,595字节）的单次批量保存，在 hosted apps `tools/list` 阶段返回HTTP 401，状态为失败，没有返回任何保存成功或新Library ID；不是自动审批拒绝。未缩批、重试、改走直接create、手工signed URL或扩大权限。来源 read/materialize 成功，不能泛化成账号断连。完整本地文件与Git提交保留；上传状态和目标清单见 qa/library-upload-status.json。父线程可在正常受支持通路恢复后继续协调，不应把清单或本地提交描述为已经上传。
