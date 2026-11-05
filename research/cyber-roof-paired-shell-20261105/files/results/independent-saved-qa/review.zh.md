# a=.55 实验保存态与双GLB独立QA

输入研究HEAD cc82f4b79defe705f13400d7196714dee148ebad；export/roof-paired-a055{,-white}.{blend,glb}及recovery.json。逐件SHA见check.json，未改变生产文件。1CPU实际打开两BLEND、双GLB分别factory-empty导入，并再次factory-empty执行原restore脚本，输出仅在本QA目录。未重渲、未重新扫描参数。

## 保存态与旧低样执行态
275个材质mesh按与recipe同定义的local vertices、polygon indices、world matrix计算SHA，全部与candidate-source11-recipe的真实执行hash相同；此前已核两候选来源执行mesh哈希一致。材白全部275对象几何、UV、可见性完全一致。
材质节点类型/名称/输入值/连接与原R05相同；旧11相机矩阵、镜头、视框、shift/clip、原3灯matrix/type/energy/color/size/shape以及World节点类型/输入/连接均实际相同。材白这些项及渲染设置亦相同。未以文件名称推断同态。
保存态Cycles 1192×671/100%、8samples/no denoise、AgX/None、exposure0/gamma1、像素比1。active为SOURCE11；SOURCE10原相机也保留。旧source10执行时切换该原相机，source11无需切换。结合前一轮渲染脚本实际fresh-load与几何赋值审查，支持将旧两候选材图明确关联此次同态保存的材质实验；不是重新渲染，不包括旧两基线图作为候选图，更不包含白模图或八检查角。

## 实际双GLB回导
两者均275mesh/11cam；全对象世界顶点双向最近邻最大距离0（检查全部导入顶点，不仅bbox）。这是坐标集合核，不声称保留顶点索引或原quad面顺序。
原生导入相机lens可差7.92499，view_frame未归一化尺寸可差.92743；这不是构图失败。按−z归一化后11相机视框方向最大差3.54148e−8，matrix最大差3.57628e−7，shift/clip差0，画幅1192:671明确设置。不能比较不同sensor约定下裸lens数值就断言失配。
材质GLB含6个PBR材质、白GLB1个，无image外部纹理依赖；原生GLB没有完整World/AREA环境。本次没有跨软件实际图级等价测试。

## factory-empty恢复
材白分别从factory-empty导入执行restore并回存restored-material.blend/restored-white.blend，均275mesh/11cam/3AREA。
恢复World节点类型、全部已记录输入及Surface连接exact；渲染配置exact，active SOURCE11正确；相机最大数值浮差3.57628e−7，AREA矩阵/参数最大1.49012e−7。限定为本输入恢复，不把hardcoded DISK/AgX/current active处理说成通用无损恢复器。

## 限制与失败保留
本轮未新增拓扑、接触、自交或法向厚度全面检查，沿用已独立核的a=.55数学范围及其失败：旧左云穿插持续、局部法向投影厚度改变、两源垂直/轮廓错误。保存文件不使这些失败消失。
白模只有共享几何/导出/恢复技术核，没有实际白模图，未做白模视觉验收。实验仍SOURCE FAILED，未替代生产R05。
首QA脚本遇factory-empty原生GLB World=None未判空异常，已保留failed-none-world.py/log；修正后完整重跑两mode成功。该异常属QA代码，不能归咎输入文件。完整check脚本/JSON/log及回存证据一并保留。
