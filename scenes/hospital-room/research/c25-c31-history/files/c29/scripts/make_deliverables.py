from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];P=R/'c29';O=P/'renders';files={'H':'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','G':'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','N642':'BV1GqXMByE1s_642.617525_right_turn_native.png'};records=[]
for a in sorted(O.glob('*_RAW_1920x1080.png')):
 k=a.name.split('_')[0];src=R/'inputs'/files[k];x=np.array(Image.open(src).convert('RGB'));y=np.array(Image.open(a).convert('RGB'));assert x.shape==y.shape==(1080,1920,3)
 z=((x.astype('uint16')+y.astype('uint16'))//2).astype('uint8');p=O/a.name.replace('_RAW_','_direct50_');Image.fromarray(z).save(p);assert np.array_equal(np.array(Image.open(p)),z)
 records.append({'view':k,'source':files[k],'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'render':a.name,'render_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'overlay':p.name,'overlay_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'formula':'floor((native_source_RGB+actual_render_RGB)/2)','warp_resize_registration_mask':False})
(O/'direct50_manifest.json').write_text(json.dumps(records,indent=2)+'\n')
b=Image.new('RGB',(1140,1100),'white');d=ImageDraw.Draw(b);font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';ft=ImageFont.truetype(font,20);sm=ImageFont.truetype(font,16)
d.text((15,12),'C29 curtain internal-fold candidate: fixed cameras and existing outer envelope',font=ft,fill='black')
for i,(k,box) in enumerate([('H',(1580,150,1840,600)),('G',(980,150,1240,600))]):
 y=70+i*500;d.text((15,y-25),k+' native 1:1 crop '+str(box),font=sm,fill='black')
 paths=[R/'inputs'/files[k],R/'c28/renders'/(k+'_C28_MATERIAL_RAW_1920x1080.png'),O/(k+'_C29_MATERIAL_RAW_1920x1080.png'),O/(k+'_C29_MATERIAL_direct50_1920x1080.png')]
 for z,(label,p) in enumerate(zip(['Native reference','Before C28 actual','After C29 actual','Direct 50% overlay'],paths)):
  x=15+z*280;d.text((x,y),label,font=sm,fill='black');b.paste(Image.open(p).convert('RGB').crop(box),(x,y+25))
d.text((15,1060),'Internal spacing improves; top height, ridge positions and physical cloth thickness remain conditional.',font=sm,fill='black');b.save(P/'C29_H_G_native_before_after.png')
