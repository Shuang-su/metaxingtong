# R05 独立有限技术复核

绑定d3d60a641edd0ec3b0cbe6a0cc1c2090f45e7727，四SHA及求值/回导结果见check.json。实际1线程双BLEND/双GLB；没有渲染或改生产。

材白162mesh/11camera，geometry/UV/visibility及相机完全相同。全部positive signed volume、零面积异常0。R04两环非流形消除，stage-central-solid仍1条非流形：实际中心轴(0,0,-.3)到(0,0,0)，linked_faces=0纯松边（state.json）。这是残余松边，不应误报台盘破洞，但仍不能说零异常。

双GLB实际空场回导，全部世界顶点双向nearest最大9.83e-7，11cam同1192:671归一化frame最大3.6912e-8。此处不是相机world pose全字段复核；后续冻结需补。media厚度导出修复保持。代表接触数/微隙在check.json，不能移称全场无碰撞。

World实际节点(.035,.035,.07,1)/Strength.45与新sidecar字段相符，旧world.color问题已修。但另发现实际保存BLEND的rim灯matrix与sidecar最大差1.7071069479，key/fill0；尚无可执行restore独立验证，不称侧文件可准确还原整场。建议明确view_layer.update后从冻结文件重新导出真实状态，保留旧失败。

未独立实看八角预览/正式图，未给有效性结论。来源仍FAILED，主任务已即时收到松边及灯matrix问题。
