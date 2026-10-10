## 本次实际入库状态：阶段尚未归档齐

以下整包/文件已提交，保持冻结原字节：
- scenes/castle-hall/02-retain-complete-geometry/assets/03_Castle_Hall_Textured_Blender.zip（8279321 bytes）
- scenes/castle-hall/02-retain-complete-geometry/assets/02_Castle_Hall_Textured_GLB.zip（3826367 bytes）
- scenes/castle-hall/02-retain-complete-geometry/assets/Castle_Hall_FullRoom_Inspection.jpg（548478 bytes）

以下完整原包仍待 Git 完整文件传输；仅列元数据，不是已上传文件：
- scenes/castle-hall/02-retain-complete-geometry/assets/04_Castle_Hall_Views_and_QA.zip（13121061 bytes，SHA256 1a5ab52ac4df2ddea1d565f14e281d050df207dd89132bd1ed159cc3a8bed12e）

没有分片，也没有把缺少QA/模型的阶段算作归档完成。历史日期与本次commit创建日期分开；模型仍为候选，来源忠实度未通过。

# 城堡宴会厅 · 记录完整有限空间几何升级

状态：重建候选 / 待来源复核。来源忠实度与几何技术检查分别记录。

### 完整有限空间几何升级
#### 几何变化
升级连续厚地板/四墙/天花；八侧窗、中央拱窗改为真洞口；补推定后入口双门与固定支座，恢复桌脚接触及气球系绳。
#### 材质与导出
18张纹理嵌入BLEND，GLB带UV/PBR；白模/材质共用几何，跨软件光照不保证一致。
#### 来源、多角度及QA
A45:15/C73:44近正面，B75:07有限斜视；1597网格拓扑检查、991,990密集射线及25,244洞口探针属于结构证据，不是实测城堡。

以下说明来自实际交付文件；其中技术验证是随包已记录结果，本次仅重核文件字节/CRC，没有重新运行Blender。
说明文件 `README_城堡宴会厅_完整房间.txt`；SHA256 `dd0c57173d88ea4d17840316df682d41245d51fc189b61823e88915722045572`。

星瞳 CASTLE HALL · 完整房间重建
版本：2026-10-10 / Blender 4.3.2

这次完成了什么
在前版城堡宴会厅可见组件上，补成固定、封闭、可从任意位置检查的完整厅体。
- 连续有厚度的地板、四周墙体和天花，接缝有实体接触。
- 两侧 8 个窗洞改为真正穿墙孔洞，补窗台、窗楣、窗侧回边；蓝色夜景窗片保留厚度。
- 中央拱窗按拱形切出实际洞口，填补原来拱窗两侧及上部的缺墙，补完整拱形洞口回边。
- 镜头后方增加明确标注为推定的后墙和双扇入口；入口有门洞、门框、门槛与闭合门扇。
- 补齐柱头薄叶、开放管线端口与地面嵌块的实体厚度，统一检查法线；恢复桌脚落地、壁灯固定支座和气球系绳/配重。
- 保留已观察到的柱列、八角/菱形地面、拱窗、桌布、甜品、花束、礼盒、气球和壁灯。人物与播放器界面不建模。

源证据和不确定性
来源：https://www.bilibili.com/video/BV1aw411T7ws/
2023-11-10《回城堡咯！》直播回放。
源帧 A：00:45:15 左右，正面空镜。
源帧 B：01:15:07 左右，小幅斜向视角，人物遮挡明显。
源帧 C：01:13:44 左右，较宽正面视角，可交叉检查拱窗与柱头。
播放器画面时间约晚 1 秒。原始截图保留在 references/；配准截图只做固定矩形裁切 (0,26)-(1188,694)，不做透视变形。
A/C 是相近正面视角，不是两个独立校准基线；B 也仅提供有限斜向约束。本包没有把同轴缩放或模型渲染当作新源证据。

尚未恢复或无法确认
1. 这不是官方原始资产，也不是逐像素、摄影测量或工程测量级复原。源图低清、有遮挡，相机是手动近似匹配。
2. 天花形制、镜头后方墙体、入口位置与样式、镜外墙体延伸、墙厚均是为几何完整性作出的合理推定；对象集中在 11_Inferred_Rear_Entrance_and_Ceiling，并带证据属性。
3. 入口通向哪里未知。本包没有建造或确认城堡厅与前半段花园之间的连接。
4. 建筑名义尺寸约为 14 × 34 × 8.8 模型单位，中央抽检通行带宽约 2.3 模型单位。比例来自家具与建筑先验；不是实测米数。Blender/glTF 的单位约定不构成实际尺度证据。
5. 柱列数量、间距、门窗比例、材质纹理、灯光、花束/蛋糕/礼盒细节仍为近似。装饰密度与源片有差异；没有把灯光亮斑做成建筑凹凸。
6. 蓝色窗片是有厚度的夜景材质，不是窗外环境的完整重建；未恢复外部花园、城市或景观。
7. 整厅围护完成不代表隐藏布局已被源视频验证。源图叠图专门保留残差，不宣称精确注册。

模型使用
models/Xingtong_Castle_Hall_FullRoom.blend：材质、灯光、参考机位和独立检查机位齐全，18 张纹理已嵌入。默认进入完整厅体视图。
models/Xingtong_Castle_Hall_FullRoom.glb：真实网格、UV、PBR 图片嵌入，适合其他 DCC 和查看器；灯光、相机、色调映射不保证跨软件一致。
所有模型网格都保持可见；没有为了某个机位隐藏墙、移动道具或加入扭曲照片平面。背面剔除已启用，结构不依赖双面材质伪装闭合。

检查图如何阅读
- Match_A / B / C：真实源帧、当前模型同机位渲染、50% 直接叠图；人物遮挡和色调差异仍可见。
- Entry / Reverse / Side / Ceiling / Exterior：任意位置的结构检查图，均基于同一完整模型。
- Cutaway：在临时副本中作真实剖切以观察室内布局，明确不是源证据，也不是交付模型中隐藏墙面的状态。
检查图使用 Cycles 32 samples，外部 Open Image Denoise 去噪；颜色和接缝以模型及原始未去噪渲染为准。

重建脚本说明
scripts/ 记录本次建模与检查步骤。若要从前版重跑，将 baseline/ 中前版 Blender 包解压到同级 restored/，然后在 Blender 中运行 complete_hall.py、final_small_repairs.py、fix_arch_aperture.py、fix_envelope_seams.py，再运行验证/导出脚本。直接使用 models/ 中已打包的 .blend 不需要这些步骤。

技术验证
详见 qa/fullroom_geometry_validation.json、qa/semantic_aperture_validation.json、qa/independent_dense_envelope_validation.json 与 qa/fullroom_glb_roundtrip.json。全部 1,597 个网格零开边/非流形边/退化三角面。10,800 条常规围护射线及 991,990 条独立密集边缘射线均无漏出；八侧窗、中央拱窗和后门洞另通过 25,244 点无实墙遮挡检查。中央拱洞进一步验证射线命中有厚度窗片而不是墙。
逐件网格闭合检查与围护射线测试是互补检查；场景是多个接触/相交的真实实体部件，并非所有道具焊成一个单体网格。
有限抽样可排查明显漏缝和路径遮挡，不是数学证明或施工安全认证。
原节目、角色和场景设计权利归各自权利人。本包为源参考驱动的重建练习。


#### 当前文件身份与哈希
- `03_Castle_Hall_Textured_Blender.zip`；8279321字节；Library版本1；SHA256 `c8854932dc55bb8dc0a47e306a1b06d6af757eb6b7d0745eb96f4f012fdd0158`。
- `02_Castle_Hall_Textured_GLB.zip`；3826367字节；Library版本1；SHA256 `978f459d88eeba8fbaef36e01176d3dcf2057a7661dfad0a8e7d4f13b4e29f4c`。
- `04_Castle_Hall_Views_and_QA.zip`；13121061字节；Library版本1；SHA256 `1a5ab52ac4df2ddea1d565f14e281d050df207dd89132bd1ed159cc3a8bed12e`。
- `Castle_Hall_FullRoom_Inspection.jpg`；548478字节；Library版本0；SHA256 `44bdabd6b1ee11aa5f3130fb558b240f9ed49a20d302b27b38c358f1e1e69055`。

#### Library时间证据（不是聊天发布日期）
- `03_Castle_Hall_Textured_Blender.zip`：条目创建 2026-10-07T23:17:38.974867Z；最近修改 2026-10-10T03:58:56.391483Z；当前Library版本 1。
- `02_Castle_Hall_Textured_GLB.zip`：条目创建 2026-10-07T23:17:38.895665Z；最近修改 2026-10-10T03:58:56.400479Z；当前Library版本 1。
- `04_Castle_Hall_Views_and_QA.zip`：条目创建 2026-10-07T23:17:38.844886Z；最近修改 2026-10-10T03:58:56.588843Z；当前Library版本 1。
- `Castle_Hall_FullRoom_Inspection.jpg`：条目创建 2026-10-10T03:58:56.364741Z；最近修改 2026-10-10T03:58:56.364741Z；当前Library版本 0。

#### 待解决
完整围护与真实洞口已核验；后墙、门、天花为推定，源片匹配近似。
- 未取得逐次聊天发布的确切时刻；Library创建/修改时间不替代聊天发布日期。
- 不能确认所有中间发布版本均已恢复；缺失历史不重建、不补造旧提交。

#### 2026-10-10 逐场来源覆盖补充核验
- 解码未知；旧截图1188×761、裁图1188×668。
- 登录后采集：未知：未找到可关联该场有效帧的登录状态日志。
- 独立角度：近正面与小斜向约2族；C较宽正面不算独立标定基线。
- 新证据使用：旧3帧有最终overlay；未见登录后高清重采/新增图驱动修改证据。。
- 跨视频后续回放：未证实：已检查记录只有单个BV；同BV更晚时间不等于后续其他回放。
- 原生1080导帧未实现。总体来源验收仍待复核。详见 `scenes/castle-hall/source-coverage-audit-20261010.json`。

#### 本阶段计划路径（已传/待传见上方状态及 manifest）
- `scenes/castle-hall/02-retain-complete-geometry/assets/03_Castle_Hall_Textured_Blender.zip`；8279321字节；SHA256 `c8854932dc55bb8dc0a47e306a1b06d6af757eb6b7d0745eb96f4f012fdd0158`；Git blob SHA1 `6682184f0826b1d6ce823bddf80a8f5dadf54f63`。
- `scenes/castle-hall/02-retain-complete-geometry/assets/02_Castle_Hall_Textured_GLB.zip`；3826367字节；SHA256 `978f459d88eeba8fbaef36e01176d3dcf2057a7661dfad0a8e7d4f13b4e29f4c`；Git blob SHA1 `c43053a79ada160649e7bf1bbc2283a2d44ce9c8`。
- `scenes/castle-hall/02-retain-complete-geometry/assets/04_Castle_Hall_Views_and_QA.zip`；13121061字节；SHA256 `1a5ab52ac4df2ddea1d565f14e281d050df207dd89132bd1ed159cc3a8bed12e`；Git blob SHA1 `472eb610d8c8126ced2de1c1b633094ff659ceb1`。
- `scenes/castle-hall/02-retain-complete-geometry/assets/Castle_Hall_FullRoom_Inspection.jpg`；548478字节；SHA256 `44bdabd6b1ee11aa5f3130fb558b240f9ed49a20d302b27b38c358f1e1e69055`；Git blob SHA1 `5101389cf803ab4ad9c8771474de291e4d1d0ba1`。
- `scenes/castle-hall/source-scope.json`；2108字节；SHA256 `d37959cd0d0f3d957e6b1e376558fba002923c39ba3b51f710d5bd779f3025b2`；Git blob SHA1 `c1552d5f0d340cdc4add40538d55cca8849800e2`。
- `scenes/castle-hall/source-coverage-audit-20261010.json`；2079字节；SHA256 `0455157c7894ffa3dd8edfe5223053996ff011f9c098b339bf76d8efacbf6f8d`；Git blob SHA1 `cfaff912e2cdef3957dd784387e1728cb8591e91`。

#### 日期语义
- 03_Castle_Hall_Textured_Blender.zip：library_item_created_at=2026-10-07T23:17:38.974867Z；library_item_modified_at=2026-10-10T03:58:56.391483Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
- 02_Castle_Hall_Textured_GLB.zip：library_item_created_at=2026-10-07T23:17:38.895665Z；library_item_modified_at=2026-10-10T03:58:56.400479Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
- 04_Castle_Hall_Views_and_QA.zip：library_item_created_at=2026-10-07T23:17:38.844886Z；library_item_modified_at=2026-10-10T03:58:56.588843Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
- Castle_Hall_FullRoom_Inspection.jpg：library_item_created_at=2026-10-10T03:58:56.364741Z；library_item_modified_at=2026-10-10T03:58:56.364741Z。Library条目创建与最新修改事件；创建时间不等于当前版本发布时间，修改时间不是聊天发布时间。
聊天发布时间、原始模型制作日期及旧Git提交日期未获证实。新归档commit日期以实际执行时间为准。

共享标准：`docs/reconstruction-standard.md`。
本阶段是现有实物的候选快照归档；不是重新建模。
完整原始包未重打包、未改字节。
