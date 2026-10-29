from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[2];P=R/'c31';O=P/'renders';refs={'G':'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','H':'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png'};rows=[]
for p in sorted(O.glob('*_RAW_1920x1080.png')):
 k=p.name.split('_')[0];src=R/'inputs'/refs[k];a=np.asarray(Image.open(src).convert('RGB'),dtype=np.uint16);b=np.asarray(Image.open(p).convert('RGB'),dtype=np.uint16);assert a.shape==b.shape==(1080,1920,3);v=((a+b)//2).astype(np.uint8);dst=p.with_name(p.name.replace('_RAW_','_direct50_'));Image.fromarray(v).save(dst);assert np.array_equal(np.asarray(Image.open(dst)),v);rows.append({'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'render':p.name,'render_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'direct50':dst.name,'direct50_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'formula':'floor((source_RGB+render_RGB)/2)','warp_registration_mask':False})
(O/'direct50_manifest.json').write_text(json.dumps(rows,indent=2))
if (O/'G_C31_MATERIAL_RAW_1920x1080.png').exists():
 box=(1530,750,1920,1080);im=Image.new('RGB',(1600,410),'white');d=ImageDraw.Draw(im)
 for i,(lab,f) in enumerate([('Native G',R/'inputs'/refs['G']),('C29 actual full',R/'c29/renders/G_C29_MATERIAL_RAW_1920x1080.png'),('C31 actual full',O/'G_C31_MATERIAL_RAW_1920x1080.png'),('Direct50 no alignment',O/'G_C31_MATERIAL_direct50_1920x1080.png')]):
  d.text((5+i*400,10),lab,fill='black');im.paste(Image.open(f).convert('RGB').crop(box),(5+i*400,40))
 d.text((10,385),'Central slot only: bed-height trials remain rejected; absolute edge residuals remain.',fill='black');im.save(P/'C31_G_FULL_before_after_direct50.png')
print(len(rows),'exact overlays')
