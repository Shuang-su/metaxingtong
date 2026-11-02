from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parents[1];Q=R/'qa/front-camera-diagnostic';src=Image.open(R/'sources/BV18C3d66E17_P1_3844.793761.png').convert('RGB');rows=[]
for mode in ['material','white']:
 p=R/f'renders/R05_native_{mode}_SRC_front.png';im=Image.open(p).convert('RGB');assert im.size==src.size==(1920,1080);out=Q/f'R05_native_{mode}_front_direct50.png';Image.blend(src,im,.5).save(out);rows.append({'render':str(p.relative_to(R)),'overlay':str(out.relative_to(R)),'dimensions':[1920,1080],'formula':'encoded RGB exact PIL blend alpha0.5, no warp or resize before overlay','sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
canvas=Image.new('RGB',(1440,592),(24,24,24));d=ImageDraw.Draw(canvas)
for i,mode in enumerate(['material','white']):
 paths=[R/'sources/BV18C3d66E17_P1_3844.793761.png',R/f'renders/R05_native_{mode}_SRC_front.png',Q/f'R05_native_{mode}_front_direct50.png']
 for j,p in enumerate(paths):
  im=Image.open(p).convert('RGB').resize((480,270),Image.Resampling.LANCZOS);canvas.paste(im,(j*480,i*296+26));d.text((j*480+5,i*296+5),mode+' / '+['source DISPLAY resize','R05 conditional camera NOT calibrated','native50 then DISPLAY resize'][j],fill='white')
canvas.save(Q/'R05-front-contact.jpg',quality=92);(Q/'R05-overlays.json').write_text(json.dumps(rows,indent=2))
