# R06b中央小云连续面实验：有限收口

独立实验分支 experiment/cloud2-relief-r06-20261105，R05原目录/文件/已归档历史不改，不自动推广为CURRENT或完整场验收。只将CLOUD_2的3线管代理换为1连续多瓣闭壳＋5嵌入卷纹，其余272物件、11camera、灯与World保持不变。两侧裁切大云未改。

来源10右完整云只提供手工设计家族轮廓/卷纹，11中央约129×59px只提供粗类别，实例对应未知。原像素描线与映射、技术收缩、背面/0.08模型单位厚度/浅起伏假设全留记录，无源贴图，无把明暗当孔。

## 实际交付
- models/roof-r06b-experiment.blend、roof-r06b-white.blend，同几何可编辑材白。
- models/roof-r06b-experiment.glb、roof-r06b-white.glb，必需roof-r06b-recovery.json与scripts/restore_r06b_glb.py。
- research-r06/roof-r06b-experiment-front-close64.png、roof-r06b-white-front-close64.png：相同人工正交近景、原灯/World、64samples无去噪。内卷纹可辨，但材图暗/白图对比低，不能叫源匹配改善。
- research-r06/source11-cloud-before-after.png与source10-cloud-before-after.png：原像素局部source/R05/R06b/白四格。
- research-r06/source11-r06b-direct50.png、source10-r06b-direct50.png：1192×671直接50%，独立逐像素误差0。
- R05基线、R06失败、R06b材白8samples来源/人工正侧近景和64samples后继均保留。不把R05旧八角冒称R06重渲或重新覆盖通过。

## 独立技术结果与边界
278材白mesh共享；双GLB实际空场回导278mesh/11cam，顶点/相机限定核验及双fresh恢复通过，AREA/World依赖sidecar。6新件封闭正体积、非流形等限定项通过。272旧物/11camera/灯World不变。

五卷纹与主体有真实BVH交叠，6436有限点射线命中主体。6新件与其余272件AABB全部不交，故本次无新增旁物交叠；不证明物理支承。自身无非共顶点BVH三角对，但相邻面折叠未穷尽，不冒完整自交证明。

R06初版重复端环开放与左小卷纹7顶点超主体投影已按真实失败留存；R06b另版焊环/封口，左小卷纹0.8局部收缩是技术内嵌假设，不是源槽精测。所有原失败脚本/日志/图均不覆盖。

仍SOURCE FAILED：实例未证、精确轮廓/内纹/颜色/位置不匹配、非native1192×671报道图且时刻未知，后续回放新角缺。仅“有面积多瓣表面＋内部卷纹”类别较原线管更合理，不能升级整个场景或用户验收。
