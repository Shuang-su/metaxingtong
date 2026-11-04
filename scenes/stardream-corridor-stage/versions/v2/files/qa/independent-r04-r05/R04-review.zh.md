# 走廊R04增量独立技术核验

2026-11-04。实际单线程Blender读取R02/R03/R04材白六模型，并真实空场导入R04双GLB；未渲染或改生产文件。

- R02→R03：全部187mesh世界坐标/面列表完全同；仅地面UV层内容变化。程序生成石纹不是来源贴图恢复。
- R03→R04：仅ONAIR_text拓扑变化。860顶点→430，637面保持，世界唯一坐标集合完全同。非流形边860→0、退化面0、正体积9.81818975357104e-5不变。全187mesh未见非流形/退化/非正体积异常；不等于自交或全场碰撞验收。
- 两次增量全部12相机矩阵/内参、灯光所核位置/类型/能量/颜色/尺寸/节点、world节点与颜色、物体隐藏状态相同。R04材白世界几何/UV/相机/灯/world/可见性相同。
- 两GLB实际回导各187mesh/12camera名称完整；双向世界最近顶点最大误差4.777675712830387e-7，camera世界矩阵最大3.5762786865234375e-7，同1192×671归一view_frame方向最大5.960464477539063e-8。
- 材BLEND三张1024²程序PNG均packed，字节SHA与相应外部PNG逐张相同；color为sRGB，rough/normal为Non-Color。白模无image且WHITE_clay常量材质，属预期。
- GLB三图全部内嵌无外部URI，地面绑定baseColor/normal(.5)/metallicRoughness，实际像素color及normal全部与各原PNG相同，rough重打包后的G通道与原灰值全部相同。rough重打包PNG SHA不同未误判丢失。不是整个渲染器光照等价证明。
- 材白GLB地面均有TEXCOORD_0；实际回导地面世界顶点/角点UV配对以1e-5取整集合相等（两版各24独特配对）。不是仅检查UV属性存在。

R02门孔/关闭门叶18ray、侧边界50ray的有限结论可因相关几何/相机精确不变继续引用，未重新执行；不称全场无缝。原23-S3无限支撑线有限段/遮挡反例、未知尺寸/左四灯对称推断/来源状态与灯位失配全部仍有效，没有删除不利点。正式套图及直接叠图本轮未检查，不据技术修复宣称来源通过。

完整精确SHA、差分、像素及回导记录：R04-diff-check.json、R04-glb-projection-check.json、R04-texture-check.json、R04-floor-uv-roundtrip.json。首次纹理检查错误地按mesh名称寻找object导致StopIteration，保留check_r04_textures-failed-meshname.py；更正为node关联mesh后实际检查完成，不曾将失败当通过。
