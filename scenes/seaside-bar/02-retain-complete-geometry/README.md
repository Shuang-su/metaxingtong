# 海边吧台 · 记录完整有限空间几何升级

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 完整有限空间几何升级
#### 几何变化
形成有限半开放服务结构、真实中央/左侧洞口、柜背柜底和落地支撑；不增完整后房/屋顶/钢琴区。
#### 材质与导出
删除相机朝向日落平面，保留开放海向视线和中性背景；白模/材质同几何，自含GLB。
#### 来源、多角度及QA
新A22:18.578219、B22:33.015559为前后静态构图，70:13重复、结束卡只道具参考；A大罐/B小罐布局不统一，采用B阶段；不再把前罐确定为灯。

以下说明来自实际交付文件；其中技术验证是随包已记录结果，本次仅重核文件字节/CRC，没有重新运行Blender。
说明文件 `README_海边吧台完整结构_中文.txt`；SHA256 `5c0b5a82af3516ad25fe3a17e62c1da7d43479512d90ee1c77dec0c23f37e29e`。

海边吧台完整结构 · 2026-10-10 候选修订

1. 本次交付是什么
这是一套统一、可编辑、可绕看的半开放吧台服务结构。窗墙为有限厚度实体；中央大开口与左侧矩形开口是真实空洞；上掀板、两根撑杆、铰轴、柜体、前服务台和连续地面均为三维几何。不是只有正面好看的无背面贴片布景。
仍然没有足够来源证明完整房间或独立凉亭，因此没有添加封闭后房、完整屋顶、玻璃幕墙、门、钢琴区或它们的连接。为使构件落地，补入地面平台、柜底/柜背/支撑、短侧墙墙角。这些补全属于设计推断，不是源片证实的真实围合。

2. 证据及尺度
来源：https://www.bilibili.com/video/BV1CY411k7Co/
A：22:18.578219，前段近景空场。
B：22:33.015559，后段正面空场。
70:13.494927 为 B 类重复视角；117:04.993156 为重新编排的结束卡，仅作道具参考。
105 分钟钢琴外景没有已证实的空间连接，未纳入模型。
本轮来源是前后静态构图，切镜/叠化不能充当连续相机运动；没有新增旋转或平移基线。源画面没有展示地面、天花、门及完整侧后围合。绝对尺度未知，Blender 使用无量纲相对单位，不能解释为实测米。
媒体解码1920×1080；实际浏览器源图精确裁剪1180×663。独立源图没有缩放、补绘或几何形变，不能称原生1080截图。

3. 统一几何与参考近似
主模型采用 B 段后期道具布局。所有普通视角与 A/B 参考相机共用同一模型，没有相机相关隐藏、移动或变形。A 中巨大左前罐、B 中小罐阵列及前后变化无法同时由单个固定布局解释；没有把前罐当灯，没有强迫同一物体三角化。
A/B均为透视近似相机；不是光学标定，不保证还原源镜头焦距。QA包含1180×663等尺寸材质/白模渲染及50%直接叠图。叠图残差真实保留，来源中的海天景、文字、水印、暂停标记没有从模型渲染中抹掉或伪造。中央窗台暗色杂物身份不清，未强行补成确定物体。为避免把图像挡板冒充真实海向空间，删除旧相机朝向的落日平面。独立模型保留开放视线，采用中性环境背景。

4. 可见及推断层
源图支持：有限米黄窗墙、大开口、左侧矩形开口、上掀木板、两侧撑杆、柜台面、服务台、酒瓶、杯子、饮料罐、书本及圆托盘。
推断：墙厚、完整柜背柜底、层板与底座、地面平台轮廓、左右低矮返墙、后侧表面、铰轴细节。新增推断构件位于“09_推断_地面柜体墙角”集合，构件属性提供证据标签；集合中少量补全的可见支撑件另标“源图支持的构件”。
开口外侧未增设围挡，主开口和左开口无遮挡；侧向进出通路保留。上掀窗板没有扩张成屋顶。

5. 文件与检查
models/seaside_bar_complete_textured.blend：打包贴图的材质版。
models/seaside_bar_complete_textured.glb：独立通用材质版。
models/seaside_bar_complete_white.blend/.glb：真正的白色材质替换，几何一致。
renders：10个普通检查视角、外侧背面、柜底、顶视及A/B相机渲染。
qa：直接叠图、三联图、检查总览、闭合/法线/退化/UV/开口射线/真实GLB导入检查。
qa/section_diagnostic_only.blend：只用于展示截面的诊断副本。x=0剖切会移除右半部，不是主模型，也不参与源图对齐。
几何检查只证明相应技术条件，不能证明真实历史房间形状。所有版本的未见部分仍须更多源视角验证。

脚本说明：scripts保留本次构建和检查记录。早期构建脚本引用原v0源模型及当前工作目录，重新运行需自行调整根目录和准备源包；成品BLEND已打包贴图，GLB自含资产，不依赖这些路径。脚本不是另一个隐藏的场景版本。


#### 当前文件身份与哈希
- `03_Seaside_Bar_Textured_Blender.zip`；4096038字节；Library版本1；SHA256 `cabbb18d0b4ca42e3fdb9ed969f4c480aa73789b2809d0d429659b8e2df97c84`。
- `02_Seaside_Bar_Textured_GLB.zip`；2021558字节；Library版本1；SHA256 `9caa66d0c70fe06e3a75569ef36c6e14ba65c7d9042783c10cb55f02386c513c`。
- `01_Seaside_Bar_White_Model.zip`；3212942字节；Library版本1；SHA256 `895ab4952af6206e0bb601f191c8d6e2b6a51a7e7ef82b07d61a6e5a1c02f561`。
- `04_Seaside_Bar_PBR_and_QA.zip`；14835347字节；Library版本1；SHA256 `9aeb9f449ce01e0817687da5562893ccb39d140b780a03c16aa4e3c5f099eede`。
- `海边吧台_完整结构_检查总览.jpg`；245754字节；Library版本0；SHA256 `26a5630574a0dd04bf09314cf417749c0a8f452088c533d42c63867a93a6e000`。

#### Library时间证据（不是聊天发布日期）
- `03_Seaside_Bar_Textured_Blender.zip`：条目创建 2026-10-07T23:38:09.944462Z；最近修改 2026-10-10T04:59:17.395388Z；当前Library版本 1。
- `02_Seaside_Bar_Textured_GLB.zip`：条目创建 2026-10-07T23:38:09.970007Z；最近修改 2026-10-10T04:59:17.408292Z；当前Library版本 1。
- `01_Seaside_Bar_White_Model.zip`：条目创建 2026-10-07T23:38:09.970487Z；最近修改 2026-10-10T04:59:17.403911Z；当前Library版本 1。
- `04_Seaside_Bar_PBR_and_QA.zip`：条目创建 2026-10-07T23:38:09.943109Z；最近修改 2026-10-10T04:59:17.385190Z；当前Library版本 1。
- `海边吧台_完整结构_检查总览.jpg`：条目创建 2026-10-10T04:59:17.354573Z；最近修改 2026-10-10T04:59:17.354573Z；当前Library版本 0。

#### 待解决
有限吧台结构完整；围护、背部及支撑含推定，材质与源片精确拟合未证明。
- 未取得逐次聊天发布的确切时刻；Library创建/修改时间不替代聊天发布日期。
- 不能确认所有中间发布版本均已恢复；缺失历史不重建、不补造旧提交。

#### 2026-10-10 逐场来源覆盖补充核验
- 1920×1080解码；1180×757截图、1180×663裁图。
- 登录后采集：未知：未找到可关联该场有效帧的登录状态日志。
- 独立角度：A/B两构图族；未找到明确新增平移或旋转，不能称两已标定基线。
- 新证据使用：新A/B实际进入结构解释和最终直接overlay；70分钟为重复，结束卡仅道具参考。。
- 跨视频后续回放：未证实：已检查记录只有单个BV；同BV更晚时间不等于后续其他回放。
- 原生1080导帧未实现。总体来源验收仍待复核。详见 `scenes/seaside-bar/source-coverage-audit-20261010.json`。

#### 本阶段实际归档路径
- `scenes/seaside-bar/02-retain-complete-geometry/assets/03_Seaside_Bar_Textured_Blender.zip`；4096038字节；SHA256 `cabbb18d0b4ca42e3fdb9ed969f4c480aa73789b2809d0d429659b8e2df97c84`；Git blob SHA1 `1f01855f849ee2fd82f62849f948abd9bb08eb5e`。
- `scenes/seaside-bar/02-retain-complete-geometry/assets/02_Seaside_Bar_Textured_GLB.zip`；2021558字节；SHA256 `9caa66d0c70fe06e3a75569ef36c6e14ba65c7d9042783c10cb55f02386c513c`；Git blob SHA1 `834cb94d180d7c1fb7339e86c0c628df9b74f096`。
- `scenes/seaside-bar/02-retain-complete-geometry/assets/01_Seaside_Bar_White_Model.zip`；3212942字节；SHA256 `895ab4952af6206e0bb601f191c8d6e2b6a51a7e7ef82b07d61a6e5a1c02f561`；Git blob SHA1 `e83e1159a6428ff77d903f0ec280752446019b2d`。
- `scenes/seaside-bar/02-retain-complete-geometry/assets/04_Seaside_Bar_PBR_and_QA.zip`；14835347字节；SHA256 `9aeb9f449ce01e0817687da5562893ccb39d140b780a03c16aa4e3c5f099eede`；Git blob SHA1 `5ff5cdf7d22cd132de1c610681606c8fe8ee4eca`。
- `scenes/seaside-bar/02-retain-complete-geometry/assets/海边吧台_完整结构_检查总览.jpg`；245754字节；SHA256 `26a5630574a0dd04bf09314cf417749c0a8f452088c533d42c63867a93a6e000`；Git blob SHA1 `891dfb5ee357ca2567ceef3fa6e4b3bf43e0cfbc`。
- `scenes/seaside-bar/source-scope.json`；2546字节；SHA256 `f795f15c9cac28f7e22b87868bcba62d073b5ff87a6a7549dca8c42ee142453c`；Git blob SHA1 `93d7b5aa5f430fbaf7b7e4aad6fb138b6e6f6142`。
- `scenes/seaside-bar/source-coverage-audit-20261010.json`；2173字节；SHA256 `37281242dd361d929546ee0137f7553ab139b2b53d0d87348272191a1a379346`；Git blob SHA1 `98fd73a8708e2c76274da86e079ae6d641e0ba79`。

#### 日期语义
- 03_Seaside_Bar_Textured_Blender.zip：library_item_created_at=2026-10-07T23:38:09.944462Z；library_item_modified_at=2026-10-10T04:59:17.395388Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
- 02_Seaside_Bar_Textured_GLB.zip：library_item_created_at=2026-10-07T23:38:09.970007Z；library_item_modified_at=2026-10-10T04:59:17.408292Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
- 01_Seaside_Bar_White_Model.zip：library_item_created_at=2026-10-07T23:38:09.970487Z；library_item_modified_at=2026-10-10T04:59:17.403911Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
- 04_Seaside_Bar_PBR_and_QA.zip：library_item_created_at=2026-10-07T23:38:09.943109Z；library_item_modified_at=2026-10-10T04:59:17.385190Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
- 海边吧台_完整结构_检查总览.jpg：library_item_created_at=2026-10-10T04:59:17.354573Z；library_item_modified_at=2026-10-10T04:59:17.354573Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
