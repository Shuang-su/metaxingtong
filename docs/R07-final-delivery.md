# 红月洞屏海景舞台：R07 原件重制交付记录

**状态：有限后半舞台条件候选；来源验收未通过、用户未验收；本轮新场景计数为0。**

这是旧原件缺失后的新制作，不是恢复旧R10/R11 SHA。全程本机 Blender 4.3.2，初始1线程、资源释放后2/6线程；未新建或续派云端Codex建模。当前无Blender连接器可用，使用该云电脑已安装Blender。授权普通Git与临备不等待重复逐条批准。

## 实际文件
- [当前材质原模型](../models/R07_material.blend) / [白模原模型](../models/R07_white.blend)
- [材质GLB](../models/R07_material.glb) / [白模GLB](../models/R07_white.glb)
- [原件大小、SHA256及Git blob](../models/R07-artifacts.json)
- [主图](../renders/final-R07/R07_MAIN_material.png)
- [8个内部检查角总览](../renders/final-R07/R07_EIGHT_CHECKS_display.jpg)（对应8张1200×800原图；不是新增来源）
- [三源材质直接50%总览](../renders/final-R07/R07_three_material_direct50_display.jpg) / [白模直接50%总览](../renders/final-R07/R07_three_white_direct50_display.jpg)（明确展示缩放）
- [原生同尺寸源/渲染/六张直接50%清单](../renders/final-R07/native-comparison-manifest.json)
- [15张渲染与6叠图实际像素、模型SHA读回](../renders/final-R07/delivery-readback-validation.json)

正式渲染15张=三源材白6张+主图1张+8检查角。两P1输出1920×1080，P2输出3840×2160；六直接叠图在相同原尺寸直接 `Image.blend(sourceRGB,renderRGB,0.5)`，逐像素读回相等，不裁切/平移/warp。每张渲染旁JSON绑定当前BLEND SHA、相机、实际尺寸、32samples、无denoise与PNG SHA，未拿旧版本图改名复用。无denoise原因是当前Blender无OIDN，首次失败日志真实保留，不声称降噪高质量完成。

## 来源与相对深度
官方星瞳_Official，BV1DZ4y1U71V，页面描述2021-12-30直播。新原生帧：P1 t45.013436、t15.116586实际1920×1080高码率；P2 t32.024562实际3840×2160。P1本次4K切换实际失败，P2真4K成功。全部原生浏览器保存，前后暂停ready4且t/尺寸一致；播放器时间不是单帧PTS。已登录可见状态、菜单、来源身份及PNG SHA见[sources/manifest.json](../sources/manifest.json)与evidence。三图全部已见、全部参与训练，非严格盲验。

三图真实运行固定版本DepthAnythingV2Small相对逆深度，CPU1线程；模型网格518×924，原尺寸对齐图只是明确标记的bicubic派生。数值、minmax/方向、精确权重、人工人物/水/天空/反射/文字警示掩码及未知confidence均保留；不是亮度灰度/米制或唯一相机证据。[分析](../depth/analysis.md)

## 技术核验与修复
R01–R07每阶段真实普通Git记录，失败保留，见[阶段清单](local-stage-history.json)。本轮最主要修复：
1. 前半月厚屏弧端重复顶点导致各6开放边：R03焊接为0，闭合实体体积正。
2. R05推定前工作闭口延长超出半径8地坪：独立1057台面射线有107下方无地；R06仅将声明工作extent扩到半径11后缺失为0，不当真实前厅/海岸证据。
3. 默认GLB未应用伞Solidify背层：独立回导查49顶点漏层、约.008误差；R07显式 `export_apply=True`。两GLB真实回导各436几何对象、无missing/extra；世界顶点双向max约6.85e-7，在1e-4工作容差内。三角面按世界位置1e-5映射的multiset全部一致，不只比较bbox/顶点集。导入normal seam仅内存焊接后，非叶片闭合实体边界/非流形/不连贯绕序/负体积均0；材白evaluated世界几何精确同一。文件只读校验未变。

这些仅为本轮明确技术回归。开放叶片单列；柱cap-band部分重叠只证明模型部分相交，不承载/全接触通过；伞和台的工程ground相切非原场实际接地。近/后白框下段最低约−1.046/−1.154，穿出代理ground/SEA底，保留未证地下埋入/完整下框假说，不能声称全场并集碰撞/真实地下支撑通过。[独立综合审查原文](../qa/independent-R07/FINAL-R07-independent-review.md)及完整实际脚本、失败/自控与最终JSON已归档QA；独立6直叠复算最大差0。

## 仍未通过
[来源失败与工程推断清单](SOURCE-VALIDATION-FAILED.md)不可被归档或主图撤销：源2/3台凹/侧瓣透视明显不合、柱/窗带构图、白框/伞比例姿态、植物/盒体细节/材质照明仍错；远动态框与浮泡没有冒作静态硬几何。舞台长舌与圆地坪是工作边界，不是完整前廊。可靠后续独立直播回放同场新角度仍缺，历史抽样不是全片排除。

**下一步**：先补可靠同场新机位与非共面对应，解决共享相机/平台/柱的多视矛盾，再逐物件与材质迭代；不逐镜头隐藏或形变。现有版本作为可编辑、可追溯的未验收候选保留，不重复旧已交图片，不发新ZIP，不擅自合并或改权限。
