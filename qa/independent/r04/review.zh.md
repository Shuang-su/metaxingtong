# R04 独立有限技术复核

绑定269bcec67b68fd83df4c53f2c2d591c265e560b0；四SHA见check.json，材质BLEND724e5ba89f95a27788ced16266f43936cdd373c5084b688653f707e53003e2a8。实际1线程只读双BLEND求值与双GLB空场回导，不渲染/不改生产。

材白162mesh/11camera，geometry/UV/visibility及相机完全相同。旧25负体积已消除，面积<1e-12面0；但stage-central-solid、stage-step-ring、inner-luminous-rim各4非流形edge。relations.json记录实际坐标及linkedface数，接缝有3-face边/中心1-face边，不能通过。两GLB全顶点双向nearest最大9.83e-7，media厚度丢失已修；原尺寸1192:671归一化camera frame误差见check.json。无材质贴图依赖，图像列表保留；尚未证明GLB灯/world等价。

代表接触：音板与琴体16BVH面交叠对，星地纹与台面241对；琴盖→琴体vertex-to-surface最近0但BVH0，属有限接触，不是铰链/承载证明。白键00/18→outer-floor仍约7.79e-6正隙，不称焊合。

对5个代表对象补了全场其余161对象AABB筛查（1e-4阈值）和所有邻候选实际BVH。白键00/18与各black-key00/18为11对，black-key00与pink-ring为15对，因此不能只因对floor微隙称白键独立悬空。音板和琴盖其他邻居结果见relations.json。AABB相离排除表面交叠和包含；AABB重叠且BVH0者标containment_not_tested，不把近表面上界当连续最短距离或无包含证明。本次不是全场支承图/碰撞验收。

未检查正式来源图/八角，来源FAILED。R04必须保留非流形失败，不据此宣称整模型通过。
