from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
r=Path(__file__).resolve().parent.parent;base=r;out=[]
for mode in ['material','white']:
 records=json.load(open(r/'qa'/('umbrella-render-'+mode+'-32s.json')));assert len(records)==4
 for rec in records:
  p=r/rec['path'];a=np.array(Image.open(p).convert('RGB'));assert a.shape==(671,1192,3);assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'];rec['nonblack_fraction']=float(np.any(a>8,axis=2).mean());rec['std']=float(a.std())
 json.dump(records,open(r/'qa'/('umbrella-render-'+mode+'-32s-validated.json'),'w'),indent=2)
 for source in ['03','04']:
  sp=r/'source'/(source+'.webp');rp=r/'renders'/('umbrella-'+mode+'-SOURCE'+source+'-32s.png');a=np.array(Image.open(sp).convert('RGB'));b=np.array(Image.open(rp).convert('RGB'));assert a.shape==b.shape==(671,1192,3);c=((a.astype(np.uint16)+b.astype(np.uint16))//2).astype(np.uint8);op=r/'renders'/('umbrella-'+mode+'-SOURCE'+source+'-direct50.png');Image.fromarray(c).save(op);d=np.array(Image.open(op));out.append({'source':str(sp.relative_to(r)),'render':str(rp.relative_to(r)),'overlay':str(op.relative_to(r)),'formula':'floor((sourceRGB+renderRGB)/2), uint16 addition, no crop/warp/resample/mask','dimensions':[1192,671],'values_checked':int(c.size),'mismatches':int((c!=d).sum()),'source_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(op.read_bytes()).hexdigest()})
for source,crop in [('03',(960,245,1192,440)),('04',(990,105,1192,330))]:
 paths=[r/'source'/(source+'.webp'),base/'renders'/('sign-material-SOURCE'+source+'-32s.png'),r/'renders'/('umbrella-material-SOURCE'+source+'-32s.png')];ims=[Image.open(p).convert('RGB').crop(crop) for p in paths];w,h=ims[0].size;canvas=Image.new('RGB',(w*3,h+24),'#202020');draw=ImageDraw.Draw(canvas)
 for i,(im,label) in enumerate(zip(ims,['Report source '+source,'Wing final straight valance','Umbrella band/valance proxy'])):canvas.paste(im,(i*w,24));draw.text((i*w+3,5),label,fill='white')
 dest=r/'renders'/('umbrella-SOURCE'+source+'-native-size-before-after.png');canvas.save(dest)
 out.append({'diagnostic':str(dest.relative_to(r)),'source_crop_xyxy':list(crop),'per_panel_size':[w,h],'resampling':False,'before':'wing final fd127 original actual32s image with straight umbrella, not a new render','after':'current umbrella candidate32s actual image','warning':'Native-size means original screenshot-pixel crop, not native video decoding'})
json.dump(out,open(r/'qa'/'umbrella-full-array-and-local-comparison.json','w'),indent=2)
