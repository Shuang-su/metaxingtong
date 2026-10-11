from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
p=Path('hospital_object_audit'); frames=p/'refs/extracted/hospital/frames'
f=Image.open(next(frames.glob('*-F-*')));g=Image.open(next(frames.glob('*-G-*')))
rf=Image.open(p/'F_render.jpg');rg=Image.open(p/'G_render.jpg')
rows=[('F native: 1920x1080 | t1823.678156 | crop (780,900,1920,1080)',f,(780,900,1920,1080)),('F archived render: 1180x664 | crop (470,545,1180,664)',rf,(470,545,1180,664)),('G native: 1920x1080 | t1116.180816 | crop (1510,715,1920,1035)',g,(1510,715,1920,1035)),('G archived render: 1180x664 | crop (925,495,1180,645)',rg,(925,495,1180,645))]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
out=Image.new('RGB',(1180,1060),'#f2f0eb');d=ImageDraw.Draw(out);y=20
d.text((20,y),'BED-END BOARD | Conditional visual diagnosis, NOT calibrated overlay',fill='#181818',font=font);y+=38
manifest=[]
for i,(label,img,box) in enumerate(rows):
 d.text((20,y),label,fill='#181818',font=font);y+=29;c=img.crop(box);c.save(p/f'bed_end_crop_{i+1}.png');out.paste(c,(20,y));y+=c.height+22
 manifest.append({'label':label,'crop_xyxy':box,'display_scale':1,'output':f'bed_end_crop_{i+1}.png'})
d.text((20,y),'Crops retain original pixels; no scaling, warping, registration or overlay.',fill='#181818',font=font)
out.save(p/'bed_end_evidence.png');(p/'crop_manifest.json').write_text(json.dumps(manifest,indent=2))
