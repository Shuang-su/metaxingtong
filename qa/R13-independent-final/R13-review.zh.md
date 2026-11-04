# R13实际原件及图像限定复核

结论：六组瓶帽接地修正技术通过限定检查，来源仍FAILED。不是完整桌面物件或完整场景验收。

## 原件哈希
- R13_material.blend SHA256 9043baa184c0a25d96ecaa15c1bfbe983aa455edf988afcee758bffa8315ed64
- R13_material.glb SHA256 094b448d6fed61bd8dfe8b97d5500dda568ea4af379347205e44344b5729044e
- R13_white.blend SHA256 3d1395f39640a05b151f8a62f5308697848b23d5faf6d096868fbae97a2a40f0
- R13_white.glb SHA256 d558a6ee01c275375dea96db64b61b8368948e5cbe1d92acb101354d2ff27519

## 实际保存态
- 两版236mesh/9cam；仅瓶3–8及自有帽12物件世界Z下降，XY精确0变化，局部几何/拓扑/UV不变。Z差约-.0028，实际浮点范围记录在R13-saved-transform-check.json；不冒称每一world浮点位完全相同增量。
- 其余224mesh世界表面精确不动，旧8cam/灯/world/旧可见性不变，仅增加DIAG_relocated_bottle8_mount。没有隐藏旁物。
- 全单体非流形/退化0、正体积。材白直接索引hash继承旧球体排序差异，实际世界顶点/三角/UV关联多重集236项全部精确相同。
- 全17瓶对有限TABLE_top逐一连续三角距离实测：0–11、13–16共16瓶距离0，每件32BVH面交叠对；12号距离0.0024999380111694336、无交叠。没有按历史阶段数量相加得出16。
- 六组body-cap连续距离全0。全部其他物件纳入关系检查，新增仅桌面；4/5瓶虽AABB相交，连续表面距离.022361311569990074，双向全部顶点solid-angle winding约0，排除互含。其他非自身帽/桌面的候选严格AABB分离。接触不是焊合/承载证明。
- 两新GLB真实空场导入各236mesh/9cam，世界双向最近顶点最大4.76837158203125e-7、1192×671归一化视框最大5.960464477539063e-8。新旧packed图像SHA与GLB内嵌图像字节SHA一致，UV不变；人工设备示意纹理不升级真实网孔。

## 六张图像实际检查
六张全部逐图实看，原记录SHA/字节/1192×671/模型SHA全部匹配，64samples/no denoise。两张R12微距是历史基线；四张R13为TABLE_high材白和瓶8底部微距材白，当前只有两个人工诊断方向，不是六源角，也未重跑旧八角。

TABLE_high维持布局；近侧最外瓶底边裁切、镜内反射、材噪声和白低对比仍在。微距R12瓶8黑底缝明显，R13此局部缝收口；两侧珠体遮挡、瓶身/帽出画、粗分面与噪声保留，因此不能凭单瓶局部证明六瓶整周或所有道具接触。

12号瓶旧浮起/钟附近干涉、箱/钟/珠串对桌缺口未改。所有瓶的来源身份与数量对应仍未证。局部技术接触不替代多源和逐对象来源验收。

## 证据
R13-diff-check.json、R13-saved-transform-check.json、R13-saved-contact-check.json、R13-shared-surface-check.json、R13-glb-projection-check.json、R12-R13-image-integrity.json及脚本/log。
两只读脚本最初输出同名，本次将变换证据另存R13-saved-transform-check.json，再真实重跑接触脚本恢复独立R13-saved-contact-check.json，最终二者均保留，非删除失败或生产文件。未渲染/未保存模型/未写生产Git。
