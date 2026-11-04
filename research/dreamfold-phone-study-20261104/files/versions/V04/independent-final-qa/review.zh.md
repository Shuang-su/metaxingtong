# 手机V04保存态、导出恢复与正式图独立QA

制作首冻结f9952dc05740d34816ffe8950b1875979c1ddd2c，路径dreamfold-phone-study-20261104/versions/V04。四原件精确SHA见check.json：
- material.blend a1548dd671f8dc563fb38f7266075449d61f6d954e97f0f62058ae909a0e6fa7
- material.glb 2a77d6fc1cac33ddb90698bc32376429c8a6d39e3619a659d1863626363c7193
- white.blend d6955d766413db2d801cc04836869fcdba98fe78cf5b9be2390cb56e2c427d8e
- white.glb 4f6113bfc94d6b8ff7d67d53798708e9dd0fc4451da549d94f08c31af01362b7

全部只读1CPU实际核验，恢复回存仅在本QA目录，未修改制作原件/重渲。

## 保存态和接触
与V03同变体实际比较：只有P04世界顶点改变，10件局部顶点/面/UV/材质节点完全同；原5相机/灯/World完全同。P04保存矩阵与独立45°构造最大差5.96046e-8。材白10mesh世界几何、三角、UV、可见性完全一致；全部0非流形/0退化/正有向体积。

保存态重新构造真实loop_triangles BVH：P04→主壳16对、→轴78对，其他7件表面交叠0；材白结果相同。此处没有把内存试验hash当保存态hash。已完成的扫描包含检查属于先前独立报告，保存态本轮只复验上述相交集合；不将0表面相交扩成全体无包含/无碰撞。轴连接是推断装配，不是工艺/承载验证。

## 两GLB实际空场回导与fresh-world恢复
每个GLB从空场真实导入10mesh/5cam，全顶点双向最近点最大1.68587e-7；5相机矩阵最大2.10600e-7、1080×603归一化视框最大5.96046e-8。不是bbox单一检查。

随后按本V04 sidecar和restore-state.py执行真实恢复，独立目录保存restored-material/white.blend。World节点色/强度/连接exact，render与view参数exact，导入几何未被恢复脚本改变。恢复相机/灯矩阵并非逐位exact：最大分别9.68575e-8、5.96046e-8，其余记录参数一致，属于已报告浮点重建差而非遗漏灯/相机。不称GLB原生含AREA/World或跨软件渲染等价；CPU线程被本次CLI-t1覆盖，不认证保存线程值。

## 正式4图及2叠
已实际逐图看material/white source7和side，另看2直接50%。均1080×603，16samples/no-denoise；源相机与side均实际保存机位，不把四图说成四独立角或8角。6图manifest的SHA/bytes/尺寸/mode/alpha_bbox全部实核一致；4渲前记录的原件SHA和相机矩阵/lens与相应保存state匹配。

两叠全数组等于：RGBA先alpha composite到黑底，再与原source7 RGB逐像素floor((a+b)/2)，最大误差0，无warp/resize。透明黑背景不是场景恢复。

源视图中后侧中段边局部改善，白模仍亮且细线低对比；side显示推断楔形与轴，未见新增明显断开，但有噪声与遮挡。未知后片底角、后侧完整轮廓和厚度没有来源约束，前片底缘/镜头细节/材质误差仍在。单条边的45°条件选值不是真实折角恢复；完整来源保持FAILED。

结论：有限增量保存/导出技术无实质阻塞，可归档为条件候选。不得把本轮局部轮廓改善升级整机/真实型号/功能面/底部接地/整场验收。

证据：check.py/json/log（含所有非exact浮点差）、saved_check.py/saved-check.json/log、images.py/image-integrity.json；先前扫描报告independent-phone-angle-scan-qa-20261104另保留。
