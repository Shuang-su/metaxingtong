# 后台人台 R05→R06 独立 QA

结论：R05新增有限人台、R06裤顶帽局部修复已实际验证；来源姿态/衣版仍FAILED，脚底座/完整室内未建。GLB在导出默认aspect正确，但正式诊断图宽高比需要复现设置，详见限制。

## 模型与变化
R04旧215mesh世界顶点/面/UV保持，R05新增16mesh和MANNEQUIN_local一相机，共231mesh/5cam；旧4cam、灯、world、旧hide、材质节点保持，新对象未隐藏。
R05→R06仅两分叉下装改变，另外229mesh不变；每件仅末24顶点XY改变，低72顶点和全部Z/拓扑保持，所有UV/5cam/灯/world/hide/材质节点相同。两阶段各自材白几何/UV/相机/灯/world/hide一致；基本拓扑非流形0、退化0、正体积。

## 实际接触
R06实际loop_triangles连续三角距离：双裤间隙0.01399993896，无相互表面交叠；两裤各与上衣距离0（50/52 BVH面交叠对）。头→颈、颈→上衣、双上臂→上衣→肘→前臂→手指定链均表面距离0。腰带和短袖也有上衣/臂的实际表面关系。组件关系表全部保留，不将球杆相交叫真实关节或承载结构。
16人台物件与旧215物件所有实际AABB均分离，BVH关系亦无旧物件，因此本次没有与原帘/架相交或完全包含。无脚/底座意味着支承未建，不虚构接地证明。
实际上衣三角solid-angle winding检查两裤顶帽：每侧24环顶点+中心+24扇三角中心共49点，R05各34在上衣内，R06各49全在内；只为明确有限包含抽样，不称整片无自交/全向遮挡证明。R05可见硬阶留为失败。

## 实际导出边界
R05及R06双GLB均空场景真实导入231mesh/5camera，无缺失或多余对象；世界顶点双向最近误差最大4.76837e-7、camera矩阵2.98023e-7。模型保存/导出960×640，原camera为AUTO，GLB导入VERTICAL。相同960×640下MANNEQUIN_local视框一致；改为正式1192×671后该相机方向分量max偏差.050244，全部相机最大约.054816。因此不能声称原GLB任意改分辨率即可重现正式图。需保持导出aspect或明确恢复AUTO/sensor/分辨率侧车设置并独立核验，不能静默把此项标通过。
第一轮检查混用原960×640与回导1192×671，是无效比较，已标mixed-aspect-rejected保留；随后两边同aspect重算并定位上述真实fit差异。几何结果不受此影响。未做全部corner normal/UV导出逐值核，不冒称渲染等价。

## 四图/两裁切
两R05失败图+两R06当前材白诊断图均实际查看，1192×671/64samples/无降噪，只有一个人工新角度。R05裤顶露帽/硬阶明确，R06此视角收进上衣后消失；剩余衣身、裤管、头颈、袖臂仍严重简化，来源的复杂不对称衣型没有恢复。相机边缘切到伞/下装、白图噪声/低对比保留。
四图完整解码，记录SHA/bytes/尺寸/模型SHA全部一致。两个same-pixel裁切已实看，四块与对应原图矩形全部逐像素差0，原图/输出SHA一致，无resize。不能把诊断渲染像素当直播原生证据，没有source同机位叠图。

## 精确原件
- R05_material.blend `91eaf48dc9b5edda47d123ccfb30e1330fdb390e934a2d33fa8fd3ce5a8ffe90`
- R05_material.glb `8f95bb99f987b94c083e7990fd5f6f651f25d896e8463cf41435c2890a3e24a6`
- R05_white.blend `663ca6ea4ff28f5b167e422a3662736c3d4d65fd60381f6a42b90d057529fbc5`
- R05_white.glb `baa6ee5c4a00827e609256f782361616e9dbb42f03fed5f9936e11f19e3a2553`
- R06_material.blend `e2b285327c3f7a8465c26e95c3f0a1016b9b1a9bfa7da98d1d34643636cc27d0`
- R06_material.glb `c27f8b4815d8ee3840dbb026bd059e09cc26bc39900b7dc2c9ff391ef6de68c7`
- R06_white.blend `a65a76524789816049643445724d484bcc1ceb79a8d833c3cdc489345dcfce45`
- R06_white.glb `04566bc86888738b1c18433a3119e3f4a09db390a8ac249845fc0762c0b89317`

证据：R05/R06-diff-check.json、R05/R06-contact.json、R06-cap-containment.json、两阶段glb-projection-check及mixed-aspect-rejected记录、camera-aspect-diagnosis.json、R05-R06-images.json，相关脚本/日志。所有检查均只读生产模型、没有重渲或改Git。
