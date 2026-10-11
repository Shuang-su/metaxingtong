from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,zipfile,shutil,html
R=Path(__file__).resolve().parents[1];Q=R/'qa';V=R/'renders';O=R/'delivery';O.mkdir(exist_ok=True)
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def ft(n):return ImageFont.truetype(font,n,index=2)
def header(im,text,h=48):
 out=Image.new('RGB',(im.width,im.height+h),(21,25,32));out.paste(im,(0,h));ImageDraw.Draw(out).text((15,12),text,font=ft(19),fill=(238,241,245));return out
panels=[]
for label in ('A','B','C'):
 source=Image.open(R/f'restored/references/Match_{label}_crop.png').convert('RGB');raw=Image.open(V/f'FullRoom_Match_{label}.png').convert('RGB');clean=Image.open(V/f'FullRoom_Match_{label}_clean.png').convert('RGB')
 overlay=Image.blend(source,raw,.5);header(overlay,f'{label}｜真实源帧 50% + 原始渲染 50%｜直接叠图，未做透视变形').save(Q/f'Overlay_50pct_{label}.jpg',quality=94)
 trip=Image.new('RGB',(1188*3,716),(21,25,32))
 for i,(im,lab) in enumerate([(source,'真实源帧'),(clean,'完整房间渲染'),(overlay,'源帧与原始渲染各 50% 直接叠图')]):trip.paste(header(im,f'{label}｜{lab}'),(1188*i,0))
 trip.save(Q/f'Source_Render_Overlay_{label}.jpg',quality=94)
 panels.append(trip.resize((1782,358),Image.Resampling.LANCZOS))
contact=Image.new('RGB',(1782,358*3+75),(21,25,32));d=ImageDraw.Draw(contact);d.text((18,14),'城堡宴会厅｜源图核对｜相机手动近似对齐，比例与陈设仍有明显偏差',font=ft(24),fill='white');d.text((18,46),'A/C 为相近正面，B 仅小幅斜向，不能视作三个独立校准基线。人物遮挡原样保留。',font=ft(17),fill=(185,194,210))
for i,p in enumerate(panels):contact.paste(p,(0,75+i*358))
contact.save(Q/'Castle_Hall_Source_Comparison.jpg',quality=94)
inspection=[('Entry','进厅全景｜天花与镜外长度为推定'),('Reverse','反向全景｜后墙与入口位置为推定'),('Side','侧向检查｜实体墙厚、真实窗洞、道具支撑'),('Ceiling','天花检查｜造型推定，网格实体闭合'),('Exterior','外部检查｜完整围护；未确认与花园连接'),('Cutaway','几何剖切｜临时副本真实切开，非源视频证据')]
board=Image.new('RGB',(1782,3*555+70),(21,25,32));d=ImageDraw.Draw(board);d.text((18,17),'城堡宴会厅｜完整房间检查｜普通视图使用同一固定几何',font=ft(24),fill='white')
for i,(lab,note) in enumerate(inspection):
 im=Image.open(V/f'FullRoom_{lab}_clean.png').convert('RGB');im.save(V/f'FullRoom_{lab}_clean.jpg',quality=95)
 p=header(im,note).resize((891,537),Image.Resampling.LANCZOS);board.paste(p,((i%2)*891,70+(i//2)*555))
board.save(Q/'Castle_Hall_FullRoom_Inspection.jpg',quality=94)
for l in ('A','B','C'):Image.open(V/f'FullRoom_Match_{l}_clean.png').convert('RGB').save(V/f'FullRoom_Match_{l}_clean.jpg',quality=95)
q=json.load(open(Q/'fullroom_geometry_validation.json'));g=json.load(open(Q/'fullroom_glb_roundtrip.json'));m=q['mesh_summary']
report='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>城堡宴会厅 · 完整房间检查</title><style>body{background:#141922;color:#e5e9f0;font:17px system-ui;max-width:1280px;margin:40px auto;padding:0 24px;line-height:1.75}h1{font-size:36px}h2{margin-top:44px;color:#ffd2a0}img{width:100%;margin:12px 0;border:1px solid #455064}section{padding:20px;background:#202838;border-radius:12px;margin:18px 0}.ok{color:#98e0af}small{color:#c3c9d4}a{color:#bad4ff}li{margin:8px 0}</style><h1>城堡宴会厅 · 完整房间检查</h1><p>2026-10-10 · 真实源帧近似重建，几何完整性续修</p><section><b class="ok">围护、网格、通行与 GLB 回导检查通过</b><p>地板、四面墙、天花、真实门窗洞口和厚度回边已形成有界厅体。没有为特定相机隐藏或搬动物件。天花、后墙及入口明确是推定补全。</p></section>'''
report+=f'<h2>结构验证</h2><ul><li>{m["objects"]:,} 个实体网格，{m["triangles"]:,} 个三角面。逐件检查：零开边、零非流形边、零退化三角面。</li><li>10,800 条常规围护射线与 991,990 条独立密集边缘射线均无漏出；全部 10 个门窗孔另通过 25,244 点无实墙遮挡检查。约 2.3 模型单位宽的中央通行带通过 785 个样本检查。比例推定，非实测米数。</li><li>GLB 回导物体名称与三角面数量一致；双向顶点误差 {g["max_bidirectional_vertex_error_m"]}，表面积相对误差 {g["surface_area_relative_error"]}；所有使用图片已内嵌。</li><li>检查是有限数值/视觉抽样，不是隐藏原布局的证据或工程认证。</li></ul>'
report+='<h2>完整厅体检查</h2><p>反向、侧向、顶面和外部可检查同一实体。剖切图仅在临时副本中真实切开墙顶，交付模型保持完整。以下画面不属于原视频证据。</p><img src="qa/Castle_Hall_FullRoom_Inspection.jpg">'
report+='<h2>源图、渲染与直接叠图</h2><p><a href="https://www.bilibili.com/video/BV1aw411T7ws/">原视频 BV1aw411T7ws</a>。A 00:45:15；B 01:15:07；C 01:13:44。A/C 相近正面，B 小幅斜向；不宣称三个独立校准基线。源图只做固定矩形裁切，没有透视拉伸。叠图采用真实源帧与原始渲染各 50%。</p>'
for l in ('A','B','C'):report+=f'<img src="qa/Source_Render_Overlay_{l}.jpg">'
report+='<h2>仍然存在的差异与推定</h2><ul><li>相机手工对齐，人物遮挡、柱列与窗的比例、花束/甜品细节、材质纹理和光照仍有差异。叠图保留这些残差。</li><li>镜头后方墙体、双扇入口、天花与结构厚度为合理补全，并未被原视频验证。</li><li>入口去向未知，没有确认或拼接花园连接。</li><li>窗外仅保留蓝色夜景材质表达，未声称重建真实外部环境。</li></ul><p>详细范围、文件使用方式及证据标签参见同包中文 README 和 JSON 检查记录。</p></html>'
(R/'Castle_Hall_QA_Report.html').write_text(report)
# Package original Library identities, so parent can replace those same versions after review.
def zwrite(path,items):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for src,dest in items:z.write(src,dest)
 assert path.stat().st_size<18000000,(path,path.stat().st_size)
readme=R/'README_城堡宴会厅_完整房间.txt'
common=[(readme,readme.name),(Q/'fullroom_geometry_validation.json','qa/fullroom_geometry_validation.json'),(Q/'fullroom_glb_roundtrip.json','qa/fullroom_glb_roundtrip.json'),(Q/'reference_manifest.json','qa/reference_manifest.json'),(Q/'view_provenance_summary.json','qa/view_provenance_summary.json'),(Q/'semantic_aperture_validation.json','qa/semantic_aperture_validation.json'),(Q/'independent_dense_envelope_validation.json','qa/independent_dense_envelope_validation.json'),(Q/'independent_review.json','qa/independent_review.json'),(Q/'independent_aperture_validation.json','qa/independent_aperture_validation.json'),(Q/'independent_all_apertures_validation.json','qa/independent_all_apertures_validation.json'),(Q/'independent_glb_roundtrip.json','qa/independent_glb_roundtrip.json')]
blend=common+[(R/'models/Xingtong_Castle_Hall_FullRoom.blend','models/Xingtong_Castle_Hall_FullRoom.blend')]+[(p,'textures/'+p.name) for p in (R/'restored/textures').glob('*.png')]+[(R/'scripts'/n,'scripts/'+n) for n in ['complete_hall.py','final_small_repairs.py','fix_portability.py','validate_fullroom.py','export_fullroom.py','render_fullroom.py','package_qa.py','fix_arch_aperture.py','fix_envelope_seams.py']]
blend.append((R/'original/03_Castle_Hall_Textured_Blender.zip','baseline/03_Castle_Hall_Textured_Blender.zip'))
zwrite(O/'03_Castle_Hall_Textured_Blender.zip',blend)
zwrite(O/'02_Castle_Hall_Textured_GLB.zip',common+[(R/'models/Xingtong_Castle_Hall_FullRoom.glb','models/Xingtong_Castle_Hall_FullRoom.glb')])
qa=common+[(p,'qa/'+p.name) for p in Q.glob('render_provenance_*.json') if 'preflight_' not in p.name]+[(R/'Castle_Hall_QA_Report.html','Castle_Hall_QA_Report.html')]+[(p,'references/'+p.name) for p in (R/'restored/references').glob('*')]+[(p,'qa/'+p.name) for p in Q.glob('*.jpg')]+[(p,'renders/'+p.name) for p in V.glob('*_clean.jpg')]+[(V/f'FullRoom_Match_{l}.png',f'renders/FullRoom_Match_{l}.png') for l in 'ABC']
zwrite(O/'04_Castle_Hall_Views_and_QA.zip',qa)
manifest=[]
for p in sorted(O.glob('*.zip')):manifest.append({'path':str(p),'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
json.dump(manifest,open(Q/'delivery_manifest.json','w'),indent=2);print(json.dumps(manifest,indent=2))
