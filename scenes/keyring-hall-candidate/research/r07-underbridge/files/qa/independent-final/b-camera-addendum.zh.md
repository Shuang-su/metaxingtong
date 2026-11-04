# R07B 相机与原件附录

冻结commit 81d1ee6c93730ff3a5bff9974bef8e7e4348a449；四件精确SHA见check-b.json。材质BLEND 8bf0d5036babd6db0a0fbd3c19ea020b38b1e6136156342355c136a284c645ee。

实际读取A/B原件：164mesh局部顶点/面/UV/材质引用/矩阵/可见性完全同；原11相机不变，只有diagnostic-underbridge-fixed变化。位置约(5.01,0,-1.2)、lens28mm、sensor36，准确矩阵存diff-b.json。两B材白共享几何UV可见性及12相机完全同。

两B GLB分别清空场景真实回导164mesh/12cam，所有世界顶点双向最近点误差≤9.83025e-7，归一化视框误差≤3.69116e-8；材质版12相机完整矩阵最大差4.17233e-7。绑定B新哈希，不将A导出代替B。

独立对两桥实际底面三角质心投影，并用全场scene.ray_cast检查首命中：内桥4个入画/4个首中自身，外桥6个入画/6个首中自身。证明这10个局部样点可见，不证明完整两环可见，更不作为全周验收。

已实际看preview-b-baseline.png与preview-b-candidate.png。两侧局部窄带由透漏变低位连接面，中部主要仍为原台底，40%低采样图噪声明显；不能仅看此角断言全底面正确。正式图尚未在本附录核验，另候完成再核。几何相同使A的有限接触/射线结果可用于B几何，但A失败可见性不沿用。

记录：check_b.py/check-b.json/log，diff_b.py/diff-b.json/log，visibility_b.py/visibility-b.json/log。仍为推断结构、来源FAILED，无施工或承载结论。
