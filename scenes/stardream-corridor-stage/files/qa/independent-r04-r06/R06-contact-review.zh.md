# R06接触修复独立限定确认

实际载入R05/R06材白四原件，单线程、未渲染。精确模型SHA见R06-diff-check.json。

材白187mesh世界几何/UV及12camera/灯/world/可见性相同。仅8个wall_plate与2个handle改变；其余177mesh世界坐标/面列表完全同。所有UV、camera/灯/world/隐藏状态以及材质节点同R05。全部mesh非流形/退化/非正体积异常为0。

逐顶点实际差分：每plate仅墙侧24顶点localZ延长±.015，把手仅根端12顶点localZ延长-.045；其余端点和XY不变，各对象顶点数和面索引列表完全同，详见R06-local-vertex-diff.json。没有改bracket、rib、roof或假定来源灯位。

采用实际世界loop_triangles、全feature连续三角距离与BVH：
- 8plate→主墙最小表面距离全0，各48交叠面配对。
- 8plate→bracket仍全0，左26/右24对。
- 2handle→leaf全0，各24对。
- bracket→roof仍有原间隙，既有bracket→rib→roof几何链保持，不需误报直接相接。
针对全部plate/bracket/handle与全场mesh的BVH关系比较，仅新增对应wall/leaf对象，没有其它新交叠对象或旧关系删除。该对象集合检查不是相交深度/面积恒定，也不证明无包含、自交或其它物件间碰撞。

这是预期浅嵌合接触修复，不是Boolean焊合、机械承载力或来源真实安装结构。R02相机支撑线有限段/遮挡反例、灯位/身份和未知尺寸失败继续保留。R05旧渲染不能重新标作R06渲染；正式套图及R06新版GLB回导本轮尚未检查。

证据：R06-contact-check-with-rib.json、R06-diff-check.json、R06-local-vertex-diff.json，以及本目录对应实际脚本/日志。未修改生产Git或模型。
