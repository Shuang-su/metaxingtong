# 海滨 r02 独立有限技术 QA

输入为 seaside-arch-r02.bundle 独立clone HEAD9688dd54171b833bb642d268a174f0f8a1749911；四原件精确SHA在check.json。只读1CPU，无任何渲染/生产修改。本报告不替换r00/r01失败报告。

## 保存态差分与拓扑
与r01实际保存态相比，仅三上圆盘、两下圆盘matrix及伞柱局部顶点/matrix改变。其余132mesh局部顶点、面、UV、matrix、可见性不变；10相机全列参数/matrix与3灯不变。未把这些有限字段扩大为整个文件字节相同。

材白各138mesh/10camera，世界三角表面、UV、可见性与相机共享一致。所有单体非流形边、松边、退化三角为0，有向体积正。这不证明全场无自交/无重叠或真实结构正确。

## 伞连接实测
实际loop_triangles、float64全三角特征距离（含边穿面、点面、边边，AABB下界剪枝）：U01柱至8根U03骨、8片U02罩的最小表面距离全部0，并各有BVH表面交叠。与r01约.3017/.3098断链不同，本次保存态确已连接。柱与后apron关系保留；新增关系限上述16对象，未新增别的柱表面交叠对象。

这仅是几何相交接合，非Boolean焊合/承载/真实伞构造证明。伞罩与全部其他物件的完整包含、自交、全边界穿插未全面验收；不称整伞/整场无碰撞。三上圆盘/两下圆盘仍属不确定发光面代理，不能当真实窗孔。

原六金条与所属拱.0025000572间隙由r01实际下上界一致证明，r02这些顶点/变换未改，故仍保留，不能称装饰接合已过。大/小拱隐藏支承也未证；没有擅加脚或要求来源未见构件。

## 两GLB与实际恢复
两GLB分别factory-empty导入，均138mesh/10cam，全部世界顶点双向最近距离约1e-6以内，原生回导视框仅浮点差。相机比较画幅1192×671，不把仅bbox当全顶点核。

实际执行r02 restore.py双mode；重定向其JSON输出并在最后低分辨率预览/渲染段之前停止，保存独立restored-material.blend/restored-white.blend。未运行脚本最后预览，也不把当前报告说成新恢复渲染对照。

恢复后10相机matrix/view-frame差0，lens/type/sensor fit/width/height/clip/shift/ortho scale全部相等；1192×671/100%/pixel aspect/sample/denoise/active camera、view transform/look/exposure/gamma与display相等。World实际Background节点输入及Surface链接一致。3AREA属性完全相等，矩阵最大浮差5.96e-8。原BLEND无外部链接库、无FILE型贴图依赖。

注意sidecar虽记录cycles，当前restore仍写死samples32/no-denoise；对当前冻结保存态实际相等，不是可任意改变cycles后都自动恢复的通用证明。没有检查每个Cycles隐藏选项/所有shader渲染等价，GLB原生也不支持AREA/World，结论仅上述实测参数经sidecar恢复。

## 图像与来源状态
本轮只技术，不重渲、不提前计20图齐套或8有效角。r01已中断长套及6张完成失败CHECK保留；不能当r02图。之后正式r02图需另按实际原件/执行态/hash/直叠核。源03/04非原生、近正轴、遮挡后推断、不同态合演未混等限制均不变。技术修链不能替代来源吻合，SOURCE仍FAILED。
