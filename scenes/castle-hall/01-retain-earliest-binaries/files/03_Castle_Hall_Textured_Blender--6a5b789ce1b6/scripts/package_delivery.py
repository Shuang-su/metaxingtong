from PIL import Image,ImageDraw
from pathlib import Path
import json,subprocess,zipfile,hashlib
R=Path(__file__).resolve().parents[1]
files=sorted(R.glob('renders/Final_*.png'));files=[p for p in files if not p.stem.endswith('_clean')]
subprocess.run(['python',str(R/'scripts/denoise.py')]+list(map(str,files)),check=True)
for cam,fn,ts in [('Match_A','castle_2715.jpg','00:45:15'),('Match_B','castle_4507.jpg','01:15:07')]:
 a=Image.open(R/'references'/fn).crop((0,26,1188,694)).convert('RGB');a.save(R/'references'/f'{cam}_crop.png');b=Image.open(R/'renders'/f'Final_Textured_{cam}_clean.png').convert('RGB')
 Image.blend(a,b,.5).save(R/'qa'/f'overlay_50pct_{cam}.jpg',quality=95)
 cv=Image.new('RGB',(2376,714),(22,25,33));cv.paste(a,(0,46));cv.paste(b,(1188,46));d=ImageDraw.Draw(cv);d.text((16,15),'SOURCE BV1aw411T7ws | '+ts,fill='white');d.text((1204,15),'APPROXIMATE RECONSTRUCTION | manual camera alignment',fill='white');cv.save(R/'qa'/f'source_render_{cam}.jpg',quality=94)
for cam in ['Panorama','Match_A','Match_B','Side']:
 a=Image.open(R/'renders'/f'Final_White_{cam}_clean.png').convert('RGB');b=Image.open(R/'renders'/f'Final_Textured_{cam}_clean.png').convert('RGB');cv=Image.new('RGB',(2376,714),(22,25,33));cv.paste(a,(0,46));cv.paste(b,(1188,46));d=ImageDraw.Draw(cv);d.text((16,15),'WHITE GEOMETRY | '+cam,fill='white');d.text((1204,15),'TEXTURED | IDENTICAL GEOMETRY AND CAMERA',fill='white');cv.save(R/'qa'/f'white_textured_{cam}.jpg',quality=94)
validation=json.load(open(R/'qa/roundtrip_validation.json'));assert validation['PASS'],validation
manifest={'source_url':'https://www.bilibili.com/video/BV1aw411T7ws/','source_date':'2023-11-10','reference_times':['00:45:15','01:15:07','01:13:44'],'scope':'Hall visible components; unseen ceiling/rear wall omitted; inferred scale and column spacing; manual camera matching','render':'1188x668, Cycles 48 samples, external OIDN denoising'}
json.dump(manifest,open(R/'qa/reference_manifest.json','w'),indent=2)
common=[R/'README_城堡宴会厅.txt',R/'qa/roundtrip_validation.json'];textures=list(R.glob('textures/*.png'))
packs={
 '01_Castle_Hall_White_Model.zip':common+[R/'models/Xingtong_Castle_Hall_White.blend',R/'models/Xingtong_Castle_Hall_White.glb'],
 '02_Castle_Hall_Textured_GLB.zip':common+[R/'models/Xingtong_Castle_Hall_Textured.glb']+textures,
 '03_Castle_Hall_Textured_Blender.zip':common+[R/'models/Xingtong_Castle_Hall_Textured.blend']+textures+list(R.glob('scripts/*.py')),
 '04_Castle_Hall_Views_and_QA.zip':common+[R/'qa/reference_manifest.json']+list(R.glob('renders/Final_*_clean.png'))+list(R.glob('qa/*.jpg'))+list(R.glob('references/*'))}
res=[]
for name,paths in packs.items():
 p=R/'delivery'/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for f in paths:z.write(f,f.relative_to(R))
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 size=p.stat().st_size;assert size<18*1024*1024
 res.append({'filename':name,'bytes':size,'MiB':round(size/1048576,3),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'integrity':'PASS'})
json.dump({'packages':res,'geometry_validation':'PASS'},open(R/'delivery/delivery_manifest.json','w'),indent=2);print(json.dumps(res,indent=2))
