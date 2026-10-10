# 海滨开放场景 · 留存最早可核实模型及说明

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 最早可核实的留存包
旧包是海滨公路、宽窄步道、岸墩链条、灯杆、棕榈、坡地与海面的有限独立场景。

这些是已恢复的历史实物；“最早可核实”不保证此前没有版本。
- `03_Seafront_Textured_GLB.zip`；7759018字节；Library版本0；SHA256 `8f15d00281d98b21858b1376409452aa48a4644d98c2a99d23e704f16941c816`。
  - 模型 `models/Seafront_Textured.glb`：SHA256 `7fce6d802c057c79918b8d48200eb8493bd1ea17cab2cdcb402b3fd804f726cd`。
- `02_Seafront_Textured_Blender.zip`；9975672字节；Library版本0；SHA256 `b60ea9570656ee9889bd49913e2eb3ef03d23b99d7ee8c47caf5adc2a71885ae`。
  - 模型 `models/Seafront_Textured.blend`：SHA256 `ea5e1b9341c7625aa2406c7ecff4c0afb48339cf0f211f4d4ee9132ac23355d7`。

#### 旧包说明依据：03_Seafront_Textured_GLB.zip 内 README_海滨场景.txt
星瞳 · 夕阳海滨公路｜可编辑三维重建
来源：《与星瞳共度的一天》2024-04-19，BV1mx4y1z7oY
https://www.bilibili.com/video/BV1mx4y1z7oY/

一、证据与范围
参考公开回放中的三帧：1:42:50（沿道路）、1:45:10（侧向表演）、1:47:15（无人海上斜视）。三帧属于正文中的连续海滨场景，不是片尾海滨静态结束卡；本模型是独立室外场景，不与卧室、厨房或舞房拼接。
人物不建模。截图中的人物、平台播放器与水印也不进入材质。

二、交付
01_Seafront_White_Models.zip：Seafront_White.blend、Seafront_White.glb。
02_Seafront_Textured_Blender.zip：Seafront_Textured.blend、外部PBR贴图。
03_Seafront_Textured_GLB.zip：Seafront_Textured.glb，使用纹理内嵌的单文件格式。
04_Seafront_Previews_and_QA.zip：白/材质成对全景、参考叠图、原始参考、回导校验、生成脚本。
每个ZIP小于18 MiB。

三、结构与编辑
Blender 4.3.2；米制。核心模型按01–08分组：道路标线、海侧步道、岸墩与链条、陆侧步道、海崖与坡地、棕榈与地被、灯具、近海波面。
道路、白/黄标线、路缘、矮岸墩、交错链环、弯曲灯杆、棕榈树干/叶片、地被、陆坡、崖体和水波网格均可编辑。不是一张整体场景图贴到平面，也未进行镜头图像warp。
双向道路宽7.2m，海侧步道2.25m，矮岸墩2.65×0.46×0.52m，路灯约12.0m。这些是保证尺度连贯的工作假设，不是从原工程获取的实测值。
近海网格有真实波面起伏和法线细波纹。棕榈枝叶为有UV的实体表面，不是始终朝向镜头的整株树卡。

四、格式差异
白模与材质版的核心几何相同，仅材质与用于预览的灯光不同。白模保留UV。
两个GLB仅导出01–08核心模型，适合继续编辑或导入其他实时引擎。GLB并不包含Blender程序天空、公里级远海延伸、太阳发光球、参考用后期辉光和可选巨型日轮。
Blender中上述内容分别放在09、10、11集合；巨型唱片状日轮默认关闭，打开10_Optional_Stage_Sun并取消该物体的隐藏即可查看侧向表演版本。它是1:45:10可见的舞台化视觉效果，不能作为真实太阳尺寸依据。
GLB查看器的环境光/色调映射可能与Blender不同，不能保证截图式同色；导入后建议用自有夕阳环境照明。

五、相机与预览
Camera_A_reference_6170：沿道路视角，25mm正常透视。
Camera_B_reference_6435：海侧低斜视，27mm正常透视。
Camera_C_side_6310：侧向道路表演方向，32mm正常透视。
Camera_D_geometry_overview：27mm正常广角总览，展示海岸与陆坡结构。
成对图是在同一相机和同一几何下渲染。材质图采用96采样，最终预览经外部Open Image Denoise清理噪点。
参考叠图仅将截图的播放器外框裁去至原视频画面（1188×668），再以50%透明度与同分辨率渲染叠加；没有局部变形或非均匀拉伸。

六、纹理
7组原创程序PBR：沥青、步道铺装、风化混凝土、海崖、坡地草土、棕榈树皮、棕榈叶；另有潮湿沥青粗糙度与随机波谱水面法线。
基础颜色为sRGB；粗糙度与OpenGL（+Y）法线为Non-Color。纹理都在Blender内打包，同时附带外部PNG。GLB内嵌核心模型使用的图像。
纹理不是原场景贴图的提取或复原。低码率360p参考不足以识别真实材质品牌、精确纹理图案、叶片拓扑或小型花草细节，故未声称这些部分精确。

七、已知局限
画面能支持海在左、陆坡在右、沿岸道路及连续构件的关系，不能确定绝对米制尺寸、被遮挡的地形断面、整段道路全长、每棵棕榈的精确位置/枝叶结构、远处未见区域。
海崖、远景延伸与植被个体为合理补全。参考的光晕、光斑与日轮显著舞台化；本交付使用原创程序环境与可选舞台几何近似，不承诺逐像素复刻。
请结合source_render_comparison和overlay_50pct文件判断相似程度；叠图是证据对照，而非证明精确复现。

八、校验
qa/roundtrip_validation.json记录两种GLB重新导入Blender后的对象/三角形/边界/UV/纹理情况。
核心网格348,756个三角形，1,901个独立可编辑网格对象。大量对象来自可逐环编辑的实体链条。若实时应用需要合批，可按集合自行合并；此交付优先保留可编辑性。
PNG纹理可从textures/materials_manifest.json查看生成方法与建议物理平铺尺寸。

#### 本阶段实际归档路径
- `scenes/seaside-scene/01-retain-earliest-binaries/assets/02_Seafront_Textured_Blender.zip`；9975672字节；SHA256 `b60ea9570656ee9889bd49913e2eb3ef03d23b99d7ee8c47caf5adc2a71885ae`；Git blob SHA1 `e0fc77316d145b4fe6299d70788b6291714cf264`。
- `scenes/seaside-scene/01-retain-earliest-binaries/assets/03_Seafront_Textured_GLB.zip`；7759018字节；SHA256 `8f15d00281d98b21858b1376409452aa48a4644d98c2a99d23e704f16941c816`；Git blob SHA1 `4db6f894d15951397a59d4e0a1dfcf398f572151`。

#### 日期语义
- 02_Seafront_Textured_Blender.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- 03_Seafront_Textured_GLB.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
