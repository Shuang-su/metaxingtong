# 外环点阵表面有界实验，最终状态

当前有效实验是v3，四原件export/roof-led-surface-v3{,-white}.{blend,glb}及roof-led-surface-v3-recovery.json、scripts/restore_led_surface_v3_glb.py。R05、R06b、a055原件和生产引用不替换。

## 实际改动与来源范围

以a055为基线，275mesh顶点/拓扑/变换及可见性全同；仅既有外LED闭合环带的128外竖面新增圆周UV/材槽，两自生成PNG作为发光与暗底。原环其它384面、内圈、屋盖、云、旧6材节点、11相机、3灯和World均不变。另存1人工近景相机，共12cam，不冒第二来源角。

源11支持多行青白面状点阵这一表面类别。实际近景可辨连续带变近方点阵；没有来源证明作者1024列/4行、相位、强度、台高或曲率。全部参数是代理，后圈延续未知。source10近紫白带非同外环，现前半外带无顶点入画且跨相机平面，不能作第二角确认。

source11原位置错位/前缘中央出画、台盘过深、屋盖和云差异仍明显。当前SOURCE FAILED，无native/4K/timecode/完整场景验收。

## 正确纹理/强度与恢复

v3实际保存Emission Strength9.124373435974121。两个8192×256 PNG外文件、BLEND packed、材GLB bufferView逐字节同；精确SHA见textures-v2/pattern-recipe.json及独立pixels.json。GLB通过KHR_materials_emissive_strength保该强度，无外链buffer；白GLB不带图案是预期。

独立按sRGB解码全PNG，均值乘强度后约(.240293,1.699531,1.183783)，相对旧(.24,1.7,1.18)亮度加权比1.00000001006。只为均匀UV面积上的线性发光标量近等，不是RGB全分量相等/图像亮度恒等/实际功率。暗底Base Color也改变，不能隐瞒其视觉影响。

材白全部几何/UV相同；双GLB真空场回导全世界顶点双向最近误差0，外带世界位置+UV round5同；12cam归一化视框误差约4.01e-8。双factory-empty sidecar恢复275mesh/12cam/3AREA，World节点/链接exact。sidecar为本场必要恢复，不声称原生GLB完整存下World/AREA或跨软件图像无损。

## 图像与失败历史

当前仅2方向：source11和人工带近景，各材白32sample共4真实图，1192×671；不改灯、不去噪。白近景暗且有噪点，但环带边界可辨，无发光图案正常。保存默认8s，32s是明确执行覆盖，不改原件。

总12张原渲：2基线8s、2首横条失败8s、2v2错强度失败8s、2v3正确8s、4当前32s。另2source11原尺寸direct50和2三联是派生图，不另算视角/渲染。两direct50各2399496通道独立全数组误差0；三联六内容区0差，16图SHA/尺寸/字节全核。基线8s/当前32s不能据噪声差归因材质提升。

首256列图案真实成横条而拒绝。一次按原面度量改近方点后，v2误读首版recipe导致实际6.3347强度而非9.1244，完整四件/图/错误声明和独立失败证据留存。v3显式recipe/PNG SHA绑定，实际保存态核强度后重新渲染，未复用错误亮度图。更早v2输出路径错误也保留脚本/log，旧证据由Git原字节恢复无丢失。历史pending/错误描述以本入口和v3-correction为准，不静默重写旧文件。

所有独立源语义、技术与最终图像QA在sources/independent-semantics及results/independent-*。同轮公开补源仅coverage/review两文本，0新图，已合入sources/public-recap，不把旧视频失败包重复归档。
