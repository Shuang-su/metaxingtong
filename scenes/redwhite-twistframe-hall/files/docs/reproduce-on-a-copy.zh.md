# 在副本重放，不覆盖冻结原件

所有建模/渲染在dot云电脑既有Blender 4.3.2执行，未用外部3D生成。生产原件已冻结；需要重放时先复制此目录，避免覆盖真实历史。

- 直接编辑可打开R07材质或白模BLEND，不依赖外部贴图。
- 从头重建最终核心：在副本执行Blender后台scripts/build_r06.py，再打开该R06材质BLEND执行scripts/repair_r07.py。后者落地四红饰并导出材白R07。
- 源相机渲染：打开R07材质BLEND执行scripts/render_views.py，参数R07 source。
- 主图/原8检查：相应材/白BLEND执行scripts/render_r07_deliverable_views.py，参数main或checks。原plan/rear只保留有限/失败状态。
- 两补充诊断：打开R07白BLEND执行scripts/render_r07_extra_diagnostics.py。它仅加两诊断相机和固定补光，全部几何保持；会保存R07_diagnostic_views_ONLY.blend。--prepare-only只重建可复现场景并读既存图，不重渲。
- 诊断矩阵以已保存BLEND重新打开后的数据为准。scripts/correct_diagnostic_metadata.py读回所有矩阵/裁剪/镜头/灯参数。一次prepare-only未更新matrix的失败manifest完整保留，并有真实勘误提交，不作为当前证据。
- 正常源图不调用诊断灯或改相机物件可见性。灰度depth分析是另一路辅助资料，不是建模网格输入。

GLB中的AREA灯省略是原生导出限制；重新渲染GLB前恢复20:11画幅（如320×176）。同画幅下实际相机投影已独立比对，不可因为lens/sensor_fit字符串不同就误判或假称完全光照一致。
