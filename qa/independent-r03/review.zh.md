# 金檐环台 R03 独立有限技术QA

冻结HEAD b1799ee12056a1edab0ba9de9a31e4dbb28a5d08，实际只读单线程检查，不渲染。每件BLEND/GLB SHA见check.json。

两版均275mesh/2cam。实际材白世界三角表面、UV、可见性及相机一致；全部275单体0非流形边、0退化三角、0孤立边且signed volume正。R02失败保留，不将开放管旧正/负volume充当实体结论。

R02→R03实际差分：275对象名和世界唯一顶点集合逐项完全同，259对象面数改变；材料分配、可见性、两相机矩阵/焦距/fit和三灯矩阵/能量/颜色不变。对应端帽/闭合轮廓修复，不是改变来源布局。此检查不证明全场无自交/相邻碰撞或每片支承连续；没把所有实体闭合当房间全壳封闭。

两GLB分别真实factory-empty导入：各275mesh/2cam，无缺失；全部世界顶点双向最近距离0（不是只比较bounds）；实际相机视框归一化角射线最大2.98e-8，matrix最大1.86e-7。材质为有限PBR假说，本报告未声称跨渲染器视觉等价或来源纹理恢复。

实际运行restore_r03_glb.py恢复材GLB并独立回存；白版采用相同脚本仅将GLB输入改白文件、输出改独立目录，亦factory-empty执行。两次保存的restored BLEND和脚本/日志/JSON均随报告。原存及恢复渲染字段1192×671/100%/24samples/no-denoise/pixelaspect一致；active SOURCE11正确。两相机frame差0，原AUTO恢复正确，不再发生R02改lens但遗留VERTICAL的视框错。

World实际Background节点输入和Surface链接完全同；三AREA的类型、能量、颜色、size、DISK相同，矩阵最多约1.49e-7浮差。脚本恢复是sidecar补回，不是GLB原生支持AREA/World，也未渲染验证视觉等价。完整字段见restore-check.json与restore-white-check.json。

尚未检查：全场实体接触/包含/自交、全屋盖与脊瓦支承、真实源相机拟合、正式8角可见性、图像直叠。只有2源假设机位，没有把它们叫8检查角。10/11中央动态状态不同，非原生报道图，隐藏背坡/支承、金云/媒体网格和尺度未证；SOURCE FAILED持续。可在此限定技术结果上继续下一有界制作/出图，不等于来源或整场验收。
