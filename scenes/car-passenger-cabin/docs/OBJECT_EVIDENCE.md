# 逐物件证据与状态表

共 45 个稳定对象 ID；重复实例逐行列明。位置/朝向以 BLEND 中对象坐标和父节点为准，源相机及关/开状态在 render-manifest；无实测尺度。S01 2190.197282、S02 610.828893、S03 2968.842253 均为同 BV 原生 1920×1080。S04 605.763813 仅上下文，不增添未证实驾驶台部件。

所有可见物件的“来源证实”仅限其存在/可见局部，不表示模型轮廓已经对齐。共同属性判断：尺寸/背面厚度/材料参数/完整连接全部推断；源相机、遮挡后轮廓、精确比例与材质照明仍待查。局部开口射线与网格闭合检查见 QA；它们不是来源验收。

| ID / 实例 | 证据帧 | 来源可支持的局部/分类 | 厚度、进深、支撑与隐藏范围 | 比对状态/残差 |
|---|---|---|---|---|
| B01_inferred_floor_boundary | S01,S02,S03 | 未见构造，研究所需的推断 | Unseen finite floor support and scope boundary, not measured full floor | 不作为来源实测；仅检查本地闭合/承接 |
| B02_sill_fixed | S02 | S02门槛局部可见，其余支撑范围推断 | Open-door sill visible in S02; cross-section/extent inferred | C06；有限边界不是完整底盘 |
| B03_front_footwell_back | S01,S02,S03 | 未见构造，研究所需的推断 | Unseen local footwell closure, not full firewall | 不作为来源实测；仅检查本地闭合/承接 |
| A01_fixed_A_pillar | S01,S02,S03 | 柱、局部顶棚/遮阳板、窗口回边可见 | YZ outline approximate; thickness/back inferred | C02/C07；倾角、视野占幅及截面未标定 |
| A02_side_roof_rail | S01,S02,S03 | 柱、局部顶棚/遮阳板、窗口回边可见 | Visible surface approximate; backside and thickness inferred | C02/C07；倾角、视野占幅及截面未标定 |
| A03_partial_headliner | S01,S02,S03 | 柱、局部顶棚/遮阳板、窗口回边可见 | Visible roof patch, inferred cap thickness and trimmed left/rear boundaries | C02/C07；倾角、视野占幅及截面未标定 |
| A04_partial_rear_window_return | S01,S02,S03 | 柱、局部顶棚/遮阳板、窗口回边可见 | Right edge/window return visible; not a complete B pillar | C02/C07；倾角、视野占幅及截面未标定 |
| A05_passenger_visor | S01,S02,S03 | 柱、局部顶棚/遮阳板、窗口回边可见 | Visible surface approximate; backside and thickness inferred | C02/C07；倾角、视野占幅及截面未标定 |
| A06_visor_support_inferred | S01,S02,S03 | 未见构造，研究所需的推断 | Attachment support unobserved | 不作为来源实测；仅检查本地闭合/承接 |
| A07_windshield_lower_return | S01,S03; S04 conditional | 柱、局部顶棚/遮阳板、窗口回边可见 | Only right-side connection constrained; broader forward association conditional | C02/C07；倾角、视野占幅及截面未标定 |
| D01_dashboard_top | S01,S02,S03 | 仪表台右端/圆风口可见；精确截面未证实 | Visible surface approximate; backside and thickness inferred | C01风口中心/比例仍有残差；不外推完整仪表台 |
| D02_dashboard_end_fascia | S01,S02,S03 | 仪表台右端/圆风口可见；精确截面未证实 | Visible surface approximate; backside and thickness inferred | C01风口中心/比例仍有残差；不外推完整仪表台 |
| D03_vent_round_rim | S01,S02,S03 | 仪表台右端/圆风口可见；精确截面未证实 | Visible shape approximate; unseen thickness/back inferred | C01风口中心/比例仍有残差；不外推完整仪表台 |
| D04_vent_recess_wall | S01,S02,S03 | 仪表台右端/圆风口可见；精确截面未证实 | Visible shape approximate; unseen thickness/back inferred | C01风口中心/比例仍有残差；不外推完整仪表台 |
| D05_vent_recess_end | S01,S02,S03 | 未见构造，研究所需的推断 | Deep unobserved cavity termination; front aperture is not filled | 不作为来源实测；仅检查本地闭合/承接 |
| D06_vent_louver_1 | S01,S02,S03 | 仪表台右端/圆风口可见；精确截面未证实 | Three approximate visible louvers, depth inferred | C01风口中心/比例仍有残差；不外推完整仪表台 |
| D06_vent_louver_2 | S01,S02,S03 | 仪表台右端/圆风口可见；精确截面未证实 | Three approximate visible louvers, depth inferred | C01风口中心/比例仍有残差；不外推完整仪表台 |
| D06_vent_louver_3 | S01,S02,S03 | 仪表台右端/圆风口可见；精确截面未证实 | Three approximate visible louvers, depth inferred | C01风口中心/比例仍有残差；不外推完整仪表台 |
| D07_lower_dash_local | S01,S02,S03 | 仪表台右端/圆风口可见；精确截面未证实 | Visible lower right corner only; hidden continuation approximate | C01风口中心/比例仍有残差；不外推完整仪表台 |
| P01_door_carrier | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Outline inferred through character occlusion; thickness/back unobserved | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P02_upper_belt | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | YZ outline approximate; thickness/back inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P03_woven_upper_insert | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Woven strip visible at left/right; middle correspondence occluded | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P04_padded_mid_panel | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | YZ outline approximate; thickness/back inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P05_armrest_woven | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Armrest visible in fragments; curvature/hidden span inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P06_armrest_edge | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Visible light edge; cross-section inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P07_handle_recess | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Small dark pull region; exact handle mechanism unknown | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P08_pull_handle | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Approximate pull, not verified mechanical assembly | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P09_pocket_base | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Visible surface approximate; backside and thickness inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P10_pocket_outer_wall | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Visible surface approximate; backside and thickness inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P11_pocket_end_1 | S01,S02,S03 | 未见构造，研究所需的推断 | Pocket end closure inferred, opening remains above lip | 不作为来源实测；仅检查本地闭合/承接 |
| P11_pocket_end_2 | S01,S02,S03 | 未见构造，研究所需的推断 | Pocket end closure inferred, opening remains above lip | 不作为来源实测；仅检查本地闭合/承接 |
| P12_side_window_glass | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Window aperture observed; whether glass is raised, exact transparency, thickness and IOR inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P13_window_frame_1 | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Continuous frame around genuine glazed opening; profile inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P13_window_frame_2 | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Continuous frame around genuine glazed opening; profile inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P13_window_frame_3 | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Continuous frame around genuine glazed opening; profile inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P13_window_frame_4 | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Continuous frame around genuine glazed opening; profile inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P14_mirror_sail | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | YZ outline approximate; thickness/back inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P15_mirror_stem | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Visible stem attachment; cross-section inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P16_mirror_housing | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Visible outer contour approximate; rear profile inferred | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| P17_mirror_glass | S01,S02,S03 | 局部门板/窗/镜存在；中部被角色遮挡 | Black reflective appearance; environmental reflected content not reconstructed | C02-C04/C06；开门54°为推断，镜位置及门板比例未对齐 |
| S01_visible_seat_outer_bolster | S01,S02,S03 | 来源右侧有限座椅边缘 | Narrow right visible seat edge only; complete cushion/back/headrest deliberately absent | 完整座椅与安装结构未见；C05条件性裁切 |
| S02_seat_edge_piping | S01,S02,S03 | 来源右侧有限座椅边缘 | Visible side border approximate; not full seat perimeter | 完整座椅与安装结构未见；C05条件性裁切 |
| M01_partial_interior_mirror | S01,S03 | S01/S03左上角仅见部分室内镜 | Visible cropped interior mirror; full placement and support uncalibrated | 完整边界/安装位置未标定 |
| M02_interior_mirror_glass | S01,S03 | S01/S03左上角仅见部分室内镜 | Visible surface approximate; backside and thickness inferred | 完整边界/安装位置未标定 |
| M03_mirror_support_inferred | S01,S03 | 未见构造，研究所需的推断 | Unobserved support inferred; final support connects to headliner, no mechanical match claim | 不作为来源实测；仅检查本地闭合/承接 |

## 材质/遮挡逐属性结论

- 门板深色软包、编织状纹理、浅色边线：来源可见；编织频率、粗糙度、纹理方向与被遮挡部分是近似。不是源纹理提取。
- 侧窗是透视外部环境的开口；本模型薄玻璃为介质假设，玻璃是否升起/光学厚度/反射参数尚未确认。白模中它故意为白色诊断材料，不能据此判定实心封窗。
- 风口圆边、暗凹腔及叶片可见；黑暗并非量化深度依据。实际布尔孔、孔壁深度、背板和叶片倾角均应区分已见与推定。
- 门槽开口来源只部分可见；本轮采用真实可容积槽体，背部接缝、深度及端壁未知。
- 门铰链的前端位置和54°开角是机械合理性假设；源图只能确认开/关两个不同时间状态，没有测出轴线或完整运动。
- 座椅只做边缘片段；不利用角色遮挡补身体、靠背、坐垫、腿或未知安装件。
- 中性灯、外部空背景、镜面黑色和顶棚织物参数不是夜景复原；所有源机位共用同一套材料与灯光。

## 核查角色与缩放

源图保留原字节；qa/object-crops 提供原生同坐标 source/render/overlay 裁切，不移动裁切中的物体。renders/source/*comparison_panel.jpg 是 480 像素宽展示缩放，不能当原生源或额外机位。角色与字幕等源有内容不删改；来源未标定，不能把遮挡区的空白渲染当精度通过。
