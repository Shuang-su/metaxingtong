# 城市窗景卧室舞台 R06 增量归档

R01–R06真实增量，最终渲染尚未交付。保留R01拓扑/反光与相机失败、R02灯罩失败、R02b空心灯罩修复、R03共享窗/凳/灯光修改、R04有限屋顶缺口及推定支撑修复、R05仅相机训练拟合及部分原尺寸渲染、R06连续圆弧吧台。当前R06材白/GLB原件已收到；R06原有限网格审计565mesh，非接触/源验收或最终回导验证。官方5张1080源+同场同日粉丝3张真解码4K，后两4K未用于R05训练；不是后续日期回放验证。官方5帧及粉丝55秒帧缺独立保存后播放器状态记录。5份真实相对深度原网格924×518，E图远城排序失败；不是测量。来源仍未验收，R05训练误差及未知隐藏构造保留。

CURRENT指向下列R06原件；本批无R06最终渲染，R01/R03仅预览，R05只部分原尺寸渲染。不得拿旧预览冒充R06最终套图。原说明中某些“进行中”或“后续验证待补”仅描述当时阶段，不意味着全部门槛通过。

182普通文件原字节与依赖布局见[files](files/)；完整身份、13原始提交的既有/新增阶段映射见[provenance.json](provenance.json)。既有[R01归档](../r01-20261103/ARCHIVE.md)及失败字节不改；当前8新原提交映射为8真实当前归档commit。原history `history/city-window-bedroom-original-20261103` 从 `e773229b81c4f40293c5fb17196aa158d8b9ba8d` 正常前进至 `21e1853f761b173447ac5b842dfd4ba2469148a4`，不伪造时间/父链。

## CURRENT与证据

- [models/R06_material.blend](files/models/R06_material.blend)。
- [models/R06_white.blend](files/models/R06_white.blend)。
- [models/R06_material.glb](files/models/R06_material.glb)。
- [models/R06_white.glb](files/models/R06_white.glb)。
- [qa/R06-changes.json](files/qa/R06-changes.json)。
- [qa/R06-material-audit.json](files/qa/R06-material-audit.json)。
- [docs/spec.md](files/docs/spec.md)。
- [docs/plan-and-execution.md](files/docs/plan-and-execution.md)。
- [docs/object-evidence.md](files/docs/object-evidence.md)。
- [depth/cityroom-multiview-analysis.zh.md](files/depth/cityroom-multiview-analysis.zh.md)。
- [sources/capture-manifest.json](files/sources/capture-manifest.json)。
- [sources/fan4k-capture-manifest.json](files/sources/fan4k-capture-manifest.json)。
- [sources/later-replay-check.json](files/sources/later-replay-check.json)。

Issue/Draft PR/评论因先前具体发布审批拒绝暂停，本轮不尝试；只完成正常Git归档和后续远端回执。main不改，不强推、不用LFS、不上传bundle容器、不删Space。发布端不重跑任何原技术/视觉检查。网页实显未核，已知证书错误路线不绕过。

源清单8帧的原PNG大小/SHA/尺寸核对；深度清单核对结果见provenance.json，任何不一致保留原件并明确报告。远端字节回读尚未在本映射提交发生，完成后另附真实回执。
