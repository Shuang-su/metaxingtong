# 深月KTV开放舞台 · 留存最早可核实模型及说明

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 最早可核实的留存包
旧版是棋盘台面、蓝带、沙发、灯、望远镜、悬星和城市背景组件，没有充分墙顶证据。

这些是已恢复的历史实物；“最早可核实”不保证此前没有版本。
- `04_KTV_Views_and_QA.zip`；8390611字节；Library版本0；SHA256 `d765f32402e5771d9a900dac268eb069238d49b99a031ba21f005d93141d3246`。
- `03_KTV_Textured_Blender.zip`；9844083字节；Library版本0；SHA256 `f5f73f23083bcc26f344957c19160ea47999219722fedf3fdd4ce09803e8cb12`。
  - 模型 `models/Xingtong_KTV_Textured.blend`：SHA256 `08aa390ad3dbb88d4a93bd88f9b0585ee39062c59829a2af303a42514fbc5098`。
- `04_KTV_Views_and_QA.zip` 的Library条目首次创建：2026-10-07T22:26:05.276485Z；不等于聊天发送时刻。

#### 旧包说明依据：04_KTV_Views_and_QA.zip 内 README_深月KTV.txt
星瞳 3D 直播场景重建 · 深月 KTV 舞台可见组件
版本：2026-10-07 / Blender 4.3.2

参考
https://www.bilibili.com/video/BV1ru41147sn/
2023-05-13《深月KTV盛大开业》，视频长度 2:08:03。
主机位 A：1:15:29（截帧播放器显示约 1:15:30）；近景 B：35:17；空镜 D：1:58:39。
另核对 20:25、25:21、45:18、1:05:15、1:31:24、1:55:59。
截图中的播放器界面、字幕、水印、人物没有重建进场景。

范围与可信度
这是城市背景舞台的可见组件重建，不是完整房间，也不是原官方资产。
明确可见：黑白棋盘表面、蓝色后侧窄带、两张银蓝色单人鼓包沙发、左侧落地灯、望远镜/三脚架、悬挂银星、舞台摇头灯与返送音箱。
没有证据支持玻璃窗墙、固定围护、天花或真实吊点；本文件没有添加这些结构。
悬线只延长到视野外，端点不是对天花位置的确认。
平台可见内边按参考布置；镜外前方深度、支撑厚度、背面、隐藏接缝和尺度为合理推定。单位采用米，是相对比例尺度，无实测尺寸。
远景城市是程序化体块、独立窗口面与霓虹线的简化背景，仅粗略对应轮廓；没有复制原城、没有臆造不清晰文字。
左上仅局部露出的带环球饰按可见形状简化。星形轮廓、褶皱和后背等存在不可避免的近似。

真实几何与材质
所有主要物件都是可编辑 mesh；没有把直播截图铺成整张场景平面。
棋盘为逐块独立面片；家具是封闭鼓包体，包含局部褶皱、前纽扣与凹陷；望远镜、三脚架、灯杆/灯罩、灯具、音箱和悬星均有独立网格。
银蓝织物使用原创平铺 base-color、roughness、normal 贴图及 PBR 材质。
.blend 的材质贴图已内嵌，同时附 textures/ 外部原图；.glb 图片内嵌。
.glb 主要交付几何/UV/PBR；不同软件的世界光、灯光与色调映射不会完全复现 Blender 预览，因此以配套渲染查看校准外观。

可隐藏组件
02_Inflated_Armchairs：可整组隐藏沙发，恢复站立/离场时的空舞台。
08_Optional_Star_Companion：黄色星伙伴为可移动独立道具，默认用参考附近的代表性摆位。没有绑定角色动画。
09_Optional_Moving_Balloon_Dog：红色气球狗在直播中持续改变位置，不是固定机位锚点。原生 .blend 中独立集合，默认隐藏；另附 Optional_Moving_Balloon_Dog.glb，按需单独导入和移动。
没有人物模型或表演动画，也不把移动道具当建筑。

文件
Xingtong_KTV_Textured.blend：完整材质版，默认正常全景相机。
Xingtong_KTV_White.blend：完全相同几何的白材质版。
Xingtong_KTV_Textured.glb / Xingtong_KTV_White.glb：相同核心几何的通用格式。仅默认隐藏的气球狗单独交付，避免 GLB 查看器强制把可选道具显示在主场景中。
Optional_Moving_Balloon_Dog.glb：上述独立移动道具。
预览：正常全景白/材质成对、A/B 机位白/材质成对、空舞台与望远镜细节。
QA：参考/渲染并排、50% 叠图、GLB 实际回导几何核对报告。

验证说明
白版与材质版在原生 Blender 和实际回导的 GLB 中分别比较几何。
回导检查物件名、三角面数、双向顶点坐标偏差、包围盒、表面积、UV 和图片内嵌。
roundtrip_validation.json 给出实际结果，不以仅“导出成功”代替回导验证。
参考叠图是对齐检查，不表示逐像素或工程测绘级精确；人物、动态道具及简化城市自然不会重合。

使用
Blender 打开 .blend 即可编辑；相机集合内保留正常全景和参考 A/B/D。
欲显示气球狗，在 Outliner 打开 09_Optional_Moving_Balloon_Dog 的显示及渲染开关。
需要空镜时，隐藏 02_Inflated_Armchairs 和 08_Optional_Star_Companion。
不要根据推定的镜外平台尺寸做施工或场地测量。
本作品为参考驱动的重建练习；原节目与角色设计的权利仍归各自权利人。

#### 本阶段实际归档路径
- `scenes/ktv/01-retain-earliest-binaries/assets/04_KTV_Views_and_QA.zip`；8390611字节；SHA256 `d765f32402e5771d9a900dac268eb069238d49b99a031ba21f005d93141d3246`；Git blob SHA1 `9baf684175feb9b25deab3745e29ffc7a7e6caa4`。
- `scenes/ktv/01-retain-earliest-binaries/assets/03_KTV_Textured_Blender.zip`；9844083字节；SHA256 `f5f73f23083bcc26f344957c19160ea47999219722fedf3fdd4ce09803e8cb12`；Git blob SHA1 `35c9e9432b4564cc7adbc4e8887d6d5c2485ff23`。

#### 日期语义
- 04_KTV_Views_and_QA.zip：library_item_created_at=2026-10-07T22:26:05.276485Z。同身份未修改的Library条目首次创建时间；不是模型制作/聊天发布时间。
- 03_KTV_Textured_Blender.zip：精确原始日期未知。只确认实际留存字节及内容阶段；未取得精确保存/制作/聊天发布日期。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
