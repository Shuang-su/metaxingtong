"""Unregistered R09/R10 pixel comparisons and native-source 50% overlays."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1];Q=R/'qa/r10';font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
names=['source_N4037','source_N6318','source_N2518','source_N2453','source_N6766','main'];manifest=[]
def sheet(pairs,path):
 out=Image.new('RGB',(1280,400*len(pairs)),(22,27,34));d=ImageDraw.Draw(out)
 for j,(a,b,title) in enumerate(pairs):
  for i,(p,label) in enumerate([(a,'R09'),(b,'R10')]):
   im=Image.open(p).convert('RGB');out.paste(im.resize((640,360)),(640*i,400*j+40));d.text((640*i+8,400*j+10),label+' | '+title,font=font,fill='white')
 out.save(path,quality=92)
pairs=[]
for name in names:
 a=R/'qa/r09'/(name+'.png');b=Q/(name+'.png');aa=Image.open(a).convert('RGB');bb=Image.open(b).convert('RGB');assert aa.size==bb.size==(1920,1080);delta=np.abs(np.asarray(aa,dtype=float)-np.asarray(bb,dtype=float));manifest.append({'name':name,'before':str(a.relative_to(R)),'after':str(b.relative_to(R)),'pixels':[1920,1080],'mean_absolute_rgb8_difference':float(delta.mean()),'registration':'none; same frozen camera and geometry','interpretation':'difference from shared environment sampling, not source accuracy'});pairs.append((a,b,name+' / common S40'))
sheet(pairs,Q/'before-after-source-main.jpg')
if (Q/'alternate_S105').exists():sheet([(R/'qa/r09/alternate_S105'/(n+'.png'),Q/'alternate_S105'/(n+'.png'),n+' / common S105') for n in names],Q/'before-after-S105.jpg')
# Full-resolution crop remains exact pixel coordinates; contact only adds labels.
out=Image.new('RGB',(1440,760),(22,27,34));d=ImageDraw.Draw(out)
for i,stage in enumerate(['r09','r10']):
 im=Image.open(R/'qa'/stage/'source_N6766.png').crop((0,0,720,720));im.save(Q/(stage+'_N6766_sky_exact_crop.png'));out.paste(im,(720*i,40));d.text((720*i+8,10),stage+' actual full render crop: x0..720 / y0..720',font=font,fill='white')
out.save(Q/'N6766-sky-before-after.jpg',quality=95)
native={'N4037':'BV1CY411k7Co_00-40-37_native.png','N6318':'BV1CY411k7Co_t6318.457925_native.png','N2518':'BV1CY411k7Co_t2518.167350_native.png','N2453':'BV1CY411k7Co_t2453.795568_native.png','N6766':'BV1CY411k7Co_t6766.766366_native.png'}
rows=[]
for key,name in native.items():
 a=Image.open(R/'sources/native'/name).convert('RGB');b=Image.open(Q/f'source_{key}.png').convert('RGB');assert a.size==b.size==(1920,1080);o=Image.blend(a,b,.5);o.save(Q/f'overlay50_{key}.png');rows.append((a,b,o,key))
out=Image.new('RGB',(1440,310*5),(22,27,34));d=ImageDraw.Draw(out)
for j,(a,b,o,key) in enumerate(rows):
 for i,(im,label) in enumerate([(a,key+' unchanged native'),(b,'R10 shared S40'),(o,'direct 50% / uncalibrated')]):out.paste(im.resize((480,270)),(480*i,310*j+40));d.text((480*i+8,310*j+10),label,font=font,fill='white')
out.save(Q/'source-render-overlay-contact.jpg',quality=92)
im=Image.open(Q/'main.png').convert('RGB');p=Q/'main_preview.jpg';im.save(p,quality=92,subsampling=0);assert p.stat().st_size<900*1024
(Q/'comparison-manifest.json').write_text(json.dumps({'comparisons':manifest,'sky_crop_xyxy':[0,0,720,720],'source_overlays':'PIL.Image.blend(source RGB, render RGB, 0.5); no transform or mask','JPEG_preview':{'path':str(p.relative_to(R)),'pixels':list(im.size),'resized':False,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}},indent=2)+'\n')
print('R10_COMPARISONS_COMPLETE')
