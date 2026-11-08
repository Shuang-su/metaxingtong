"""Direct pixel comparisons. Crops are display evidence, never new source views."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,re
R=Path(__file__).resolve().parents[1];Q=R/'qa/r11';F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
names=['source_N4037','source_N6318','source_N2518','source_N2453','source_N6766','main']
native={'N4037':'BV1CY411k7Co_00-40-37_native.png','N6318':'BV1CY411k7Co_t6318.457925_native.png','N2518':'BV1CY411k7Co_t2518.167350_native.png','N2453':'BV1CY411k7Co_t2453.795568_native.png','N6766':'BV1CY411k7Co_t6766.766366_native.png'}
def opened(p):return Image.open(p).convert('RGB')
def text(d,pos,label):d.text(pos,label,font=F,fill='white')
def pairs(state='S40'):
 sub='' if state=='S40' else 'alternate_S105';out=Image.new('RGB',(1280,400*6),'#17202b');d=ImageDraw.Draw(out)
 for j,name in enumerate(names):
  for i,stage in enumerate(['r10','r11']):
   p=R/'qa'/stage/sub/(name+'.png');im=opened(p);out.paste(im.resize((640,360)),(640*i,400*j+40));text(d,(640*i+8,400*j+10),stage+' | '+state+' | '+name)
 out.save(Q/('before-after-source-main.jpg' if state=='S40' else 'before-after-S105.jpg'),quality=92)
pairs();pairs('S105')
out=Image.new('RGB',(1440,310*5),'#17202b');d=ImageDraw.Draw(out)
for j,(key,src) in enumerate(native.items()):
 a=opened(R/'sources/native'/src);b=opened(Q/f'source_{key}.png');assert a.size==b.size==(1920,1080);o=Image.blend(a,b,.5);o.save(Q/f'overlay50_{key}.png')
 for i,(im,label) in enumerate([(a,key+' unchanged source'),(b,'R11 shared S40'),(o,'direct 50% / uncalibrated')]):out.paste(im.resize((480,270)),(i*480,j*310+40));text(d,(i*480+6,j*310+10),label)
out.save(Q/'source-render-overlay-contact.jpg',quality=92)
checks=[f'check_{i:02d}' for i in range(8)]+['check_top'];out=Image.new('RGB',(1440,310*3),'#17202b');d=ImageDraw.Draw(out)
for i,n in enumerate(checks):out.paste(opened(Q/(n+'.png')).resize((480,270)),(i%3*480,i//3*310+40));text(d,(i%3*480+6,i//3*310+10),'R11 '+n+' / diagnostic')
out.save(Q/'inspection-contact.jpg',quality=92)
cropdir=Q/'crops';cropdir.mkdir(exist_ok=True);records=[]
def crop(path,box,name):
 im=opened(path);c=im.crop(box);p=cropdir/(re.sub(r'[^a-zA-Z0-9_-]+','_',name)+'.png');c.save(p);records.append({'path':str(p.relative_to(R)),'input':str(path.relative_to(R)),'input_pixels':list(im.size),'xyxy':box,'crop_pixels':list(c.size),'transform':'crop only; native pixels; contact display scales separately'});return c
def triptych(label,source_path,source_box,render_name,render_box,sub='',display=(440,280)):
 imgs=[crop(source_path,source_box,label+'_source'),crop(R/'qa/r10'/sub/(render_name+'.png'),render_box,label+'_r10'),crop(Q/sub/(render_name+'.png'),render_box,label+'_r11')]
 out=Image.new('RGB',(display[0]*3,display[1]+64),'#17202b');d=ImageDraw.Draw(out)
 for i,(im,lab) in enumerate(zip(imgs,['Source / different framing','R10 frozen-camera crop','R11 same crop'])):
  im.thumbnail(display,Image.Resampling.LANCZOS);out.paste(im,(i*display[0]+(display[0]-im.width)//2,64+(display[1]-im.height)//2));text(d,(i*display[0]+7,10),lab);text(d,(i*display[0]+7,35),label)
 return out
rows=[]
rows.append(triptych('N4037 far lamp / identity tentative',R/'sources/native'/native['N4037'],(1790,635,1920,795),'source_N4037',(1160,395,1380,620)))
rows.append(triptych('N6318 cropped lamp / floor unavailable',R/'sources/native'/native['N6318'],(630,910,840,1080),'source_N6318',(440,990,690,1080)))
rows.append(triptych('N6318 S105 / cropped opening only',R/'sources/native'/native['N6318'],(630,910,840,1080),'source_N6318',(220,495,345,540),'alternate_S105'))
out=Image.new('RGB',(1320,sum(i.height for i in rows)),'#17202b');y=0
for im in rows:out.paste(im,(0,y));y+=im.height
out.save(Q/'source-lamp-local-comparison.jpg',quality=94)
rect=(550,520,1000,870);out=Image.new('RGB',(900,390),'#17202b');d=ImageDraw.Draw(out)
for i,stage in enumerate(['r10','r11']):im=crop(R/'qa'/stage/'main.png',rect,'main_'+stage);out.paste(im,(450*i,40));text(d,(450*i+8,10),stage+' main native crop; unchanged camera')
out.save(Q/'main-lamp-before-after.jpg',quality=95)
out=Image.new('RGB',(1440,600),'#17202b');d=ImageDraw.Draw(out)
for i,(path,label) in enumerate([(R/'qa/r11/diagnosis/R10_diagnostic_lantern.png','R10 new diagnostic render'),(Q/'diagnostic_lantern.png','R11 same diagnostic camera'),(Q/'white_diagnostic_lantern.png','R11 neutral geometry diagnostic')]):
 im=opened(path);im=im.crop((480,300,1340,1020));im.thumbnail((480,540));out.paste(im,(i*480+(480-im.width)//2,60));text(d,(i*480+8,10),label)
out.save(Q/'lantern-diagnostic-contact.jpg',quality=92)
im=opened(Q/'main.png');p=Q/'main_preview.jpg';im.save(p,quality=92,subsampling=0);assert p.stat().st_size<900*1024
report={'cropped_evidence':records,'overlay':'RGB direct Image.blend(source, render, 0.5), no registration, warp or masks','source_limits':['N4037 identities/positions tentative and source foreground lamp hidden in candidate','N6318 source full lamp but model image crops body/floor; cannot validate hidden portions','N2453 source lamps not matched in frozen camera; diagnostic is not an extra source view','N2518 triangular light and N6766 no clear paper bag are regression views, not paper-lamp targets'],'preview':{'pixels':list(im.size),'resized':False,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}}
(Q/'comparison-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('R11_COMPARISONS_COMPLETE')
if (Q/'glb_reimport_main.png').is_file():
 a=np.asarray(opened(Q/'main.png'),dtype=float);b=np.asarray(opened(Q/'glb_reimport_main.png'),dtype=float);old=np.asarray(opened(R/'qa/r10/main.png'),dtype=float);delta=np.abs(a-b)
 stats={'variant':'C','GLB_mean_absolute_RGB8_difference':float(delta.mean()),'GLB_max_channel_difference':float(delta.max()),'GLB_fraction_pixels_any_channel_gt_8':float(np.mean(delta.max(-1)>8)),'scope':'actual final C GLB import render with original BLEND world/lights retained, not standalone viewer comparison'}
 for label,(x0,y0,x1,y1) in {'main_lamp_core':(735,665,765,705),'main_adjacent_deck':(650,745,835,790)}.items():
  stats[label]={'xyxy':[x0,y0,x1,y1],'R10_mean_display_luma':float((old[y0:y1,x0:x1]@np.array([.2126,.7152,.0722])).mean()),'R11_mean_display_luma':float((a[y0:y1,x0:x1]@np.array([.2126,.7152,.0722])).mean()),'purpose':'fixed crop change diagnostic, not source metric'}
 (Q/'pixel-change-statistics.json').write_text(json.dumps(stats,indent=2)+'\n')
