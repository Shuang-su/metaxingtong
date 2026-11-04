from PIL import Image,ImageDraw
import pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R06-comparisons';out.mkdir(exist_ok=True);rec=[]
for num,name,box in [(8,'SOURCE_08_wide',(530,240,685,440)),(23,'SOURCE_23_oblique',(650,45,845,230)),(26,'SOURCE_26_side',(330,40,445,190))]:
 paths=[P/f'sources/report/{num:02d}.png',P/f'renders/R06/material_{name}.png',out/f'material_{name}_direct50.png']
 if not all(p.exists() for p in paths):continue
 w,h=box[2]-box[0],box[3]-box[1];im=Image.new('RGB',(w*3,h+24),(30,30,30));d=ImageDraw.Draw(im)
 for i,(p,lab) in enumerate(zip(paths,['REPORT SOURCE','R06 RENDER','DIRECT50 FAILED'])):
  im.paste(Image.open(p).convert('RGB').crop(box),(i*w,24));d.text((i*w+3,5),lab,fill='white')
 f=out/f'{name}_local.png';im.save(f);rec.append({'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'crop_original_pixels':box,'resampling':False,'inputs':[{'path':str(p.relative_to(P)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]})
(P/'qa/R06-local-records.json').write_text(json.dumps(rec,indent=2))
