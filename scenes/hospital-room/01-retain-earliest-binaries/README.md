# 病房 · 留存最早可核实模型及说明

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 最早可核实的留存包
旧整包及三拆包是同一病房：窗墙、沙发、绿椅、电视、部分病床、输液架等多机位近似；旧目录名office不代表另有办公室。

这些是已恢复的历史实物；“最早可核实”不保证此前没有版本。
- `xingtong_room_reconstruction.zip`；27697851字节；Library版本0；SHA256 `81457c3c7182f4d622cec50884ed240ed1ed1dcc3b58555e18ec15a8b85b3782`。
  - 模型 `xingtong_room_reconstruction/xingtong_room_interior.glb`：SHA256 `921cc9bd557761e38569db2b4f43ba19fc93cdb540794a954277bfd445ff3459`。
  - 模型 `xingtong_room_reconstruction/xingtong_room_materials.blend`：SHA256 `040ba00b3208849f223285b0472d9bf6f34f184ae42d3f52ce04a36090a0e3ba`。
  - 模型 `xingtong_room_reconstruction/xingtong_room_white.blend`：SHA256 `a58ba74ba12b653c0cf26c0c6c24246d59161932c1f50f5e0d3681d6aa1dceb1`。
  - 模型 `xingtong_room_reconstruction/xingtong_room_white_interior.glb`：SHA256 `7ef4d0cfdc17f4f16a9e9510b34b3c371b21a49e37325022158b201c3116572d`。
- `xingtong_textures_and_review.zip`；12149243字节；Library版本0；SHA256 `1b2dcc28aa9b6aaf732bd3634df1e2e9f8dd3748a0be39454da79623af9adf32`。
- `xingtong_material_models.zip`；13041227字节；Library版本0；SHA256 `e3cff5036d48bfff3492c3dce9af60b1686afea729725d3182368ee6c1c11809`。
  - 模型 `xingtong_room_reconstruction/xingtong_room_interior.glb`：SHA256 `921cc9bd557761e38569db2b4f43ba19fc93cdb540794a954277bfd445ff3459`。
  - 模型 `xingtong_room_reconstruction/xingtong_room_materials.blend`：SHA256 `040ba00b3208849f223285b0472d9bf6f34f184ae42d3f52ce04a36090a0e3ba`。
- `xingtong_white_models.zip`；2520325字节；Library版本0；SHA256 `4b922386472aa7d9ed0811b63a3684e95dc9ba169d596a201503f6c3ffd1c083`。
  - 模型 `xingtong_room_reconstruction/xingtong_room_white.blend`：SHA256 `a58ba74ba12b653c0cf26c0c6c24246d59161932c1f50f5e0d3681d6aa1dceb1`。
  - 模型 `xingtong_room_reconstruction/xingtong_room_white_interior.glb`：SHA256 `7ef4d0cfdc17f4f16a9e9510b34b3c371b21a49e37325022158b201c3116572d`。
- `xingtong_room_reconstruction.zip` 的Library条目首次创建：2026-10-07T09:55:49.213530Z；不等于聊天发送时刻。

#### 旧包说明依据：xingtong_room_reconstruction.zip 内 xingtong_room_reconstruction/README_中文.txt
星瞳 2026-03-27 直播室内布景 · 多机位参考重建
来源视频：BV1GqXMByE1s

这是一套可编辑的 Blender 场景近似重建，不是原始直播资产，也不是真实尺寸测绘。
主要结构、沙发、薄曲面绿椅、百叶、褶帘、帘轨、电视、床端板/床垫、输液架/挂袋、矮柜与花枝均为实际几何。未重建人物。

主要参考与机位：
H：18:21.37，无人前视，适合检查窗梃、沙发轮廓和绿椅。
F：30:23.92，电视墙/顶棚/床端板视角。
G：18:36.06，沙发与床同框广角，人物区域不作为误差评估区域。
补充：10:46.92 输液架和柜台；18:55.41 百叶/顶棚；29:57.63 更完整床端板。
未混入随后紫色舞台、校园或其它场景。

文件：
xingtong_room_materials.blend：完整材质版，外部贴图已打包。
xingtong_room_white.blend：同一套室内几何的白模版。玻璃保留透明，窗外背景隐藏。
xingtong_room_interior.glb：材质版室内几何与基础PBR材质，便于查看/导入。不含近似城市远景；渲染引擎差异会影响观感。
xingtong_room_white_interior.glb：同一室内几何的白模GLB。
textures/pbr/：5套材质，共15张512×512基础色、粗糙度、法线贴图。基础色为sRGB；粗糙度/法线为Non-Color。室内网格有UV。
renders/：H/F/G 三机位材质和白模渲染，1180×664。
overlays/：与同尺寸参考50%混合的叠图，无透视变形、无后期扭曲对齐。

打开 Blender：
默认相机为 MATCH_H。其它匹配机位在“09_Matched_Cameras”集合。
“07_Procedural_City_Approximate”和“11_Exterior_Only_Reference_Projection”为近似窗外背景，可独立关闭。
背景使用无人帧中经过排除的纯室外像素，未包含人物、室内物件或播放器UI。未观察到的窗外部分使用室外片段延展/镜像；外围重复建筑并非实景复原。室内没有用整张参考图作贴墙替身。

仍有差异与限制：
1. 参考源为360p播放截图放大，边缘有模糊、遮挡，不能从这些资料恢复高精度细节。
2. 场景单位与尺寸仅用于建模。房间绝对尺度、未见的地面、床架/床底、背面及最左侧结构均为推定。
3. 百叶高度、布帘褶皱、家具曲率、床的远近和不同视角间仍有可见残差。F机位窗帘边缘仍有几十像素量级偏移，G机位床端板/床面的相对高度与远近仍未完全吻合；不宣称像素级或完整空间精确复原。
4. 窗外为近似背景，人物与电视中的节目画面未复制。电视显示为无文字抽象线条的替代示意图，非直播逐帧内容，不用于画面内容的像素匹配评估。
5. 稀疏结构锚点的改进用于说明迭代效果，不等于整幅图的重建准确率。
6. 白模与材质版保留相同室内网格和物体变换；只更换材质和窗外可见性。

版本迭代：
v01：初始窗/沙发/椅几何与粗略电视墙机位。
v02：缩短沙发前深度、调整前景与部分机位，验证局部锚点不足以确定房间透视。
v03：结合干净前视与电视墙的平行线重解机位/结构，新增输液设施及真实穿孔床端板。
v04–最终：修正尖刺缝线、薄椅背、百叶高度、帘轨位置和帘的硬阴影，补UV与可导出的PBR贴图。

#### 本阶段实际归档路径
- `scenes/hospital-room/01-retain-earliest-binaries/assets/xingtong_room_reconstruction.zip`；27697851字节；SHA256 `81457c3c7182f4d622cec50884ed240ed1ed1dcc3b58555e18ec15a8b85b3782`；Git blob SHA1 `8e6bf359702f9e321f39b4a04eea0868954fea8e`。
- `scenes/hospital-room/01-retain-earliest-binaries/assets/xingtong_material_models.zip`；13041227字节；SHA256 `e3cff5036d48bfff3492c3dce9af60b1686afea729725d3182368ee6c1c11809`；Git blob SHA1 `92d1da870c6409e3e30e37f51a0f23f8dd152269`。
- `scenes/hospital-room/01-retain-earliest-binaries/assets/xingtong_textures_and_review.zip`；12149243字节；SHA256 `1b2dcc28aa9b6aaf732bd3634df1e2e9f8dd3748a0be39454da79623af9adf32`；Git blob SHA1 `ee821fb1c1c014065208e4acadfcbab1bf4bc6c6`。
- `scenes/hospital-room/01-retain-earliest-binaries/assets/xingtong_white_models.zip`；2520325字节；SHA256 `4b922386472aa7d9ed0811b63a3684e95dc9ba169d596a201503f6c3ffd1c083`；Git blob SHA1 `4506150dc876dc0da5b17587963dbb120c1db873`。

#### 日期语义
- xingtong_room_reconstruction.zip：library_item_created_at=2026-10-07T09:55:49.213530Z。同身份未修改的Library条目首次创建时间；不是模型制作/聊天发布时间。
- xingtong_material_models.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- xingtong_textures_and_review.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- xingtong_white_models.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
