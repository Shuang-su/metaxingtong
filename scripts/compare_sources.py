from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];O=R/'comparisons';O.mkdir(exist_ok=True);rows=[]
for n in [17,20,21]:
 src=R/'inputs'/f'{n}.webp';a=Image.open(src).convert('RGB');assert a.size==(1192,671)
 for v in ['material','white']:
  p=R/'renders'/f'{v}-source{n}-conditional.png';b=Image.open(p).convert('RGB');assert b.size==a.size;o=O/f'source{n}-{v}-direct50.png';im=Image.blend(a,b,.5);im.save(o);sheet=Image.new('RGB',(3576,671));sheet.paste(a,(0,0));sheet.paste(b,(1192,0));sheet.paste(im,(2384,0));sheet.save(O/f'source{n}-{v}-source-render-overlay.png')
  for q,role in [(src,'original report WebP; not native frame'),(p,'actual R07 source-camera render, not reused R06'),(o,'direct 50% RGB same-grid overlay')]:rows.append({'path':str(q.relative_to(R)),'role':role,'bytes':q.stat().st_size,'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'size':[1192,671]})
shutil.copyfile(R/'renders/material-inspection-05.png',R/'renders/main-material.png')
a=Image.open(R/'renders/diagnostic-b-baseline.png').convert('RGB');b=Image.open(R/'renders/diagnostic-b-candidate.png').convert('RGB');assert a.size==b.size==(1192,671);pair=Image.new('RGB',(2384,695));pair.paste(a,(0,24));pair.paste(b,(1192,24));d=ImageDraw.Draw(pair);d.text((8,5),'R06 BEFORE | same camera/fill | LEFT: outer gap r6.01 | RIGHT: inner gap r5.01',fill='white');d.text((1200,5),'R07B AFTER | inferred low connectors | LEFT: r6.01 | RIGHT: r5.01 | local view only',fill='white');pair.save(O/'diagnostic-b-before-after.png')
(R/'docs/comparison-manifest.json').write_text(json.dumps({'records':rows,'main_role':'byte-identical material inspection05 alias; actual new R07 normal main, not source-aligned','diagnostic_role':'Two actual images with same added light/camera; no objects hidden; only local bottom joints, not full circumference','source_status':'FAILED, source image timestamp and native decode unknown'},indent=2))
