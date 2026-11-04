from PIL import Image,ImageDraw
import pathlib,json,hashlib,numpy as np
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R06-comparisons';out.mkdir(exist_ok=True);records=[]
for mode in ['material','white']:
 for num,name in [(8,'SOURCE_08_wide'),(23,'SOURCE_23_oblique'),(26,'SOURCE_26_side')]:
  sf=P/f'sources/report/{num:02d}.png';rf=P/f'renders/R06/{mode}_{name}.png'
  if not rf.exists():continue
  a=Image.open(sf).convert('RGB');b=Image.open(rf).convert('RGB');assert a.size==b.size==(1192,671)
  ar=np.array(a,dtype=np.uint16);br=np.array(b,dtype=np.uint16);f=out/f'{mode}_{name}_direct50.png';Image.fromarray(((ar+br+1)//2).astype(np.uint8)).save(f);records.append({'source':str(sf.relative_to(P)),'render':str(rf.relative_to(P)),'overlay':str(f.relative_to(P)),'source_sha256':hashlib.sha256(sf.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256(rf.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'dimensions':[1192,671],'formula':'floor((uint16(source_RGB)+uint16(render_RGB)+1)/2)','resampling':False,'state':'common warm model state; source08/23 dynamic-light/layout relationship unknown','source_type':'report screenshot, not native decoded frame, clip time unknown','status':'FAILED source reconstruction, diagnostic only'})
 paths=[P/f'renders/R06/{mode}_CHECK_{i:02d}.png' for i in range(1,9)]
 if all(p.exists() for p in paths):
  contact=Image.new('RGB',(1200,742),(35,35,35));d=ImageDraw.Draw(contact)
  for i,p in enumerate(paths):
   im=Image.open(p).convert('RGB');im.thumbnail((396,223));x=i%3*400;y=i//3*247;contact.paste(im,(x,y+22));d.text((x+4,y+4),f'CHECK_{i+1:02d} MODEL DIAGNOSTIC',fill='white')
  contact.save(out/f'{mode}_eight-checks.jpg',quality=93)
(P/'qa/R06-overlay-records.json').write_text(json.dumps(records,indent=2));print('overlays complete',len(records),'expected6')
