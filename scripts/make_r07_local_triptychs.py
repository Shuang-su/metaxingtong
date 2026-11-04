from PIL import Image,ImageDraw
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];out=P/'renders/R07-comparisons';out.mkdir(exist_ok=True);records=[]
for num,name,box in [(13,'SOURCE_13_high',(330,340,815,625)),(21,'SOURCE_21_high',(410,265,790,425))]:
 w,h=box[2]-box[0],box[3]-box[1];im=Image.new('RGB',(3*w,h+26),(35,35,35));d=ImageDraw.Draw(im);files=[P/f'sources/report/{num}.png',P/f'renders/R06/material_{name}.png',P/f'renders/R07/material_{name}.png']
 for i,(p,lab) in enumerate(zip(files,['REPORT SOURCE (not native)','R06 radial inset','R07 parallel-edge hypothesis'])):
  im.paste(Image.open(p).convert('RGB').crop(box),(i*w,26));d.text((i*w+4,6),lab,fill='white')
 target=out/f'material_{name}_local-before-after.png';im.save(target);records.append({'file':str(target.relative_to(P)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'crop_original_pixels':box,'resampled':False,'sources':[{'path':str(p.relative_to(P)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]})
(P/'qa/R07-local-comparison-records.json').write_text(json.dumps(records,indent=2))
