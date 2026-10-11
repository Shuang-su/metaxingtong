# 卧室（7.7深最终版） · 留存最早可核实模型及说明

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 最早可核实的留存包
旧版为床、竖软包、棋盘织物、床柜、灯钟、地毯、人字地板及装饰画的近正面重建；无独立侧/反面基线。

这些是已恢复的历史实物；“最早可核实”不保证此前没有版本。
- `02_Bedroom_White_Models.zip`；2555776字节；Library版本0；SHA256 `7597431f5a074541ebfbbfd0dda06731eef8bc25e05847104fa84652526958a4`。
  - 模型 `models/02_bedroom_white.blend`：SHA256 `ed694e08302e8257afaa61bd039b539fb6dcbf81d6ca1450316af91ef70bb9aa`。
  - 模型 `models/04_bedroom_white.glb`：SHA256 `3b34f5696e5e0202d992b5cd2b6e6396e2f3798136a75ff521877ab91f866b50`。
- `03_Bedroom_Textures_Review.zip`；9998102字节；Library版本0；SHA256 `d368f07eced42812ab71e132405ac37aec5d3024e49a2237bd69eefec1c64a54`。
- `01_Bedroom_Material_Models.zip`；13096810字节；Library版本0；SHA256 `b7e4be7a0470c0e6096c2225cec0b23371790d4c51f9975b9d5632e50a294096`。
  - 模型 `models/01_bedroom_material.blend`：SHA256 `4e8c2410fb77ac0ad70f7711e0d0e02bac0ff78c4f36d3c09bd07378c029a5fe`。
  - 模型 `models/03_bedroom_material.glb`：SHA256 `72adddcd15f8da59ce12ce4e8591ef22d4950728eddc48ef7ad1806532022887`。

#### 旧包说明依据：02_Bedroom_White_Models.zip 内 README_中文.txt
星瞳卧室｜《与星瞳共度的一天》2024-04-19 场景近似重建
来源：https://www.bilibili.com/video/BV1mx4y1z7oY/

这是独立卧室的可编辑3D重建，不是官方资产、测量级复原或完整户型。没有把直播人物建入模型，也没有把整张截图投射到房间。

证据与边界
- 全景主要参考50:07、50:40；床头细节参考50:10、11:14、15:11、1:15:03、1:30:20；右柜和灯钟参考1:55:14。
- 这些截图几乎沿同一正前方方向。近景与全景是景别变化，不是独立侧向验证。没有已确认的背面、侧墙或反向机位。
- 真实网格：竖软包床头/床框，床垫与有厚度的布料，黑白棋盘枕被，地毯，人字拼花地板，墙面线框，床边白柜和细支架，橙色蘑菇灯，蓝色小闹钟，相框，大叶植物。
- 墙上红色漫画、床头小画像是单独绘制的近似装饰图，未声称还原原画。植株叶片可见部分有依据；盆器、背部枝叶未被明确拍到，属于补全。
- 房间深度、左右侧墙、顶面、被床挡住的墙和家具背面均为推定。房间面向相机的一面留开，方便检查。不与舞房、厨房或客厅拼成未经证实的户型。
- 尺寸采用合理公制假设：床框约2.29×2.30m，床垫约2.19×2.27m、顶面约0.50m，低床头顶面约0.87m。房间约7.6×5.7m、顶高3.3m。视频没有标尺，所以不是测量值。

交付
models/01_bedroom_material.blend：带材质版。贴图已打包，Blender 4.3.2。
models/02_bedroom_white.blend：同一份几何的纯白模型。
models/03_bedroom_material.glb：带PBR材质可交换版。
models/04_bedroom_white.glb：同一几何的纯白GLB。
textures/：8组512px BaseColor / Roughness / Normal，另含两张近似装饰画；材质基于真实UV，未使用整房背景贴图。
renders/：正常水平广角、另一方向自由查看、正面参考镜头和同轴拉近镜头、白模图、源图叠加和并排对照。
analysis/：几何一致性、GLB回导报告、少量手工标注结构点的相机拟合记录。
references/：公开直播回放截图，仅作对照。
scripts/：重建、细化、导出与检查脚本，便于继续修改。

使用与检查
- 默认打开QA_wide_level相机：正常水平广角，垂直线保持竖直。不要只看匹配机位判断模型是否合理。
- MATCH_front_50m07_same_axis是正面长焦近似拟合；MATCH_close_50m10_same_axis使用同一姿态的1.971倍镜头缩放和画幅偏移，没有移动或局部拉伸家具来骗对齐。
- overlay只表示同轴画面比较。人物、衣物、浮层、原画差异和遮挡会存在；不能将叠图称为多视角一致性证明。
- 单独重绘的装饰画、低清来源和推定背面会限制相似度。没有进行全图相似度打分或把手工结构点误差当作全场景精度。
- GLB仅含模型、UV、材质和相机；工作室灯光未作为互换结果要求，其他软件应自行配置照明。查看器色彩管理不同会造成外观差异。
- 渲染为Cycles CPU，4线程。预览使用外部Open Image Denoise降噪；原始渲染与降噪图均保留于工作目录。

时间戳说明
截图文件名使用浏览器跳转的目标秒数，播放器捕获时常已前进约1秒。例如home_3007在截图中显示50:08，home_3040显示50:41，home_3010显示50:11。时间引用均为约值，不作逐帧同步声明。

照明、木色和织物粗糙度为近似设置，不是由低清视频反演的实测PBR参数。整体尺度/布局先按正常观察角度检查，再用同一份几何匹配正前方镜头。最终细节调整包括整体降低枕头和翻转真实叶片面，未按镜头变形房间或家具。

可复现脚本顺序：generate_textures.py → build_bedroom.py → solve_front_camera.py → refine_and_export.py → final_detail_pass.py → final_boundary_pass.py → validate_glb.py。最后可用denoise_images.py生成降噪预览，并运行create_review_and_package.py打包。

最终边界检查：补全植物作为整体前移0.65m；仅推定的房间右侧边界加宽0.4m，避免叶片穿墙。床、柜及参考相机没有因此移动或变形。

#### 本阶段实际归档路径
- `scenes/bedroom/01-retain-earliest-binaries/assets/01_Bedroom_Material_Models.zip`；13096810字节；SHA256 `b7e4be7a0470c0e6096c2225cec0b23371790d4c51f9975b9d5632e50a294096`；Git blob SHA1 `a6d30c0f016deda85c8b66d7c766fcfb327b877f`。
- `scenes/bedroom/01-retain-earliest-binaries/assets/02_Bedroom_White_Models.zip`；2555776字节；SHA256 `7597431f5a074541ebfbbfd0dda06731eef8bc25e05847104fa84652526958a4`；Git blob SHA1 `ab4d01fe13854463fcfbb0e86b889812c08ac304`。
- `scenes/bedroom/01-retain-earliest-binaries/assets/03_Bedroom_Textures_Review.zip`；9998102字节；SHA256 `d368f07eced42812ab71e132405ac37aec5d3024e49a2237bd69eefec1c64a54`；Git blob SHA1 `2444999a0c3cfb6455d1ee0dffff0a3b2c7690e2`。

#### 日期语义
- 01_Bedroom_Material_Models.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- 02_Bedroom_White_Models.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- 03_Bedroom_Textures_Review.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
