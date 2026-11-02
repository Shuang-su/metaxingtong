# 红月洞屏海景舞台：2026-11-02 原件重制作

**当前 R07：有限后半舞台条件重建，来源未验收，不计作新场景。**

从本轮重新采集的官方原生参考新制作；旧R10/R11原件缺失，没有恢复其旧文件或SHA。所有阶段真实普通Git保留，不用LFS。

- 当前可编辑原件：[材质BLEND](models/R07_material.blend)、[白模BLEND](models/R07_white.blend)
- 跨软件导出：[材质GLB](models/R07_material.glb)、[白模GLB](models/R07_white.glb)；显式 `export_apply=True` 保留伞纸厚度
- [模型字节与Git blob](models/R07-artifacts.json) · [新来源身份/原生帧manifest](sources/manifest.json)
- [相对深度诊断](depth/analysis.md) · [R05冻结时逐物件及历史限制](docs/R05-status.md)
- [R07最终交付记录](docs/R07-final-delivery.md)：实际主图/8检查角/3原尺寸材白/6直接50叠图已齐并读回；[来源未通过清单](docs/SOURCE-VALIDATION-FAILED.md)保持有效。

P1 t45.013436/t15.116586 为实际1920×1080高码率（本次4K切换失败），P2 t32.024562为真实3840×2160。三张浏览器原生导帧均前后暂停ready4、时间与尺寸不变，非插值。三源全部已见并训练，不称盲测。画质菜单/登录可见状态与解码证据另存evidence。

R05延长工作前闭口造成台面超出有限地坪、默认GLB漏伞Solidify背层，两项已留失败；R06工作地坪extent改为半径11，仅推定边界非前厅；R07显式导出evaluated厚度。独立回导436几何对象、材白同几何，世界顶点双向max约6.85e-7；1057台面采样无工作地坪由107降为0。这些技术回归不等于来源还原通过。

台轮廓多边形近似、上弧窗曲率/柱构图/白框/伞比例、物件细节/材质等仍有可见重影，隐藏支撑/尺寸/前方结构未证。后续独立直播同场新角度仍缺，历史抽样不当全片排除，用户未验收。不声称完整原场馆已复原。
