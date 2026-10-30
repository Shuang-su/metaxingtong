# Native-pixel residuals

B0 = 原几何/原机位；B1 = 原几何/r03 冻结机位；D1 = 实际共享剖面/r03 同一冻结机位；A2 = 仅数值 A 柱假设，未写入实体。点使用二维欧氏距离；风口外缘使用投影圆点到手动拟合椭圆的径向 RMS；线使用观测点至有限投影线段的二维距离 RMS。不是图像相似度或整体验收分数。

## 拟合锚与未拟合检查

D1 只拟合风口中心/外缘及台面上下转折。A2 单独拟合 A 柱下接点与内边线。镜子中心、顶棚下沿、门板上沿完全不参与本轮任何拟合；S04 排除。手动标记约 7–15 px 不确定性，3D 对应仍是代理假设。

## S01

| 特征 | B0 | B1 | D1 | A2 数值 |
|---|---:|---:|---:|---:|
| 风口中心 | 158.4 | 115.6 | 4.6 | 4.6 |
| 风口外缘 | 121.7 | 102.0 | 8.3 | 8.3 |
| 台面上转折 | 164.6 | 83.0 | 24.0 | 24.0 |
| 台面下转折 | 152.5 | 74.1 | 9.9 | 9.9 |
| A 柱下接点 | 19.6 | 106.5 | 106.5 | 41.1 |
| A 柱内边 | 173.6 | 215.7 | 215.7 | 126.0 |
| 镜子中心（未拟合） | 127.3 | 194.3 | 194.3 | 194.3 |
| 顶棚下沿（未拟合） | 279.8 | 249.8 | 249.8 | 249.8 |
| 门板上沿（未拟合） | 72.2 | 88.3 | 88.3 | 88.3 |

实际 D1 表面检查：

| 特征 | 实际检查 | 首个不透明命中 |
|---|---|---|
| dash_top_corner | blocked_by_other_object | P14_mirror_sail |
| dash_bottom_corner | blocked_by_other_object | P02_upper_belt |
| a_foot | visible_surface | D01_dashboard_top |
| vent_rim_0 | visible_surface | D03_vent_round_rim |
| vent_rim_1 | grazing_vertex_neighborhood_visible | 无中心射线命中 |
| vent_rim_2 | visible_surface | D03_vent_round_rim |
| vent_rim_3 | visible_surface | D03_vent_round_rim |
| vent_rim_4 | visible_surface | D03_vent_round_rim |
| vent_rim_5 | visible_surface | D03_vent_round_rim |
| vent_rim_6 | visible_surface | D03_vent_round_rim |
| vent_rim_7 | visible_surface | D03_vent_round_rim |
| mirror_center | visible_shape_center | P17_mirror_glass |
| roof_lower_line_0 | blocked_by_other_object | A05_passenger_visor |
| roof_lower_line_1 | visible_surface | A02_side_roof_rail |
| door_belt_line_0 | blocked_by_other_object | D01_dashboard_top |
| door_belt_line_1 | blocked_by_other_object | S01_visible_seat_outer_bolster |

来源中用于拟合的风口和台面转折可见；模型投影点若落在遮挡后，不构成有效可见对应。镜子在 S01/S03 可见、S02 无可用镜子中心。门板与 A 柱边线只使用人物外的可见段；角色遮挡区没有补建角色或完整座椅。

## S02

| 特征 | B0 | B1 | D1 | A2 数值 |
|---|---:|---:|---:|---:|
| 风口中心 | 141.1 | 97.9 | 11.6 | 11.6 |
| 风口外缘 | 115.9 | 88.1 | 8.8 | 8.8 |
| 台面上转折 | 190.9 | 80.1 | 26.4 | 26.4 |
| 台面下转折 | 175.5 | 73.2 | 1.4 | 1.4 |
| A 柱下接点 | 82.5 | 79.3 | 79.3 | 60.2 |
| A 柱内边 | 192.5 | 196.7 | 196.7 | 110.5 |
| 门板上沿（未拟合） | 25.2 | 89.0 | 89.0 | 89.0 |

实际 D1 表面检查：

| 特征 | 实际检查 | 首个不透明命中 |
|---|---|---|
| dash_top_corner | visible_surface | D01_dashboard_top |
| dash_bottom_corner | grazing_vertex_neighborhood_visible | 无中心射线命中 |
| a_foot | visible_surface | D01_dashboard_top |
| vent_rim_0 | visible_surface | D03_vent_round_rim |
| vent_rim_1 | grazing_vertex_neighborhood_visible | 无中心射线命中 |
| vent_rim_2 | visible_surface | D03_vent_round_rim |
| vent_rim_3 | visible_surface | D03_vent_round_rim |
| vent_rim_4 | visible_surface | D03_vent_round_rim |
| vent_rim_5 | visible_surface | D03_vent_round_rim |
| vent_rim_6 | visible_surface | D03_vent_round_rim |
| vent_rim_7 | grazing_vertex_neighborhood_visible | 无中心射线命中 |
| door_belt_line_0 | blocked_by_other_object | D01_dashboard_top |
| door_belt_line_1 | visible_surface | P02_upper_belt |

来源中用于拟合的风口和台面转折可见；模型投影点若落在遮挡后，不构成有效可见对应。镜子在 S01/S03 可见、S02 无可用镜子中心。门板与 A 柱边线只使用人物外的可见段；角色遮挡区没有补建角色或完整座椅。

## S03

| 特征 | B0 | B1 | D1 | A2 数值 |
|---|---:|---:|---:|---:|
| 风口中心 | 127.1 | 104.2 | 7.1 | 7.1 |
| 风口外缘 | 104.4 | 87.9 | 6.4 | 6.4 |
| 台面上转折 | 72.1 | 66.2 | 20.0 | 20.0 |
| 台面下转折 | 69.2 | 54.0 | 16.8 | 16.8 |
| A 柱下接点 | 89.3 | 95.3 | 95.3 | 32.7 |
| A 柱内边 | 193.7 | 215.6 | 215.6 | 136.5 |
| 镜子中心（未拟合） | 168.4 | 181.8 | 181.8 | 181.8 |
| 顶棚下沿（未拟合） | 205.9 | 230.9 | 230.9 | 230.9 |
| 门板上沿（未拟合） | 90.7 | 68.7 | 68.7 | 68.7 |

实际 D1 表面检查：

| 特征 | 实际检查 | 首个不透明命中 |
|---|---|---|
| dash_top_corner | blocked_by_other_object | P14_mirror_sail |
| dash_bottom_corner | blocked_by_other_object | P02_upper_belt |
| a_foot | visible_surface | D01_dashboard_top |
| vent_rim_0 | visible_surface | D03_vent_round_rim |
| vent_rim_1 | visible_surface | D03_vent_round_rim |
| vent_rim_2 | visible_surface | D03_vent_round_rim |
| vent_rim_3 | visible_surface | D03_vent_round_rim |
| vent_rim_4 | visible_surface | D03_vent_round_rim |
| vent_rim_5 | visible_surface | D03_vent_round_rim |
| vent_rim_6 | visible_surface | D03_vent_round_rim |
| vent_rim_7 | grazing_vertex_neighborhood_visible | 无中心射线命中 |
| mirror_center | visible_shape_center | P17_mirror_glass |
| roof_lower_line_0 | blocked_by_other_object | A05_passenger_visor |
| roof_lower_line_1 | visible_surface | A02_side_roof_rail |
| door_belt_line_0 | blocked_by_other_object | D01_dashboard_top |
| door_belt_line_1 | blocked_by_other_object | S01_visible_seat_outer_bolster |

来源中用于拟合的风口和台面转折可见；模型投影点若落在遮挡后，不构成有效可见对应。镜子在 S01/S03 可见、S02 无可用镜子中心。门板与 A 柱边线只使用人物外的可见段；角色遮挡区没有补建角色或完整座椅。

## 边界和稳定性

共享剖面：前缘 ΔY 0.09362；倾角 -26.93°；台面厚 0.09006；整套风口比例 0.65000（下限）；局部高度 ΔZ 0.07023。均为无实测尺度的模型单位。

A2 仅数值：下接点 ΔY -0.16211、单一弧度 -0.10000（下限）。S02 相机 pitch +0.06 rad 也到边界。未扩大边界，未添加逐点变形。

| 留出来源 | ΔY | 倾角 ° | 台面厚 | 风口比例 | ΔZ |
|---|---:|---:|---:|---:|---:|
| S01 | 0.09152 | -25.77 | 0.09184 | 0.65000 | 0.07097 |
| S02 | 0.09344 | -26.13 | 0.08637 | 0.65000 | 0.07215 |
| S03 | 0.09596 | -28.57 | 0.09098 | 0.65000 | 0.06668 |

留一来源试验仅检验冻结相机后的共享几何敏感性；相机先使用全部三图拟合，故不是独立验证。局部剖面数值变化有限，但三个试验全部撞风口比例下限；未拟合镜子/边线和实际遮挡问题未解决，整体不采用。
