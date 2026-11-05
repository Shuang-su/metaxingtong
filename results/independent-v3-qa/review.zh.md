# 环台外缘点阵 v3 独立保存态/导出/图像小核

输入HEAD aa6636b253ae1f06055a92d33fad38d5879674e4，cyber-ring-emissive-band-study-20261105/export/roof-led-surface-v3四原件及sidecar。原件SHA见check.json。1CPU只读实际两BLEND/两GLB与factory-empty sidecar恢复，没有生产写入或重渲。旧v2错读recipe失败另存independent-ring-led-v2-qa-20261105，不覆盖旧结论。

## 实际差分
与a055保存材基线相比275对象几何（local顶点、polygon索引、world matrix）和visibility全部exact；材白同几何/UV。只有STAGE_OUTER LED front full circumference inferred新增UV；128外竖面用新材槽，其余384面仍旧材。圆周UV独立按顶点角序/高度复算最大误差4.20739e−8。旧6材节点类型/输入/连接全同，旧11cam全同，3灯/World节点/渲染态同。新增唯一明确作者DIAG close相机，共12cam。
没有改变屋盖、内圈或其他几何。新增图案覆盖外圈全周，后侧延续仍是作者推断，不能说来源已观察。

## 贴图与均值
两张8192×256 RGB PNG在外部文件、BLEND packed和材质GLB bufferView内逐字节完全相同；GLB无外链buffer，白GLB无图像。sRGB色彩空间、Linear采样，白材不显图案正常。
实际节点Emission Strength=9.124373435974121；GLB通过KHR_materials_emissive_strength保存同值，emissiveFactor=[1,1,1]，两纹理槽正确，metallic=.2/roughness=.3。
独立全PNG sRGB解码线性均值[.0263352840887,.186262769255,.129738521007]，与recipe0差。乘保存强度后为[.240292966568,1.699531063903,1.183782714701]，相对旧[.24,1.7,1.18]按(.2126,.7152,.0722)加权比1.00000001006。只证明均匀UV贴图像素线性发光均值的这一标量近等，RGB各分量并不全exact，更不证明相机图像亮度、反射、总功率或源真实发光值相等。暗底Base Color同时被改，是表面类别假说，不隐瞒其影响。
1024列×4行是作者频率，不能等于真实灯数。实体灯珠未新增。

## 实际GLB与恢复
两GLB空场真实导入：275mesh/12cam。全对象世界顶点双向最近邻最大0；此为坐标集合而非顶点索引/quad拓扑保真。外带world+UV角点集合四舍五入5位一致。所有相机1192:671归一化视框最大差4.01090e−8、matrix3.57628e−7、shift/clip0。
重新factory-empty执行原v3恢复脚本并回存两独立BLEND：275mesh/12cam/3AREA；World节点输入连接与渲染态exact，相机最大浮差3.57628e−7，灯1.49012e−7。不能把依赖sidecar的环境说成GLB原生包含，也未做跨软件图级无差证明。

## 两张真正新图
实际独立查看v3-material-close-8s.png与v3-material-source11-8s.png，均1192×671、alpha全255；图SHA、保存输入BLEND SHA、渲染脚本SHA和实际强度与各recipe一致。脚本fresh load真实v3，并在渲前检查强度和packed PNG，不复用旧v2错强度图。
近景可清楚区分多行亮格/暗间隙，满足有限表面类别示例；噪点仍明显。source11机位仅两侧部分外带入画，中央近缘仍出画，原台环位置/屋盖/云/环境失配都保留。无白模实渲、无新八角套图、无source10第二角同带验真。本轮没有直接50%新叠图，因此未声称新叠图已核。

结论：修复v2强度路径错配，v3可作为独立可编辑的单源类别材质实验；SOURCE FAILED，不升级为整体重建验收。原a055模型的已有穿插/厚度/形状误差不因表面贴图而消失。
