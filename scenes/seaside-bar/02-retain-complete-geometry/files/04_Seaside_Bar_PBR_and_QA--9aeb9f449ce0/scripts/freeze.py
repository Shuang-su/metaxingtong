from pathlib import Path
from PIL import Image
import json,zipfile,hashlib,shutil,datetime
R=Path('/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom');q=R/'qa';S=Path('/workspace/scratch/fa58bfcf0425/bar_room_source/verified_collection')
v=json.load(open(q/'geometry_validation.json'));r=json.load(open(q/'source_structural_residuals.json'))
assert v['white_textured_identical_vertex_coordinates']
for t in ['textured','white']:
 assert v[t]['source']['degenerate_triangles']==0 and v[t]['source']['invalid_normals']==0
 assert v[t]['source']['nonfinite_uv']==0 and not v[t]['source']['missing_uv']
 assert v[t]['triangle_count_match'] and v[t]['symmetric_vertex_distance_units']<1e-5
assert all(x['lower_inside_mount'] and x['upper_inside_lifted_panel'] for x in v['brace_endpoints'])
contacts=json.load(open(q/'assembly_contact_corrections.json'))
assert max(x['residual_units'] for a in contacts.values() for x in a)<1e-5
lines=['最终技术检查（无量纲相对单位）','', '两根撑杆端点：'+json.dumps(v['brace_endpoints'],ensure_ascii=False), '杯盘/书/罐接触校正最大残差：'+str(max(x['residual_units'] for a in contacts.values() for x in a))]
for t in ['textured','white']:
 x=v[t];s=x['source'];lines += [t+': '+str(s['mesh_objects'])+' 个网格；'+str(s['triangles'])+' 个三角形。','闭合组件 '+str(s['closed_components'])+'；含非流形边组件 '+str(len(s['open_components']))+'。','退化三角形 '+str(s['degenerate_triangles'])+'；异常法线 '+str(s['invalid_normals'])+'；缺失UV '+str(len(s['missing_uv']))+'；非有限UV '+str(s['nonfinite_uv'])+'。','真实GLB回导三角形数量一致：'+str(x['triangle_count_match'])+'；双向最近顶点最大误差 '+str(x['symmetric_vertex_distance_units'])+' 相对单位。']
lines += ['', '材质/白模顶点坐标完全一致：'+str(v['white_textured_identical_vertex_coordinates']), '', '射线检查：主开口与左侧开口不命中遮挡；实体墙与地面应命中。',json.dumps(v['rays'],ensure_ascii=False), '', '完整发光圆柱包围盒与墙/掀板的空间关系：',json.dumps(v['lamp_bounds'],ensure_ascii=False), '', '源图人工锚点残差：A '+str(round(r['A']['rms_px'],1))+'px；B '+str(round(r['B']['rms_px'],1))+'px。','锚点为手工近似结构对应；A竖框只衡量水平距离，其余为二维距离。相机经人工调构图，不应作为独立扫描精度。叠图中还存在显著道具、材质、光照与海天背景差异。','B主要残差：桌面深度与遮挡、瓶杯复杂造型、窗板厚度、书脊纹理、右前罐与托盘尺寸。','A主要残差：巨大左前罐没有在B统一布局中出现，前服务台与右前道具的出现/缺失不一致；不以移动道具隐藏该差异。','没有新增运动视差，不能由这些残差得出真实侧后墙已还原。','', '支撑检查：地面顶面z=-0.44；新增柜侧板落至z=-0.44；前台肋/底板接触；瓶架三个台阶分别承接各排瓶底；左细杯补台与原左台面相交连接且有落地支柱；上掀板铰轴及两撑杆接入板下。此为构造连通性检查，非承重工程计算。']
(q/'技术检查与残差_中文.txt').write_text('\n'.join(lines))
# JPEG inspection copies, originals remain local; source and overlay PNGs stay lossless in QA.
review=R/'review_jpg';review.mkdir(exist_ok=True)
for p in R.joinpath('renders').glob('*.png'):
 Image.open(p).convert('RGB').save(review/(p.stem+'.jpg'),quality=93)
common=[(R/'README_海边吧台完整结构_中文.txt','README_海边吧台完整结构_中文.txt'),(q/'技术检查与残差_中文.txt','技术检查与残差_中文.txt')]
groups={
'03_Seaside_Bar_Textured_Blender.zip':common+[(R/'models/seaside_bar_complete_textured.blend','models/seaside_bar_complete_textured.blend')]+[(R/'renders'/('源图_'+x+'_透视近似_材质.png'),'renders/源图_'+x+'_透视近似_材质.png') for x in ['A','B']],
'02_Seaside_Bar_Textured_GLB.zip':common+[(R/'models/seaside_bar_complete_textured.glb','models/seaside_bar_complete_textured.glb')],
'01_Seaside_Bar_White_Model.zip':common+[(R/'models'/n,'models/'+n) for n in ['seaside_bar_complete_white.blend','seaside_bar_complete_white.glb']]+[(R/'renders'/('源图_'+x+'_透视近似_白模.png'),'renders/源图_'+x+'_透视近似_白模.png') for x in ['A','B']],
'04_Seaside_Bar_PBR_and_QA.zip':common+[(q/'section_diagnostic_only.blend','qa/section_diagnostic_only.blend')]+[(p,'qa/'+p.name) for p in q.iterdir() if p.suffix in ['.json','.txt','.png','.jpg']]+[(p,'inspection/'+p.name) for p in review.iterdir()]+[(p,'scripts/'+p.name) for p in R.joinpath('scripts').glob('*.py')]+[(p,'references/'+p.name) for p in S.iterdir() if p.name in ['README.txt','contact_sheet.jpg'] or p.suffix=='.json' or p.name.endswith('_exact_crop.png')]+[(p,'textures/'+p.name) for p in Path('/workspace/scratch/fa58bfcf0425/bar_room_source/recovered/textures').glob('*.png') if not p.name.startswith('sunset_backdrop')]
}
manifest={'candidate':'seaside_bar_complete_20261010','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_url':'https://www.bilibili.com/video/BV1CY411k7Co/','library_state':'待父通知后替换；尚未写入Library','verified_source_archive_sha256':'1c3441213831e896e32bc0926a5200554405c62e7b284942f6b1733af16cb463','expected_previous_version':0,'files':[]}
for name,files in groups.items():
 dst=R/'frozen'/name
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  names=set()
  for p,arc in files:
   if arc in names:continue
   z.write(p,arc);names.add(arc)
 size=dst.stat().st_size;assert size<18000000,(name,size)
 manifest['files'].append({'name':name,'path':str(dst),'bytes':size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(R/'frozen/freeze_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(manifest,ensure_ascii=False,indent=2))
