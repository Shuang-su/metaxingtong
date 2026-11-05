# 后台R11设备示意表面独立QA

实际R10→R11只移除七个失败新板/边框，保留两钮三键。剩236mesh全部世界/局部几何不变，原231当然未挪动；8cam、灯world、旧材质节点与剩余可见性不变。body仅前面face3（normal -Y）4个UV loops12..15改变，材质版仅此面绑定新DEVICE_front_diagram_not_scan，其余五面仍DARK_metal；白版六面仍WHITE_clay。材白实际世界顶点、三角及表面UV关联排序后全部相同。

五controls各连续三角距body为0，三键各8/两钮各48 BVH面交叠对，唯一全场AABB及表面邻居均为body，没有新第三方相交/包含候选。七实体板移除消除其新增体积与重复共面前表面，但旧body↔瓶6–8的相交/包含仍存在、body离桌.007499992847442627未修。不能说示意纹理修了原布局或设备实体凹槽。

两GLB真实空场回导各236mesh/8cam，最近世界顶点误差≤4.76837158203125e-7，同1192×671画幅视框≤5.960464477539063e-8。body材质GLB分两primitive，都有TEXCOORD_0；白一个primitive有UV。其余有限技术界限与旧报告一致，不宣称所有normal/材质视觉等价。

纹理是1024×640 RGB人工平面分区，非来源照片/扫描/真实网孔。外部PNG、BLEND packed3567bytes、GLB嵌入bytes全同SHA256 d8cf461703085858fbff3284a2af749b2e9c1c23e7bd9672d0cc325033b92db7，嵌入解码有效且RGB逐像素一致；BLEND为sRGB。白GLB无图像正常，白模不用示意纹理。该图只表达表观分区，不代表可编辑真实网孔/凹深，也不把缺失几何冒成完成。

两R11当前1192×671诊断图已实看：材图四角/分隔底黑块不再出现，纹理边线为平面，旧前瓶遮挡/穿body依旧；白图只有五controls与原box、没有实体饰板，低对比和采样噪声仍在。均同一个人工DIAG_device_front，不是来源匹配视角或整房完成。

两图SHA/bytes/模型绑定匹配记录。两份R09/R10/R11三段samepixel crop按[130,130,1020,671]上下拼接全数组误差0，SHA匹配；R09/R10是既有基线原图未当R11新渲。此次未制作来源direct50，不宣称source通过。

精确当前原件：
- R11_material.blend 54d6e8b3b204ed11e32b22cb457f13d94f7e344695ad14583bd837e5178dd6dd
- R11_material.glb 4248c4e4cedfa51ce4521f073f73282261b8a8f0df47beeb6be0bcb57d77458b
- R11_white.blend cab03e3a6d5c703504b96a56b97c1015856a14967f33cdd305c9fd412854e4b0
- R11_white.glb f49646190fc6b3e271b68ce0b1da22e33a906564f8c0083208976c85938d179e

证据：R11-diff-check.json、R11-front-assignment.json、R11-shared-surface-check.json、R11-new-contact-check.json、R11-glb-projection-check.json、R11-glb-texture-check.json、R11-images.json及脚本/log。未写生产Git/模型或重新渲染。来源仍FAILED。
