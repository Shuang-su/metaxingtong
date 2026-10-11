from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,json,zipfile,hashlib
R=Path(__file__).resolve().parent;D=R/'final7p7';P=R/'frozen';P.mkdir(exist_ok=True)
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';F=ImageFont.truetype(font,23);S=ImageFont.truetype(font,17);B=ImageFont.truetype(font,32)
shutil.copy2(R/'README_中文.txt',D/'README_中文.txt')
for f in (R/'source/unpacked/textures').glob('*'):shutil.copy2(f,D/'textures'/f.name)
for f in (R/'source/unpacked/references').glob('*'):shutil.copy2(f,D/'references'/f.name)
for f in R.glob('*.py'):
 if f.name.startswith('independent_') and f.name.endswith('7p7.py') or f.name in ['build7p7.py','finish7p7.py','render7p7.py','validate7p7.py','verify_glb7p7.py','denoise7p7.py','package7p7.py']:shutil.copy2(f,D/'scripts'/f.name)
# Deliver compact high-quality previews; original render PNG stays in work folder.
render_files=[]
for f in sorted((D/'renders').glob('*_denoised.png')):
 
 im=Image.open(f).convert('RGB');out=f.with_name(f.stem.replace('_denoised','')+'_review.jpg');im.save(out,quality=94,subsampling=0);render_files.append(out)
for stem,ref,label in [('source_front','home_3040.jpg','约50:41正前方全景'),('source_close','home_3010.jpg','约50:11同轴拉近：不是独立侧面')]:
 src=Image.open(D/'references'/ref).convert('RGB').crop((0,26,1188,694))
 mat=Image.open(D/'renders'/(stem+'_material_denoised.png')).convert('RGB');white=Image.open(D/'renders'/(stem+'_white_denoised.png')).convert('RGB');assert mat.size==white.size==src.size
 white_overlay=Image.blend(src,white,.5);wp=D/'renders'/(stem+'_white_50percent_direct_overlay.png');white_overlay.save(wp,optimize=True);render_files.append(wp)
 overlay=Image.blend(src,mat,.5);op=D/'renders'/(stem+'_50percent_direct_overlay.png');overlay.save(op,optimize=True);render_files.append(op)
 canvas=Image.new('RGB',(2376,440),'#20242a');draw=ImageDraw.Draw(canvas);draw.text((18,8),label+'｜完整房间室内相机近似：精确源片拟合未达标',font=F,fill='#f1e6d5')
 for i,(im,title) in enumerate([(src,'源截图原样裁边'),(mat,'材质版：固定完整几何'),(white,'白模：同一几何'),(overlay,'50%直接叠图：无源图变形')]):
  draw.text((i*594+12,44),title,font=S,fill='#dddddd');canvas.paste(im.resize((594,334),Image.Resampling.LANCZOS),(i*594,74))
 draw.text((18,413),'人物/衣物、装饰画、透视、织物和光照差异保留。来源低清且同轴，不能证明隐藏侧面。',font=S,fill='#ecc68f')
 p=D/'renders'/(stem+'_comparison_中文.jpg');canvas.save(p,quality=94);render_files.append(p)
# Twelve ordinary camera views, all full room. Last includes exterior.
imgs=sorted([f for f in (D/'renders').glob('*_review.jpg') if f.name[:2].isdigit() and int(f.name[:2])<=12]);assert len(imgs)==12
sheet=Image.new('RGB',(1920,1650),'#20242a');draw=ImageDraw.Draw(sheet);draw.text((20,12),'卧室完整房间｜12个固定几何检查视角',font=B,fill='white');draw.text((20,55),'反向、真实门窗、墙角和外壳均可检查；门窗及未见部分是推定',font=F,fill='#e7c78e')
for i,f in enumerate(imgs):
 x=i%3*640;y=100+i//3*387;draw.text((x+12,y),f.stem.replace('_review',''),font=F,fill='white');sheet.paste(Image.open(f).resize((640,360),Image.Resampling.LANCZOS),(x,y+28))
p=D/'renders/卧室_十二视角_中文.jpg';sheet.save(p,quality=92);render_files.append(p)
cover=Image.new('RGB',(1600,1090),'#20242a');draw=ImageDraw.Draw(cover);draw.text((22,12),'星瞳卧室｜完整有限房间',font=B,fill='white');draw.text((22,58),'几何可检查 · 隐藏部分推定 · 源片精确拟合未达标',font=F,fill='#e7c78e')
for i,(stem,label) in enumerate([('01_入口看床','普通视角：材质完整模型'),('normal_white','相同几何：白模'),('07_反向入口','反向：推定入口与墙角'),('13_独立剖切_不用于普通视角','独立剖切副本：明确删墙顶')]):
 x=i%2*800;y=110+i//2*485;draw.text((x+16,y),label,font=F,fill='white');im=Image.open(D/'renders'/(stem+'_review.jpg'));cover.paste(im.resize((800,450),Image.Resampling.LANCZOS),(x,y+30))
p=D/'renders/卧室_完成预览_中文.jpg';cover.save(p,quality=94);render_files.append(p)
identity=json.loads((D/'analysis/geometry_identity.json').read_text());assert identity['identical']
checks=json.loads((D/'analysis/structure_validation.json').read_text());assert not checks['degenerate_faces'] and not checks['nonmanifold_objects'] and not checks['negative_signed_volume_objects'] and checks['corner_rays_all_hit'] and not checks['walkway_collisions'];assert all(x['entire_disk_inside_by_horizontal_analytic_extent'] for x in checks['area_lights'])
reimport=json.loads((D/'analysis/glb_reimport_validation.json').read_text());assert all(q['passed'] for q in reimport)
meta=[D/'README_中文.txt']+list((D/'analysis').glob('*.json'))+list((D/'analysis').glob('*.txt'))
filesets=[('01_Bedroom_Material_Models.zip','libfile_c4839cf40da0819186824a902802a7f1',[D/'models/01_bedroom_material.blend',D/'models/03_bedroom_material.glb']+meta),('02_Bedroom_White_Models.zip','libfile_fa9a5d3cb58c81919c49ccb857254b5d',[D/'models/02_bedroom_white.blend',D/'models/04_bedroom_white.glb']+meta),('03_Bedroom_Textures_Review.zip','libfile_87dc240f3d8c81919d2810ce4f18900a',[D/'models/05_bedroom_CUTAWAY_INFERRED.blend']+meta+list((D/'textures').glob('*'))+list((D/'references').glob('*'))+list((D/'scripts').glob('*.py'))+render_files)]
manifest=[]
for name,lib,files in filesets:
 p=P/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for f in files:z.write(f,str(f.relative_to(D)))
 assert p.stat().st_size<18000000,(p,p.stat().st_size)
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 manifest.append({'local_path':str(p),'name':name,'library_file_id':lib,'expected_current_version':0,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'zip_integrity':'passed','version_reason':'完整有限卧室：真实厚墙门窗、同几何白模、12视角与独立剖切、法线/射线/灯面/GLB核验；源片精确拟合未达标'})
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps(manifest,ensure_ascii=False,indent=2))
