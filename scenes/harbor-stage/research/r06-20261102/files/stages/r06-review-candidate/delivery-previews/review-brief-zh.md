# 海港舞台 R06｜可编辑候选，尚未验收

**已完成：** 394 个可编辑物件、同几何白模、两份实际回导的 GLB；32 张正式渲染、14 张原生直接 50% 叠图及 8 组局部对照。8 个材质/白模检查方位已逐张查看，反向文字技术问题已修，旧错误阶段保留。

**仍未通过：** 来源绑定的条件相机没有完成标定，预告高俯上下视关系、实演侧部曲带出画比例等明显不合；外台阶、灯具、植物/背景仍粗略，大型充气物等未做。全部 7 帧都是构建输入，**后续独立回放确认仍缺**。直接叠图算术正确与技术检查通过，不等于来源还原通过；也未收到用户接受。

## 看图

- [正常主图：原生 1920×1080](../source-renders/preview-front/material.png)
- [三组来源失败概览：源 / 材 / 直接 50%（派生）](three-source-failed-overview-derived.png)
- [8 角材质联系表（派生）](eight-angle-material-derived.png)
- [8 角白模联系表（派生）](eight-angle-white-derived.png)

全部 7 组小对照保留：[实演正面](comparison-01-aug24-front-derived.png) · [预告正宽](comparison-02-preview-front-derived.png) · [预告高俯](comparison-03-preview-high-derived.png) · [预告斜宽](comparison-04-preview-wide-derived.png) · [预告低仰](comparison-05-preview-low-derived.png) · [120 秒侧部](comparison-06-companion-120-derived.png) · [126 秒真 4K 侧部](comparison-07-companion-126-derived.png)。

小图标注原尺寸与缩放，只整体缩小展示。原生来源、渲染和直混原件保留。材白共用条件相机；所有来源渲染共用几何/材质/照明，没有按镜头隐藏物件或扭曲图像掩盖残差。

## 继续编辑

- [材质 BLEND](../harbor-r06-material.blend) · [同几何白模 BLEND](../harbor-r06-white.blend)
- [材质 GLB](../harbor-r06-material.glb) · [白模 GLB](../harbor-r06-white.glb)
- [完整报告](../stage-report.md) · [逐物件证据](../object-evidence.md) · [小图 SHA/来源](preview-manifest.json)

模型单位不是实测米制。BLEND 贴图已打包；GLB 内嵌贴图，但不包含 Blender 区域灯/世界光。上述是仓库内相对入口；实际私有 Git/Space 地址由交付记录绑定，本地链接不表示已发布。
