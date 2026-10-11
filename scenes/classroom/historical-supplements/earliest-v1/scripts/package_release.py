from pathlib import Path
from PIL import Image
import zipfile,json,hashlib,os
R=Path(__file__).resolve().parents[1];S=R/'package_stage';S.mkdir(exist_ok=True)
# Copies only, so local full-resolution PNGs and original QA remain available for inspection.
paths=[]
def add(src,rel):paths.append((Path(src),rel))
add(R/'README_教室说明.txt','README_教室说明.txt')
for p in (R/'models').glob('Xingtong_Classroom_*'):
 if p.suffix in ['.blend','.glb']:add(p,'models/'+p.name)
for p in (R/'textures').glob('*.png'):add(p,'textures/'+p.name)
for name in ['class_919.jpg','class_1224.jpg','class_2123.jpg','class_3658.jpg','class_3912.jpg','class_4284.jpg','class_668.jpg','class_5447.jpg']:
 add(R/'references'/name,'references/'+name)
for p in (R/'delivery_views').glob('Final_*.jpg'):
 q=S/p.name;im=Image.open(p);im.save(q,quality=90,optimize=True);add(q,'renders/'+p.name)
for pattern in ['Overlay50_*.jpg','Paired_*.jpg','Comparison_*.jpg']:
 for p in (R/'qa').glob(pattern):
  q=S/p.name;Image.open(p).save(q,quality=89,optimize=True);add(q,'qa/'+p.name)
for name in ['roundtrip_validation.json','blender_textured_geometry.json','blender_white_geometry.json','normal_orientation_check.json','wide_camera_landmarks.json','image_comparison_manifest.json']:
 add(R/'qa'/name,'qa/'+name)
for p in (R/'scripts').glob('*.py'):add(p,'scripts/'+p.name)
manifest=[]
for p,rel in paths:manifest.append({'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
index=S/'MANIFEST.json';index.write_text(json.dumps({'title':'Xingtong 2024-04-12 Classroom reconstruction','status':'Geometry round-trip and UV/packed-image checks passed; dimensions and repeated counts explicitly estimated','files':manifest},indent=2));add(index,'MANIFEST.json')
def make(name,files):
 z=R/'delivery'/name
 with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as f:
  for p,rel in files:f.write(p,rel)
 return z
z=make('Xingtong_Classroom_White_Textured_PBR.zip',paths)
if z.stat().st_size<18*1024*1024:out=[z]
else:
 z.unlink();model=[x for x in paths if x[1].startswith('models/') or x[1] in ['README_教室说明.txt','MANIFEST.json'] or x[1].startswith('qa/Paired_')]
 rest=[x for x in paths if x not in model]+[(R/'README_教室说明.txt','README_教室说明.txt')]
 out=[make('01_Xingtong_Classroom_Models.zip',model),make('02_Xingtong_Classroom_PBR_QA.zip',rest)]
for z in out:
 assert z.stat().st_size<18*1024*1024
 with zipfile.ZipFile(z) as f:assert f.testzip() is None
print(json.dumps([{'path':str(z),'bytes':z.stat().st_size,'MiB':z.stat().st_size/1024/1024,'sha256':hashlib.sha256(z.read_bytes()).hexdigest()} for z in out],indent=2))
