from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,zipfile,hashlib,shutil
R=Path(__file__).resolve().parents[1];D=R/'delivery';D.mkdir(exist_ok=True)
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';font=ImageFont.truetype(FONT,25);small=ImageFont.truetype(FONT,18)
for stem,ref,title in [('front','home_3040.jpg','全景：同一正前方机位'),('close','home_3010.jpg','近景：同轴变焦，不是独立侧视验证')]:
 source=Image.open(R/'references'/ref).convert('RGB').crop((0,26,1188,694));render=Image.open(R/'renders'/(stem+'_material_denoised.png')).convert('RGB');assert render.size==source.size
 overlay=Image.blend(source,render,.5)
 overlay.save(R/'renders'/(stem+'_source_overlay.png'),optimize=True)
 out=Image.new('RGB',(1782,458),(28,29,32));d=ImageDraw.Draw(out);d.text((16,7),title,fill=(244,240,229),font=font)
 for i,(im,label) in enumerate([(source,'原始截图（人物与播放器叠层未纳入模型）'),(render,'真实网格 / 相机近似匹配'),(overlay,'50% 原图叠加：无图像局部变形')]):
  out.paste(im.resize((594,334),Image.Resampling.LANCZOS),(i*594,84));d.text((i*594+12,51),label,fill=(211,210,201),font=small)
 d.text((16,427),'单前视证据限制：尺寸、隐藏结构及左右侧墙为推定；装饰画为重绘近似。',fill=(226,197,138),font=small)
 out.save(R/'renders'/(stem+'_comparison.jpg'),quality=93)
# Compact model overview, labels distinguish viewability from evidence.
cover=Image.new('RGB',(1600,1050),(25,27,30));d=ImageDraw.Draw(cover);big=ImageFont.truetype(FONT,33)
d.text((25,15),'星瞳卧室 · 白模与材质版',font=big,fill=(244,240,228));d.text((27,60),'《与星瞳共度的一天》2024-04-19 | 可绕看真实网格 · 同轴参考近似重建',font=small,fill=(210,203,186))
for x,y,file,label in [(0,113,'normal_material_denoised.png','正常水平广角 / 材质版'),(800,113,'normal_white_denoised.png','相同几何 / 纯白模型'),(0,594,'front_material_denoised.png','正前方参考镜头 / 近似匹配'),(800,594,'opposite_material_denoised.png','另一观察方向 / 隐藏区域为推定')]:
 d.text((x+20,y-30),label,font=font,fill=(226,221,208));im=Image.open(R/'renders'/file).convert('RGB').resize((800,450),Image.Resampling.LANCZOS);cover.paste(im,(x,y))
cover.save(R/'renders/bedroom_overview.jpg',quality=94)
validation=json.loads((R/'analysis/glb_reimport_validation.json').read_text());assert all(x['passed'] for x in validation)
geo=json.loads((R/'analysis/geometry_audit.json').read_text());assert geo['white_material_geometry_identical']
filesets={
 '01_Bedroom_Material_Models.zip':[R/'models/01_bedroom_material.blend',R/'models/03_bedroom_material.glb',R/'README_中文.txt',R/'analysis/geometry_audit.json',R/'analysis/glb_reimport_validation.json'],
 '02_Bedroom_White_Models.zip':[R/'models/02_bedroom_white.blend',R/'models/04_bedroom_white.glb',R/'README_中文.txt',R/'analysis/geometry_audit.json',R/'analysis/glb_reimport_validation.json'],
 '03_Bedroom_Textures_Review.zip':list((R/'textures').glob('*'))+list((R/'references').glob('*'))+list((R/'scripts').glob('*.py'))+list((R/'analysis').glob('*.json'))+[R/'README_中文.txt']+list((R/'renders').glob('*_denoised.png'))+list((R/'renders').glob('*_comparison.jpg'))+list((R/'renders').glob('*_source_overlay.png'))+[R/'renders/bedroom_overview.jpg']}
manifest=[]
for name,files in filesets.items():
 p=D/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for f in files:z.write(f,f.relative_to(R))
 size=p.stat().st_size;assert size<18*1024*1024,(name,size)
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 manifest.append({'file':name,'bytes':size,'MiB':round(size/1024**2,2),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'zip_integrity':'passed'})
(R/'delivery/delivery_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
