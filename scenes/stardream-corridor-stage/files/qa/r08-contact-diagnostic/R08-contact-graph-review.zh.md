# R08 完整网格表面接触图（独立后续诊断）

绑定材质BLEND SHA256 f836768fd9f233241d8b4c19b3862575e178713abb0caa1193a67268b1e32def，只读，无渲染/修改。

187mesh全部无序物体对先用真实世界顶点AABB最小分离下界筛选；下界≤1e-6才检查实际loop_triangles、BVH并运行连续三角全特征最短距离。将表面距离≤1e-6定义为一条图关系，保留精确距离与BVH面交叠数，不把bbox重叠直接作连接。结果395条关系，3个连通组：183物体主组，正端DOOR_leaf_1+DOOR_handle_1两物体组，负端DOOR_leaf_-1+DOOR_handle_-1两物体组。

395关系中21条距离严格正但仅5.96e-8至2.38e-7，属于本轮明确容差范围，不声称精确零。将这些全部去除后重算严格零距离图，组大小仍183/2/2，门组孤立结论不依赖1e-6阈值。

门叶/把手只在彼此组内，尚未有表面连接至墙、地、顶或soffit。这是保存几何的结构诊断，不把门叶设计净空直接判为错误或真实物理悬空，也不构成添加未观测铰链的来源依据。

所有8灯具finial、roof、lower_tip均有表面连接至有限房壳。最短路径可能经过diffuser，因此另外禁止经过任何diffuser重算，24个被检查构件仍都有经金属rib/bracket/plate等的路径。例：LANTERN_1_0_lower_tip→bottom_ring→rib0→bracket→wall_plate→WALL_side_1。此为几何路径，不是机械接头/承载通过。

另48个AABB候选经实际三角距离排除，全为各灯diffuser与6根rib的表面间隙，距离0.00092605196704–0.000926590677525，不得将bbox候选误计成接触；它们不破坏上述其他连接路径。

局限：以对象为图节点，多连通分量对象（R07两段横梁）在同节点内不表达内部连通性，本图不能代替分量级拓扑图。本轮表面关系图不把完全包容自动当表面接触，未做全体积布尔/交叠深度/全部面自交/现实力学验收。183主组连通不证明所有结构无缝或尺寸正确；来源仍FAILED。原20灯安装组件和标牌问题的逐项修复已另报告，不以graph拓宽验收。

证据：R08-contact-graph.json、R08-contact-graph-paths.json、R08-contact-graph-zero-sensitivity.json、check_graph.py/graph.log。paths文件区分all_geometry与exclude_diffuser，终点限定有限墙地顶/soffit，不把装饰batten当最终房壳。
