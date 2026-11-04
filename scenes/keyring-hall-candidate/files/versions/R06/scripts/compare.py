from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];out=R/'comparisons';out.mkdir(exist_ok=True);records=[]
for n in [17,20,21]:
 src=ROOT/'sources'/f'{n}.webp';im=Image.open(src).convert('RGB');assert im.size==(1192,671)
 for variant in ['material','white']:
  p=R/'renders'/f'{"white-" if variant=="white" else ""}source{n}-conditional.png';render=Image.open(p).convert('RGB');assert render.size==im.size
  over=Image.blend(im,render,.5);op=out/f'source{n}-{variant}-direct50.png';over.save(op)
  for role,path in [('source',src),('render',p),('direct50',op)]:records.append({'source':n,'variant':variant,'role':role,'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions':im.size,'transform':'none; direct same-grid RGB Pillow.blend alpha0.5' if role=='direct50' else 'none'})
  sheet=Image.new('RGB',(1192*3,671));sheet.paste(im,(0,0));sheet.paste(render,(1192,0));sheet.paste(over,(2384,0));sheet.save(out/f'source{n}-{variant}-source-render-overlay.png')
# Local crops do not add source baselines; no resizing or warping.
crops=[(17,'key-arc',(0,330,1192,510)),(20,'piano-bench',(800,200,1192,671)),(21,'key-arc',(0,330,1192,560)),(21,'piano',(630,540,880,671)),(21,'star-stage',(200,510,950,671))]
for n,obj,box in crops:
 src=Image.open(ROOT/'sources'/f'{n}.webp').convert('RGB');ren=Image.open(R/'renders'/f'source{n}-conditional.png').convert('RGB');over=Image.blend(src,ren,.5);w,h=box[2]-box[0],box[3]-box[1];sheet=Image.new('RGB',(w*3,h))
 for i,im in enumerate([src,ren,over]):sheet.paste(im.crop(box),(w*i,0))
 sheet.save(out/f'crop-{n}-{obj}-source-render-overlay.png')
(R/'docs/comparison-manifest.json').write_text(json.dumps({'model_commit':'130b5632b838729af6b97059849972d60640b924','material_blend_sha256':'591c0347a4ab63be9f7c6028058874d846fb16e3ba10c5e4c18775a40ed06d06','white_blend_sha256':'0c50e2b00305eb6335fed61bb163377e5754e8f905f17daf98fbdf929b48ea66','sources':'report WebP, not native; times unknown','records':records,'crops':[{'source':n,'object':obj,'xyxy':b,'resized':False} for n,obj,b in crops]},indent=2))
shutil.copyfile(R/'renders/inspection-05.png',R/'renders/main-material.png')
# Contact sheets are explicitly scaled diagnostic derivatives, originals retained.
for variant in ['material','white']:
 sheet=Image.new('RGB',(596*4,360*2));d=ImageDraw.Draw(sheet)
 for i in range(8):
  p=R/'renders'/f'{"white-" if variant=="white" else ""}inspection-{i+1:02}.png';im=Image.open(p).convert('RGB');im.thumbnail((596,336));sheet.paste(im,(i%4*596,i//4*360));d.text((i%4*596,i//4*360+337),f'{variant} inspection {i+1:02} | scaled 50%',fill='white')
 sheet.save(out/f'{variant}-eight-inspections-contact.png')
