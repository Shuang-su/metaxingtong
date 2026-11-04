# 手机V03相机保存及恢复状态独立复核

仅技术/复现增量，无新渲染，不改变V02来源FAILED/隐面推断结论。

## 实际四原件
- material.blend SHA256 ab9fcb7e32dfebffa222e474a41ed3d728d0222b5a6bf9af5483a049ad8de31d
- material.glb SHA256 aa0503c01401aebbe49779e3210c91dc2b480d702c4fd997d2f759e55d370e0a
- white.blend SHA256 327aa2447e5e3b94461b3a7a9596872d22af47da736eff44fd7fe74f86a36cf9
- white.glb SHA256 407568da8207ca16e0e36ae55aa552d7c5a2d99964255e35fb3bc4817ec4c114

## 新相机与导出
- 两BLEND各10mesh/5camera；与V02相同版本逐项比较，世界/局部坐标、面、UV、材质节点、灯、world、来源相机、画幅及色彩状态均相同。仅增加4诊断相机。
- 从V02真实几何bounds独立重算已渲诊断recipe，4保存camera matrix误差均0、lens48同；5张复用图SHA全部匹配。是复用V02实渲，不称V03新渲或补了白模图。
- 两GLB真实空场回导各10mesh/5camera/0light；全顶点双向最近误差最大1.6858739115832577e-7。统一1080×603后，5个原生回导相机归一化视框最大5.960464477539063e-8。
- glTF不原生保留这两AREA灯与World。需随附BLEND和对应scene-state JSON/restore脚本，不声称单独GLB完全等照明。

## 发现并纠正的恢复失败
首次实际执行restore，原World nodes Background为(.05087608844,…)/Strength1，但侧车仅world.color=.22，恢复后Background变.22。明确是有效照明不同，非仅节点排序差。原失败机器证据pre-fix-world-failure.json、restore-state-failed-snapshot.py和初轮log保留；制作方另保留failed-world-state-attempt。

修正后重新空场导入两GLB并实际执行新restore，World节点类型/值/连接与原BLEND全部相等，恢复后的画幅/色彩状态相等，导入mesh未改。相机归一化视框精确相同；赋回矩阵有最高约9.69e-8浮点差，灯矩阵约5.96e-8，能量/色/形状/尺寸相同，不能写matrix字节精确恒等。修正后没有因恢复成功冒称已渲出新图。

## 保留范围
来源单平面条件拟合、后片过宽/底缘失配、材质近似/粒子遮挡、厚度折角/背面推断仍全部保留。V01低残差wrong-side、V02四角坐标分量RMSE5.222875与欧氏点RMS7.386261的区别不改。

此处仅相机/几何/状态技术复现核，不是完整场景、新的来源角度或来源验收。详尽V02图像和接触结果另见independent-dreamfold-phone-v02-qa-20261104/review.zh.md。

证据check.json、recipe-check.json、check-world-fixed.log及脚本；无重渲、无生产模型/Git改动。
