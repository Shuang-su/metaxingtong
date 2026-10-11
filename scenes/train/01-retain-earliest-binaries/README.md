# 列车 · 留存最早可核实模型及说明

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 最早可核实的留存包
旧版保留深绿座椅、相向桌、红帘、灯具和窗列的统一车厢可见组件，3个旧包含白模/材质/审阅。

这些是已恢复的历史实物；“最早可核实”不保证此前没有版本。
- `xingtong_train_white_models.zip`；2907076字节；Library版本0；SHA256 `2d6c3ec3bd2de596ac76e8f37b5c2feab15a3f6322ef72e4153c4a6140658417`。
  - 模型 `02_train_white.blend`：SHA256 `263146a88d4fbccc08d4569a3478a43d50b965f5b3441ac69cab1ad51233ee85`。
  - 模型 `04_train_white.glb`：SHA256 `af0c20bfab16027390c2f530eecb5d834b1b792c9a951b1dbe106c97d595c206`。
- `xingtong_train_review_textures.zip`；11232940字节；Library版本0；SHA256 `17f58bb5d9a9cbe0358e595e5f5ce5aeeaedede91335d48aa72915fc05e46970`。
- `xingtong_train_material_models.zip`；13856128字节；Library版本0；SHA256 `f79eb0414b9cdefa42860f7dfbbff3af0bb8efafb1c729257b0f141ba7bc2d84`。
  - 模型 `01_train_material.blend`：SHA256 `b313809aadbf0ee5480afcbbc2fa01dab083b3e339d0b5107be84a7bb5d8f186`。
  - 模型 `03_train_material.glb`：SHA256 `cdcf235b8579ad03e8334eda8644605f632c409d078b69d1c7b3beb5659e4d81`。

#### 旧包说明依据：xingtong_train_white_models.zip 内 README_中文.txt
星瞳《深月列车情缘！》复古车厢：可编辑近似重建
来源：https://www.bilibili.com/video/BV1fMP4ziEUd/ （2026-03-06，1:47:31）

交付重点
- 真实三维网格车厢，中央过道、双侧相向高背座位、靠墙直边/靠过道圆端木桌、窗框玻璃、红色褶皱窗帘、行李架/斜撑/行李、中央顶棚/灯/通风格栅、端门/维修门/花瓶花束。
- 材质版及白模版使用同一套几何。提供各自的 .blend 和 .glb。
- 正常、水平的18mm广角是整体比例检查的主要依据；参考机位A/B/D和叠图用于观察视角差异，没有对渲染做透视变形或移动单个家具来适配不同镜头。
- 18张512×512 UV PBR位图（6组Base Color、Roughness、Tangent Normal）和1张站名牌位图。它们是本次作者程序生成的材质，不是原始资产或实物扫描；Blender内已打包，外置PNG也提供。

证据及视角
- 11:36、13:59：车厢纵深宽镜头，用于重复模块及整体空间判断。
- 11:51：门上滚动牌特写，可核实“THE NEXT STOP IS SHENYUE STATION”。模型用该句的静态排版，不还原滚动动画。
- 12:01、12:28：同一车厢的粉色表演灯效果；用于圆端桌、靠背、门窗上部横竖分格和维修门结构，未另造舞台。
- 15:19（A）：右侧座位近景；45:12（B）：左侧偏轴镜头；13:59（D）：纵向较宽镜头。
- 1:00:16：端门与两侧圆端桌/花瓶更清楚。保留该近似相机，但最近桌面遮挡与原图仍有差异，不把它作为精确对齐成功证据。
- 14:16：侧窗外有夜景楼灯；外部城市只用独立可隐藏的简化几何表示，没有尝试确认具体城市。
- 35:10：有移动售货车；本交付固定车厢未重建人物、售货车、食物/服装及表演烟雾、彩纸、舞台投影等动态道具。
- 本视频正文抽样证据显示这些机位属于同一车厢；不是对1小时47分每帧逐一检查的声明。

尺度与不确定性
- 单位为名义米：内宽约3.0m、内长11.1m、中央净高约2.6m，桌面0.795m、座垫0.48m、座背顶部约1.28m。没有原场景尺寸或相机参数，不能作为工程测量使用。
- 宽帧至少能辨认5组窗/座位重复；模型每侧采用6个紧凑模块（节距1.8m）。第6组、整车总长以及未拍到的反向端墙是合理补全，不是得到证实的原布局。
- 所有机位公用同一几何；对齐只是近似。人物遮挡、低清画质、镜头运动及未知镜头参数使门窗、天花线和近端靠背仍有可见残差。对照图如实保留误差，不声称像素级复原。
- 细小花瓣、皮面簇绒、箱包、五金和木纹为低清证据下的合理细化；告示牌小字未猜造。
- 材质blend含可隐藏的夜景外部几何、参考/QA相机、Cycles面光。GLB为便携室内网格和相机，使用嵌入PBR贴图；不包含Blender面光及外部城市。
- 白模用于核查形体，采用中性灯光。白/材质两版室内几何哈希应一致；verification.json记录实际检查，GLB有独立回导验证。

文件
01_train_material.blend / 02_train_white.blend：可编辑工程。
03_train_material.glb / 04_train_white.glb：便携室内模型。
normal_material.png / normal_white.png：相同正常水平广角成对检查。
comparison_*.jpg：参考、渲染、50%叠图（人物未建，UI/水印不作为几何）。
textures/：完整外置UV PBR位图；references/：本次机位依据。
scripts/：重建/修订脚本；其路径变量需要随本地目录修改。

最终验证（2026-10-07）
- 1742个室内网格，均有UV；GLB回导后267840个三角面，坐标有限。
- 两版Blender的室内几何哈希一致；两版GLB的规范化世界坐标三角形哈希也一致。
- 19张图像全部嵌入材质版（18张512×512 PBR图＋站牌）；GLB没有外部图像URI。
- D机位固定24mm，仅拟合相机位置/朝向。5个手读结构锚点在1188×668参考中的平均残差2.65px、最大6.05px。锚点本身有低清读数误差；这不是全图对齐分数。
- 对比A可见近端花束与原图遮挡不同，B的窗列/顶棚仍有误差；花束位置、皮面细节并非原资产测量结果。
- normal_material.png和normal_white.png是优先检查空间合理性的正常广角；comparison_B/D是不同参考机位的诚实对比，comparison_A额外保留近景局限。
- 展示PNG经过OIDN降噪，没有任何几何/透视变形。

#### 本阶段实际归档路径
- `scenes/train/01-retain-earliest-binaries/assets/xingtong_train_material_models.zip`；13856128字节；SHA256 `f79eb0414b9cdefa42860f7dfbbff3af0bb8efafb1c729257b0f141ba7bc2d84`；Git blob SHA1 `1e3f6118676a0598fd312d9ca7e136a19989c6a9`。
- `scenes/train/01-retain-earliest-binaries/assets/xingtong_train_review_textures.zip`；11232940字节；SHA256 `17f58bb5d9a9cbe0358e595e5f5ce5aeeaedede91335d48aa72915fc05e46970`；Git blob SHA1 `75fad202c28f6f41f65cdb2f25020e1bc8d2e281`。
- `scenes/train/01-retain-earliest-binaries/assets/xingtong_train_white_models.zip`；2907076字节；SHA256 `2d6c3ec3bd2de596ac76e8f37b5c2feab15a3f6322ef72e4153c4a6140658417`；Git blob SHA1 `88fbaa39aa8961ec8ed0f9ca02317b7ae9f930e8`。

#### 日期语义
- xingtong_train_material_models.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- xingtong_train_review_textures.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
- xingtong_train_white_models.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
