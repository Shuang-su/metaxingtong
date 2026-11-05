from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
r=Path(__file__).resolve().parent.parent
out=[]
for mode in ['material','white']:
 records=json.load(open(r/'qa'/('render-'+mode+'.json')))
 assert len(records)==10
 for rec in records:
  p=r/rec['path'];a=np.array(Image.open(p).convert('RGB'));assert a.shape==(671,1192,3);assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
  rec['pixel_mean']=a.mean(axis=(0,1)).tolist();rec['nonblack_pixel_fraction']=float(np.any(a>8,axis=2).mean());rec['pixel_std']=float(a.std());assert a.std()>5 and np.any(a>8,axis=2).mean()>.1
 for src in ['03','04']:
  sp=r/'source'/(src+'.webp');rp=r/'renders'/(mode+'-SOURCE'+src+'.png');a=np.array(Image.open(sp).convert('RGB'));b=np.array(Image.open(rp).convert('RGB'));assert a.shape==b.shape==(671,1192,3)
  c=((a.astype(np.uint16)+b.astype(np.uint16))//2).astype(np.uint8);op=r/'renders'/(mode+'-SOURCE'+src+'-direct50.png');Image.fromarray(c).save(op);re=np.array(Image.open(op));assert np.array_equal(c,re)
  out.append({'mode':mode,'source':str(sp.relative_to(r)),'render':str(rp.relative_to(r)),'overlay':str(op.relative_to(r)),'source_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(op.read_bytes()).hexdigest(),'dimensions':[1192,671],'formula':'uint8(floor((source_RGB_uint16 + render_RGB_uint16)/2)); no warp, crop, resample, mask or color transform','full_array_values_checked':int(c.size),'mismatched_values':int((c!=re).sum())})
 json.dump(records,open(r/'qa'/('render-'+mode+'-validated.json'),'w'),indent=2)
 canvas=Image.new('RGB',(1600,970),'#202020');draw=ImageDraw.Draw(canvas)
 for i,rec in enumerate(records):
  im=Image.open(r/rec['path']).convert('RGB');im.thumbnail((400,225));x=(i%4)*400;y=(i//4)*320;canvas.paste(im,(x,y+22));draw.text((x+5,y+4),mode+' '+rec['camera'],fill='white')
 canvas.save(r/'renders'/(mode+'-contact-sheet.jpg'),quality=92)
json.dump(out,open(r/'qa'/'direct50-full-array.json','w'),indent=2)
