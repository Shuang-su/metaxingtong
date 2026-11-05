from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent.parent
for n,r in [('11','source11-r03.png'),('10','source10-auxiliary-r03.png')]:
 a=Image.open(P/'sources'/f'{n}.webp').convert('RGB');b=Image.open(P/'renders'/r).convert('RGB');assert a.size==b.size==(1192,671)
 Image.blend(a,b,.5).save(P/'renders'/f'source{n}-direct50-r03.png')
 # Unaltered crop triples, all at the same pixel coordinates.
 boxes={'main-roof':(80,65,1110,225),'inner-stage':(270,348,918,493),'cloud-right':(1030,105,1192,240)} if n=='11' else {'common-roof':(0,0,1192,110),'common-inner':(0,410,1192,671)}
 for k,box in boxes.items():
  w,h=box[2]-box[0],box[3]-box[1];c=Image.new('RGB',(w,h*3+60),(20,20,20));d=ImageDraw.Draw(c)
  for i,(label,im) in enumerate([('SOURCE',a),('RENDER',b),('DIRECT 50%',Image.blend(a,b,.5))]):d.text((4,i*(h+20)+3),label,fill='white');c.paste(im.crop(box),(0,i*(h+20)+20))
  c.save(P/'renders'/f'roi-{n}-{k}.png')
ims=sorted((P/'renders').glob('check-*.png'));sheet=Image.new('RGB',(796*2,478*4),(25,25,25));d=ImageDraw.Draw(sheet)
for i,f in enumerate(ims):
 im=Image.open(f);x=(i%2)*796;y=(i//2)*478;sheet.paste(im,(x,y+30));d.text((x+6,y+7),f.stem,fill='white')
sheet.save(P/'renders/check-contact-sheet.png')
rows=[]
for f in sorted((P/'renders').glob('*.png')):
 b=f.read_bytes();rows.append({'path':str(f.relative_to(P)),'dimensions':Image.open(f).size,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(P/'qa/render-file-manifest.json').write_text(json.dumps(rows,indent=2))
