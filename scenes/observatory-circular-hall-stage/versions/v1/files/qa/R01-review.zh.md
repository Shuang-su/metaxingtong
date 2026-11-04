# R01 初结构独立只读检查

仅针对 HEAD 00865fbd2906aad54c183e287cd2659412e0aad4 的R01冻结文件，Blender4.3.2单线程实际打开/回导，无生产写入、无渲染。
材质BLEND SHA256 70bb243aa9febd00efd8500e02ea50e190983da3a32e213cbd78194e0a68c66f；白模8ad57605315098eb6492c1f6cf880c80d6b549895674af284964d421c7d6fbc8。

- 202mesh全部材白世界顶点/面索引hash相同，13相机matrix相同，未隐藏render mesh。
- 全202单体非流形边0、signed volume正。但DOOR_00_gold_arch、DOOR_06_gold_arch、TERRACE_portal_01、TERRACE_portal_03各2面积<1e-12退化面，技术FAILED。arch复用闭环frame产生脚底共线带；另外两同构portal不能因数值阈值未触发就证明其语义面有效。建议构造真正U形边界挤出，保留R01失败。
- 实际壳体三角BVH：10窗中心三个高度共30射线均通，支持这些采样位置的真孔，不是贴假窗口。两门z1/2.5/3.9共6射线通；z.48两射线被连续下墙圈挡住，门底有.16高门槛假说。不能说一直敞到floor top=.4。
- 12墙缝方向×5高度=60径向射线及24方位×4半径=96向上屋盖射线都命中壳实体。只是代表点未见穿漏，不证明连续全壳无缝，也未全量碰撞/自交/接合检查；单体闭合不等于整体封闭。
- 材白两GLB均真实导入空Blender，202mesh/13camera名称齐，世界顶点双向最近距离最大1.1921e-7；camera matrix最大4.7684e-7。使用同1192×671画幅实际view_frame归一化射线最大误差1.1921e-7。最初直接比angle_y得到.14297rad差，原因比较未考虑sensor-fit/画幅语义，该数不作为投影失败结论，初JSON和后续同画幅复核都留存。
- 此轮GLB检查不证明完全相同三角拓扑、材质渲染等价或所有依赖。未独立实看生产预览，此轮无逐源像素验收；12bay/尺寸/4外brace及全部相机均条件假说。来源FAILED，不升为完成版。

证据：R01-check.json、R01-glb-check.json、R01-glb-projection-check.json及相应实际脚本/log。R02/R03不在本报告范围。
