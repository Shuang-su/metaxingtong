# 金檐环台 R02 独立技术首检：失败保留

冻结HEAD f7344697e10c5213bf3d0ca402f9d95c122c7ffd。实际单线程读取roof-r02.blend/roof-r02-white.blend、空场导入roof-r02.glb；精确SHA及全部对象表见check.json。未渲染、未修改生产文件。

275个材白mesh的世界三角表面、UV、visibility及两相机完全一致。五个屋盖有限厚壳各0非流形/退化、正体积；其余多数管条存在真实开口：259对象各16非流形边（两8边端环），0 loose/退化。34开放管signed volume≤0；未闭壳时此值不证明全体反法向，也不能以多数正volume认定封闭实体。未做全体自交/相邻支持检查，修闭合后应再核，不能移称通过。

材GLB真实回导275mesh/2cam，全部世界顶点双向最近误差0，直接原生GLB相机归一化角框最大2.98e-8、matrix最大1.86e-7。白GLB本冻结根本不存在，明确NOT_PRESENT，四文件实际是两BLEND/一GLB/一JSON，不称双导出通过。

实际factory-empty运行生产restore_glb.py，只将输出路径改独立目录，保存restored-from-glb.blend。发现真正相机恢复错误：GLB导入sensor_fit=VERTICAL，脚本重写原lens40/43而未恢复原AUTO及完整sensor参数；恢复后角框最大差约0.0548，不能复用原图或称同机位环境完整恢复。原保存1192×671/50%，恢复100%；首预览实际596×335，JSON仅写1192×671不能当原尺寸渲染记录。

恢复World实际节点输入/连接与原件完全相同，active SOURCE11正确；3AREA属性type/energy/color/size/DISK相同，matrix最多1.49e-7浮差。上述局部正确不抵消相机FOV错误。完整执行记录见restore-check.json/log和实际回存原件。

此次没有来源拟合或图像验收：10/11中央状态不同、非原生、未知相机尺寸，始终SOURCE FAILED。没有8检查角，有限屋顶/台阶候选不等全房壳。后续R03必须另版本/实际复核，旧R02错误保留。
