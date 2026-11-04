# R07B 正式图像与恢复附录

制作图像冻结commit 57a69715173b9765101ff3d72b8b7f426638aa03。已逐图实看9张正式原图与6张直接50%叠图；检查未渲染、未改制作原件。

## 完整性和状态
- 9原图均1192×671：材3源+inspection05，白3源，以及R06/R07B同局部底视基线/候选两图。确切SHA、bytes、PNG模式及alpha范围在image-integrity.json。
- 实际6张全数组叠图均等于floor((原WebP解码RGB+渲染RGB)/2)，最大误差0，无warp/resize。9张原图RGBA alpha均恒255（全不透明），RGB按制作脚本直接convert('RGB')，非额外透明前景变形。
- 6张全尺寸横条三块全部逐像素等于source/render/overlay；底视左右对照扣除上方24px新增身份栏后，全部像素等于两原图横拼。
- comparison-manifest的18项SHA/bytes/尺寸全匹配；7条源图/主图render记录的模型SHA与实际B原件匹配。
- main-material.png与本次实际material-inspection-05.png字节完全同，不是R06旧图复用，也不另算角度。
- 底视渲前记录两版本相机矩阵/lens、4灯（原3+临时诊断补光）、World Background/Strength相同。诊断补光只用于该对照；源图脚本fresh load B原件，使用原3灯。材源64samples、白源32samples、底视32samples，无去噪。不把不同样本数称完全相同渲染设置。

## 实际像素结论
- 底视左侧外r6.01、右侧内r5.01的局部贯穿处改为低位面。左右仍有边缘明暗带、局部噪声，大部分画面是原台底。结合独立4/6三角质心全场首命中结果，只能证明该角有限部位可见，不证明全圆周或完整底面。
- source17材白仍有明显键顶过高、黑白分组/宽度节奏与来源不合；星纹和环层关系也不匹配。
- source20材白键底、琴盖斜率/位置/大小、周边环台仍明显偏离，主要构件被画幅截断；不能由新增桥认定来源改善。
- source21材白琴投影过大、键节奏、环弧/星纹与来源明显双影；媒体表观仍未恢复。
- 白源图依旧低对比和噪声，不是完整细缝检查。主图是有用的正面高斜模型总览，但外台边界与对称重复限制覆盖。
- 本轮不是8个新有效检查角：只有3个来源假设角、1个主视角和1个局部底视角（底视又含旧基线）。R06历史八角不可移称R07新八角。来源仍FAILED，隐藏桥仍推断，不是实际施工或承载结论。

## 新GLB场景恢复实际复验
两B GLB各从空场导入，再执行本版本restore_glb_lighting.py配render-sidecar-b.json，回存仅在独立QA目录restored-material/white.blend。World Background颜色/强度/Surface连接exact；原3 AREA参数exact、矩阵最大差1.19209e-7；12相机齐。1192×671/100%、active source21、Cycles64/no-denoise、AgX/view/exposure/gamma与对应保存BLEND一致。恢复输出包含164mesh，详见导入check-b与restore-check记录。不声称GLB原生保留AREA/World，也不声称跨软件渲染等价。CLI -t1下不认证保存线程数。

原始证据：images.py/log/image-integrity.json，restore_check.py/log/restore-check.json；技术与B相机见review.zh.md、b-camera-addendum.zh.md。四模型哈希均由实际读取绑定，源和图像不可替换后沿用结论。
