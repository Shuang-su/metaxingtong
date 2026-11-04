from PIL import Image,ImageDraw
import pathlib,json,hashlib,numpy as np
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R06-comparisons';out.mkdir(exist_ok=True);records=[]
for mode in ('material','white'):
 for num,name in [(13,'SOURCE_13_high'),(14,'SOURCE_14_front'),(15,'SOURCE_15_exterior'),(21,'SOURCE_21_high')]:
  sf=P/'sources/report'/f'{num:02d}.png';rf=P/'renders/R06'/f'{mode}_{name}.png'
  if not rf.exists():continue
  a=Image.open(sf).convert('RGB');b=Image.open(rf).convert('RGB');assert a.size==b.size==(1192,671)
  # No resampling/registration/warp: round-half-up mean of original RGB channels.
  ar=np.array(a).astype(np.uint16);br=np.array(b).astype(np.uint16);ov=((ar+br+1)//2).astype(np.uint8);f=out/f'{mode}_{name}_direct50.png';Image.fromarray(ov).save(f)
  records.append({'source':str(sf.relative_to(P)),'render':str(rf.relative_to(P)),'overlay':str(f.relative_to(P)),'source_sha256':hashlib.sha256(sf.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256(rf.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':[1192,671],'formula':'floor((uint16(source_RGB)+uint16(render_RGB)+1)/2)','warp':False,'source_type':'article screenshot, not native frame, clip time unknown','result':'FAILED source reconstruction; diagnostic only'})
 for group,cameras in [('eight-checks',[f'CHECK_{i:02d}' for i in range(1,9)])]:
  fs=[P/'renders/R06'/f'{mode}_{n}.png' for n in cameras]
  if not all(f.exists() for f in fs):continue
  contact=Image.new('RGB',(1200,742),'#303030');d=ImageDraw.Draw(contact)
  for i,f in enumerate(fs):
   im=Image.open(f).convert('RGB');im.thumbnail((396,223));x=i%3*400;y=i//3*247;contact.paste(im,(x,y+22));d.text((x+4,y+4),cameras[i]+' MODEL DIAGNOSTIC',fill='white')
  contact.save(out/f'{mode}_{group}.jpg',quality=93)
(P/'qa/R06-overlay-records.json').write_text(json.dumps(records,indent=2))
print('complete overlays',len(records))
