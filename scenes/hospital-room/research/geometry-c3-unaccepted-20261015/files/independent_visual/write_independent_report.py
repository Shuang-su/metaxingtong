from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parent.parent;O=R/'independent_visual';S=R.parent/'hospital_anchor_preparation_20261014/restored'
sources={'G':S/'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','H':S/'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','F':S/'hospital-F-tv-BV1GqXMByE1s-t1823.678156-native.png','N640':R.parent/'hospital_empty_frame_annotation_20261014/source_views/BV1GqXMByE1s_640.406589_empty_hospital_native.png'}
paths=list(sources.values())+[R/'renders_D_baseline'/f'{k}_D_RAW_1920x1080.png' for k in ['G','H','F']]+[R/'renders_C2'/f'{k}_C2_RAW_1920x1080.png' for k in ['G','H','F']]+[R/'renders_C3'/f'{k}_C3_RAW_1920x1080.png' for k in ['G','H','F','N640']]
D={x['view']:x for x in json.load(open(R/'renders_D_baseline/manifest.json'))};C={x['view']:x for x in json.load(open(R/'renders_C3/manifest.json'))}
checks={k:{'same_camera_name_as_D':D[k]['camera']==C[k]['camera'],'matrix_and_lens_independent_check':'Not independently verified here: D render manifest does not record camera matrix or lens. Parent states G/H/F reuse D cameras.','render_sha256_matches_manifest':hashlib.sha256((R/'renders_C3'/C[k]['file']).read_bytes()).hexdigest()==C[k]['sha256'],'manifest_same_geometry_flag':C[k]['same_geometry']} for k in ['G','H','F']}
report={
 'status':'C3_NOT_SOURCE_ACCEPTED',
 'review_finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'summary_zh':'C3仅改善部分右外轮廓，仍明显不符合来源。米黄柱遮挡使三视图实际可见灰折面只剩来源约一半；灰折面顶部/轨道形态、两块靠背和其他模型差异未解决。N640相机假设也未获得直接来源验证。',
 'scope':{'review':'Independent visual comparison of actual sources and completed native RAW renders. No model edits, browser, user computer, or Git.','coordinate_system':'Native 1920x1080 pixels, origin upper-left.','evidence_images':'Unscaled, unwarped same-coordinate crops of source and raw images. Labels added outside cropped image regions only. No image overlay used as acceptance proof.','geometry_limit':'Visual contact cannot prove physical attachment or source geometry. Cross-view fingerprints below are render-manifest assertions, not an independent full mesh proof.','photometry_limit':'RAW images are noisy and rendered lighting differs. Shadow/fold shading alone cannot establish fold depth or topology.'},
 'render_identity_checks':checks,
 'excluded_evidence':[{'view':'H','source_xy':[1840,900],'reason':'Right gray outline is sofa-occluded, excluded.'},{'view':'G','source_xy':[1151,100],'reason':'Different top boundary branch, excluded from right-outline residuals.'},{'view':'H','source_xy':[1493,793],'reason':'Rounded right-cushion shoulder, not a straight right-side correspondence.'},{'view':'H','source_xy':[1228,798],'reason':'Dark shoulder/inter-cushion shadow defeats color-threshold edge extraction; no threshold residual used.'},'Characters, TV picture content, HUD, and exterior city content do not score room geometry.'],
 'findings':[
 {'id':'pillar_occlusion','priority':'blocking','verdict':'fail','views':['G','H','F'],'description_zh':'米黄柱在来源可见灰折面区域中向右扩张。C3虽收紧灰体右轮廓，柱右界基本继承C2，进一步把可见折面压成窄条。y=500处灰折面来源宽G约132–142/H164–174/F167–177px；C3约70/84/82px。软左边界只能取区间，不能当精确接触线。','evidence':[f'{k}_pillar_fold_native_comparison.png' for k in ['G','H','F']],'measurements':'visible_scanline_measurements.json'},
 {'id':'right_outer_contour','priority':'partial_improvement','verdict':'partial_not_acceptance','description_zh':'实际可见右外轮廓在G/H更接近来源，H抽样行差异落在约2px读数不确定性内；G约左偏3–7px。F y500仍左偏约19px、y700约11px，至下段才靠近。这里只陈述具体可见边，不把整块面或模型判为通过。','evidence':['G_pillar_fold_native_comparison.png','H_pillar_fold_native_comparison.png','F_pillar_fold_native_comparison.png'],'measurements':'visible_scanline_measurements.json'},
 {'id':'gray_top_and_rail','priority':'blocking','verdict':'fail','description_zh':'G/F来源灰折面顶端大体向右抬高；D/C2/C3可见灰体顶端却向右下落，且折面与下轨的画面接合、轨间横撑倾斜与位置不同。C3柱顶在RAW中抵到轨件，并不构成来源同一连接结构的证明。顶部另作形态证据，不复用被排除的G右轮廓点。','evidence':['G_top_connection_native_comparison.png','F_top_connection_native_comparison.png']},
 {'id':'sofa_two_backrests','priority':'blocking','verdict':'partial_left_improvement_right_unresolved','description_zh':'C3与C2靠背表现基本相同。左靠背上缘相对D有局部改善；但H来源左上缘从左到右上扬，C3从左到右下落，不能用一次平移概括解决。G右靠背明确可见的x802和x839处上缘仍比来源高约30px；H右靠背中右段上缘约低3–9px。质感、圆角/鼓包和下缘/座面关系仍不像来源。','evidence':['G_sofa_native_comparison.png','H_sofa_native_comparison.png'],'measurements':'visible_sofa_measurements.json'},
 {'id':'other_model_differences','priority':'unresolved','verdict':'not_corrected_by_C3','description_zh':'仍可见床栏/前景床面轮廓与遮挡关系不符，H及N640前景床面遮住的沙发区域过大；绿色椅背是较直硬的矩形，来源为弯曲壳形；输液袋及左侧设备/支架轮廓不同；百叶、墙顶连接和光照也不一致。前两类为直接轮廓差异；折面明暗、色彩、阴影不单独当几何证据。','evidence':['H_sofa_native_comparison.png','N640_sofa_native_comparison.png'],'full_raw_files':['renders_C3/G_C3_RAW_1920x1080.png','renders_C3/H_C3_RAW_1920x1080.png','renders_C3/F_C3_RAW_1920x1080.png','renders_C3/N640_C3_RAW_1920x1080.png']},
 {'id':'N640_camera_hypothesis','priority':'blocking_for_N640','verdict':'not_source_validated','description_zh':'N640 RAW有同一过遮挡问题，且窗框及家具画面位置整体偏右。y=500中央黑窗竖框暗核，来源x1001–1019，C3为x1056–1074，相差约55px。来源照片间静态背景旋转/焦距比拟合并不证明Blender眼位、深度或成图匹配；这里不能宣布N640通过。','evidence':['N640_pillar_fold_native_comparison.png','N640_sofa_native_comparison.png'],'mullion_measurement':{'y_band':[498,502],'source_dark_core_x':[1001,1019],'C3_dark_core_x':[1056,1074],'center_difference_px':55,'method':'5-row median RGB mean <60 within x960:1120; visually checked central mullion, not city content.'}}
 ],
 'recommendation_zh':'保留C3作为未验收实验记录；不要替代基线或宣称来源重建完成。下一轮必须联合约束柱/灰体的遮挡顺序与可见宽度、顶部到轨道的结构、两块靠背的跨镜头轮廓；F继续保留为条件检验，N640先修复并验证相机迁移。不得用每镜头隐藏、图像warp或贴图伪造通过。',
 'measurements':{'visible_contours':json.load(open(O/'visible_scanline_measurements.json')),'visible_sofa':json.load(open(O/'visible_sofa_measurements.json'))},
 'reviewed_files':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in paths],
 'evidence_images':[p.name for p in sorted(O.glob('*_native_comparison.png'))]
}
(O/'independent_visual_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
md='''# C3 独立视觉复核：来源未通过

已逐张看 G/H/F 来源、D/C2/C3 RAW，以及 N640 来源与 C3 RAW。所有图证都是原尺寸、同坐标直接裁切，没有缩放、位移、warp 或遮挡修补；未修改任何模型。

## 主要结果

1. **米黄柱遮挡是阻断项。** y=500 可见灰折面来源宽约 G132–142/H164–174/F167–177 px，C3只剩约70/84/82 px。来源左边界带阴影，给区间，不伪称精确接触线。右边线接近不能补偿整块可见面宽约减半。
2. **右外轮廓只属局部改善。** 实际 RAW 的 G右边线约左偏3–7px；H抽样行在约2px测读不确定性内；F在y500/y700仍约左偏19/11px，下段才靠近。不能以这些点宣布模型通过。
3. **灰折面顶部与轨道结构不符。** G/F来源顶端整体向右抬高；候选可见顶端向右下落。灰体接下轨的画面关系、横撑倾斜和位置也不同。柱顶抵到轨件不等于恢复来源结构，也不证明物理连接。
4. **两块沙发靠背仍未解决。** 左靠背相对D局部改善，但H上缘斜向仍与来源相反。G右靠背在x802、839的明确可见上缘仍高约30px；H右靠背中右段约低3–9px。C3继承C2，软包曲面、下缘及座面关系也不一致。
5. **其余显著差异仍在。** H/N640前景床面遮住沙发的范围过大；绿色椅背较直硬，来源为弯曲壳形；输液袋、左侧设备/支架、百叶及墙顶连接仍不同。光照、色彩和噪点差异不单独计作几何失败。
6. **N640相机假设未通过直接来源验证。** y=500中央黑窗框暗核来源x1001–1019，C3 x1056–1074，约右移55px；沙发等也偏右。照片静态背景旋转/焦距比拟合不能证明Blender眼位、深度或成图匹配。

## 图证索引（原图坐标）

- G_pillar_fold_native_comparison.png：x930–1220，y200–920；来源/D/C2/C3，可见宽度。
- H_pillar_fold_native_comparison.png：x1520–1880，y0–880；来源/D/C2/C3，可见宽度。未使用沙发遮挡的y900。
- F_pillar_fold_native_comparison.png：x100–460，y50–1070；来源/D/C2/C3，宽度及斜率。
- G_top_connection_native_comparison.png：x930–1320，y0–320；顶部、柱轨连接。
- F_top_connection_native_comparison.png：x150–850，y0–330；顶部、柱轨连接。
- G_sofa_native_comparison.png：x150–960，y800–1080；两靠背。
- H_sofa_native_comparison.png：x820–1580，y760–1050；两靠背及床面遮挡。
- N640_pillar_fold_native_comparison.png：x1540–1910，y100–850；柱/灰体。
- N640_sofa_native_comparison.png：x830–1900，y700–1050；沙发与前景床面。

## 证据限制与核验

- G/H/F的C3相机名称与D manifest相同；D manifest未记矩阵/焦距，本视觉复核不独立宣称已核验二者一致。RAW SHA256均与C3 manifest一致。每视图相同几何来自manifest声明，本视觉复核不代替独立物理/网格审查。
- H灰外轮廓(1840,900)因沙发遮挡排除；G(1151,100)属于不同顶部分支，不用于右外轮廓残差；H右靠背(1493,793)圆肩不当直侧边。
- H(1228,798)靠背暗肩的颜色阈值会抓到内部阴影，已排除该自动读数，未把异常残差当几何失败。
- 精确采样、分支说明、不确定性和原图SHA256详见 independent_visual_report.json；可复查采样脚本及 visible_scanline_measurements.json、visible_sofa_measurements.json。

## 结论

**C3可保留为未验收实验，不能提升为来源验收模型。** 下一轮需同时约束柱/灰体遮挡、可见宽度、顶部/轨道结构和两块靠背；F继续作条件检验，N640先验证相机迁移。不得每镜头隐藏、warp或伪造通过。
'''
(O/'independent_visual_report.md').write_text(md)
print(json.dumps({'status':report['status'],'json':str(O/'independent_visual_report.json'),'md':str(O/'independent_visual_report.md'),'checks':checks},ensure_ascii=False,indent=2))
