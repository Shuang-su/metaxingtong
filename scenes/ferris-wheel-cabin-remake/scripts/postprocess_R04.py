"""Direct pixel50/50 blends (not generative edits); resized contact sheets clearly derived."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1];q=R/'qa';pairs=[('front','3844.793761'),('bench','3868.514759'),('corner','3889.303546'),('high','3954.958617_high')];rows=[]
for view,t in pairs:
 src=R/f'sources/BV18C3d66E17_P1_{t}.png';im=Image.open(src).convert('RGB');assert im.size==(1920,1080)
 for mode in ['material','white']:
  rend=R/f'renders/R04_native_{mode}_SRC_{view}.png';ri=Image.open(rend).convert('RGB');assert ri.size==im.size
  out=q/f'R04_native_{mode}_{view}_direct50.png';Image.blend(im,ri,.5).save(out);rows.append({'source':str(src.relative_to(R)),'render':str(rend.relative_to(R)),'overlay':str(out.relative_to(R)),'size':list(im.size),'formula':'PIL.Image.blend RGB encoded values alpha0.5, no crop warp registration or content modification','sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
canvas=Image.new('RGB',(1440,4*296),(24,24,24));d=ImageDraw.Draw(canvas)
for i,(view,t) in enumerate(pairs):
 fs=[R/f'sources/BV18C3d66E17_P1_{t}.png',R/f'renders/R04_native_material_SRC_{view}.png',q/f'R04_native_material_{view}_direct50.png']
 for j,p in enumerate(fs):
  im=Image.open(p).convert('RGB');im=im.resize((480,270),Image.Resampling.LANCZOS);canvas.paste(im,(480*j,296*i+26));d.text((480*j+5,296*i+5),f'{view} / '+['native source DISPLAY resize','REMAKE uncalibrated camera','DIRECT50 native then DISPLAY resize'][j],fill='white')
canvas.save(q/'R04-source-contact.jpg',quality=91)
fs=sorted((R/'renders').glob('R04_check_CHECK*.png'));sheet=Image.new('RGB',(1440,((len(fs)+2)//3)*296),(24,24,24));d=ImageDraw.Draw(sheet)
for i,p in enumerate(fs):
 im=Image.open(p).convert('RGB').resize((480,270),Image.Resampling.LANCZOS);x=(i%3)*480;y=(i//3)*296;sheet.paste(im,(x,y+26));d.text((x+5,y+5),p.stem,fill='white')
sheet.save(q/'R04-check-contact-final.jpg',quality=90)
Image.open(R/'renders/R04_native_material_MAIN.png').convert('RGB').save(q/'R04-main.jpg',quality=93)
(q/'native-overlay-manifest.json').write_text(json.dumps(rows,indent=2))
