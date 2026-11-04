# 观星台 R08 外景条件相机候选独立 QA

结论：只改SOURCE_15_exterior的条件姿态，局部构图改善，但没有真实校准或来源验收。仍用原18mm，未选择最低训练cost的12mm；12mm前拱回归和35mm试验历史应保留。

## 实际四原件
R07→R08全部215mesh世界顶点/面、全部UV、材料节点、灯/world/hide不变；只有SOURCE_15_exterior相机矩阵改变，其他12机位不变。材白几何/UV/13相机/灯/world/hide一致。基本拓扑未出现非流形/退化/非正体积异常。实际保存材白18mm矩阵对条件解float矩阵max2.5332e-7；25诊断点投影对计算值max0.00019831px，不借用试验模型hash。
两GLB各空场景真实导入215mesh/13cam，无缺失/新增，世界顶点双向最近最大5.3312e-7、camera矩阵4.76837e-7、1192×671归一化视框方向1.19209e-7。非全属性/渲染等价证明。

## 前拱与门洞有限诊断
固定18mm条件相机、不改任何标点/几何，最近有限线段距离：L10外前拱mean5.3095/max16.0537px，L11内前拱10.3345/18.7148px；L09主洞外墙开口边8.6103/14.6246px。均不达到标注主观误差范围，仍FAILED。L08外深框和L07缺高装饰拱不混入。
25个最近边投影对应点用透视正确权重还原world，再从相机向该world点对完整场景ray：目标前1e-4距离内未撞到更近物体。只证明这些离散模型对应点无检测到的前遮挡，不是沿原源像素ray、不证明源身份、不证明整条弧全可见。门脚仍未观测，未外推。

## 正式四图与叠图
实际逐张查看两R07基线+两R08当前材白SOURCE15图，均1192×671、记录64samples/不降噪。四图完整解码、SHA/bytes/尺寸及绑定模型SHA全匹配；四direct50均实际查看，全RGB按记录floor((source+render)/2)复算差0，源/渲染/叠图SHA全部一致，无warp/resize。不能把四图称四个来源角，只有一个来源机位的两版本/材白。
相比基线，当前墙体与前拱大轮廓更近，但屋尖肩部/屋顶曲线与檐层仍明显不同；窗数、装饰层、高拱、深门框和外部撑臂形状/位置缺失，白图低对比和透过门洞的室内结构仍有偏差。底部平台出画范围变化明显，不能说所有结构都改善。

## 原件SHA
- R08_material.blend `7d968ac26610c7a6284b679a9fffcdcd43e63377b8487e7433f79709fa89d8e2`
- R08_material.glb `72ccf811166a0b2f2884fc98ece3a596759f983e59e0c7cf4573e343c93072eb`
- R08_white.blend `8fba6666e514d432b7d3be701fc314c65cafa01803a68d000f26b0d9864c182d`
- R08_white.glb `4870129238ff018ad979e23506c68e5cb47adc4ecb264f5b2d5c338ff545c60a`

证据：R08-diff-check.json、R08-glb-projection-check.json、R08-saved-camera-check.json、R08-image-check.json、trial18-correspondences.json、trial18-visibility.json及脚本/日志。初轮投影/凸包来源检查见camera-fit-review.zh.md；main guard风险已重读确认修复。source15仅报道截图，非原生帧、确切片内时间未知，条件机位绝不等于新场景或完成验收。
