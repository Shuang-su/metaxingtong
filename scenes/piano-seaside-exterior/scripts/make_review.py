"""Direct 50% pixel blending. No registration, warp, masking, resize of evidence originals."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,sys,hashlib
root=Path(__file__).resolve().parents[1];stage=sys.argv[1] if len(sys.argv)>1 else 'r04';qa=root/'qa'/stage
sources={'N4037':'BV1CY411k7Co_00-40-37_native.png','N6318':'BV1CY411k7Co_t6318.457925_native.png','N2518':'BV1CY411k7Co_t2518.167350_native.png','N2453':'BV1CY411k7Co_t2453.795568_native.png','N6766':'BV1CY411k7Co_t6766.766366_native.png'}
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
rows=[];records=[]
for id,name in sources.items():
 rp=qa/f'source_{id}.png'
 if not rp.exists():continue
 s=Image.open(root/'sources/native'/name).convert('RGB');r=Image.open(rp).convert('RGB');assert s.size==r.size==(1920,1080),(id,s.size,r.size)
 overlay=Image.blend(s,r,.5);op=qa/f'overlay50_{id}.png';overlay.save(op)
 row=Image.new('RGB',(1440,310),'#19202a');draw=ImageDraw.Draw(row)
 for j,(im,title) in enumerate([(s,id+' native source'),(r,stage+' conditional camera render'),(overlay,'50% direct blend - uncalibrated')]):
  row.paste(im.resize((480,270)),(480*j,40));draw.text((480*j+10,10),title,font=font,fill='white')
 rows.append(row);records.append({'source_id':id,'source':str((root/'sources/native'/name).relative_to(root)),'render':str(rp.relative_to(root)),'overlay':str(op.relative_to(root)),'pixels':[1920,1080],'operation':'PIL.Image.blend(source.convert(RGB), render.convert(RGB), 0.5)','registration':'none','masking':'none; source performer and overlays preserved','status':'conditional manual source camera, not calibrated or accepted'})
contact=Image.new('RGB',(1440,310*len(rows)),'#19202a')
for i,row in enumerate(rows):contact.paste(row,(0,310*i))
contact.save(qa/'source-render-overlay-contact.jpg',quality=92)
(qa/'overlay-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
# Exact same-coordinate crops are derived checks, not additional source cameras.
boxes={'N6318':(300,350,1440,950),'N2518':(350,300,1800,1050),'N2453':(520,470,1600,1050),'N4037':(1100,580,1910,1080)}
for id,box in boxes.items():
 if not (qa/f'source_{id}.png').exists():continue
 s=Image.open(root/'sources/native'/sources[id]).convert('RGB').crop(box);r=Image.open(qa/f'source_{id}.png').convert('RGB').crop(box);o=Image.blend(s,r,.5)
 for role,im in [('source',s),('render',r),('overlay50',o)]:im.save(qa/f'local_{id}_{role}.png')
(qa/'local-crops.json').write_text(json.dumps({'coordinate_system':'original 1920x1080 left-top; x0,y0,x1,y1; no local registration','crops':boxes},indent=2)+'\n')
checks=sorted(qa.glob('check_*.png'))
if checks:
 sheet=Image.new('RGB',(1440,310*((len(checks)+2)//3)),'#19202a');d=ImageDraw.Draw(sheet)
 for i,p in enumerate(checks):
  x=i%3*480;y=i//3*310;im=Image.open(p);sheet.paste(im.resize((480,270)),(x,y+40));d.text((x+10,y+10),p.stem+' | inspection, not source',font=font,fill='white')
 sheet.save(qa/'inspection-contact.jpg',quality=92)
print('review generated',len(records),'source overlays;',len(checks),'inspection views')
