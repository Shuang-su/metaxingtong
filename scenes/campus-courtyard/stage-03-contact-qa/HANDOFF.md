# Stage03 冻结交接

分支 `scene/campus-courtyard`。模型实际制作commit `19bbe72f231590f7feccb5a9b7cd6822b8eedfec`；其后未再改动模型。完整回归、图像和读回记录另作真实提交，最终冻结HEAD以母线程收到的最终回报为准。

本轮只使用四张原生源BV1GqXMByE1s。另一BV反向帧尚未接收、未使用；母线程说明该回放更早，不能算更晚回放验证。下一步先锁本轮共享几何、材质、照明、可见性，仅定新来源相机并检查留出关系，先报告基线差异再决定改模。

## 三个实际变化

1. SRC04右下地面侧边/空白改为连续铺地，同像素ROI1372/1537缺失射线降为0/1537，原始裁切保留。
2. 长凳脚垫、蓝/绿场灯与篮架底座、树池及楼梯底板贴合各自上表面。29个指定支承点通过；不是全场支承验收。近景前后图直接展示变化。
3. 花池02退出台阶、花池03退出蓝场，平面AABB分别留约0.04/0.89单位间隔；台阶连续截面消除嵌套盒体端面重叠。新花池位置仍推断。

独立只读复核两轮分别见qa/independent_review_stage02.md和qa/independent_review_stage03.md；作者另实际查看4组叠图、8角联系表与接触前后图。

窗格/立面/跑道与原四相机未改。上部特征的camera-only试验未通过、未采用；涂装试验暴露场地共享布局未解，实际失败图和模型均保留。植被只是体积近似。运动面边界/涂装、篮板与窗格投影、地表分层底部偏置及草地跑道边界、隐藏基础仍待复核，不宣称完整几何或来源验收。

## 关键不变量

- `geometry_sha256`：`63da7b79be472d305e5b158b898175a4a862d2e93d1edc3cd65b9a83f9173965`
- `material_nodes_sha256`：`95dee56141b972c1a5db7e8079d182215649e4f0d08a12efa5d4c2800013ac27`
- `material_assignments_sha256`：`17082b920c6e203bb621a3e9a06a1786b9b90cd8fb7ca1657c1ecbaff3c9f7b9`
- `texture_pixels_sha256`：`6ef63a0f744010cbf756266fb4221e7cb86b1cdb5eb82a1839dd986b07501f55`
- `lighting_sha256`：`cac46ec2728eded1ee4084ad6d741073f627828e51301df62384e10893b8cb59`
- `visibility_sha256`：`486d59ca5ab9d8768179c88a1e6dd1ee8378b21daa9a8d0b437c46fe3f958002`
- `source_cameras_sha256`：`f9e1b49a5d6ba2f7de893331d8f848f65b9069df4e75a97a628140089bf50c7d`

逐组件和实际节点/相机参数见qa/frozen_invariants.json。白模与材质世界几何哈希一致；GLB实际回导顶点双向最大差0，纹理像素hash一致。4张源/渲染/50%叠图全部1920×1080并验证直接混合；8检查角1280×720。

## 核心文件

| 文件 | bytes | SHA256 | Git blob |
|---|---:|---|---|
| campus-courtyard_material.blend | 14601752 | 0e006df071e40407ae0cc149de8d13f1cd5a68bab9cc7fe0c7cff621912a5fb4 | 035ee2dc6f8b653b819ddb15e927c3f1410b3afb |
| campus-courtyard_white.blend | 14602392 | da2c7a793a5d99e6c1d88ef3399fc309da89184d38e43feb0d0ef6eaf6dbe559 | f5a9fc00f45d0fd9471a91763d886750a20c197a |
| campus-courtyard.glb | 9077392 | 0879baa74835d153b80d964669d9c945725ee06495a7b71b7dae78ee0cebbd74 | e2a3e5d75c2c1583f682e46b0dee89a2c59e1d80 |
| qa/glb_actual_reimport.blend | 5328639 | 4f6e362678095d4f2019ae6d107b4b1fa7034ee01eceeeaaa1cf91e985e87cf1 | a416cdac83816386355858f9ac9d9f02fb2f2ef1 |
| renders/MAIN.png | 4071092 | ffce9941983aec591217b1d98e2680548c61854b303a01f6f0a333d738b7ecf3 | 2b780f8591b091f83e3f27f506c8d73038ad572f |
| renders/MAIN_display_preview.jpg | 462068 | d10e8e142707c29c4750d2d51e8d76583f5a8ff9cb18106f9b21917b685b17a7 | 8b55dd2a43b846550691233ff4f12d95a4684b58 |
| inspection_contact_sheet_display_preview.jpg | 295308 | 567595b1188a4d916e804e16fcb6368f72ebeffa71987249d72218202a43df4d | 52e06e91e3a9f878a73b21eb4cff6c92d524246a |
| qa/contact_before_after_sheet_display_preview.jpg | 162249 | 74dd5310264d395d0db05bb359c76769f0fdf9862cf630c163bc6d79c797bbc3 | 17f3fdd6cf8aabad758354b62f9c855a1b705a9e |

主图JPEG1920×1080、462,068B；八角小联系表JPEG1920×620、295,308B；接触对比JPEG1800×650、162,249B。均为有损展示副本，原PNG未改。

本轮未push/PR，也未进行Library重试或新上传；遵从母线程待授权安排。旧批量helper401只属于stage02尝试，不能把其原177文件请求当成本轮已上传。跨环境原件交付仍未完成；无新Library ID。
