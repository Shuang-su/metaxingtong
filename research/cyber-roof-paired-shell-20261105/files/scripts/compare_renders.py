from PIL import Image,ImageDraw
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent.parent;rows=[]
for n in ['10','11']:
 src=Image.open(P/'sources'/f'{n}.webp').convert('RGB');images=[src]
 for state in ['baseline','candidate']:
  im=Image.open(P/'renders'/f'{state}-source{n}-8s.png').convert('RGB');assert im.size==src.size==(1192,671);out=Image.blend(src,im,.5);out.save(P/'renders'/f'{state}-source{n}-direct50.png');images.append(im)
 contact=Image.new('RGB',(1192,3*701),(10,10,10));d=ImageDraw.Draw(contact)
 for i,(label,im) in enumerate(zip(['SOURCE original non-native / unknown timestamp','R05 baseline a=.74 / original camera and lighting / 8 samples','IN-MEMORY candidate a=.55 / pair shifts + rigid rings / 8 samples / SOURCE FAILED'],images)):
  d.text((8,i*701+8),label,fill='white');contact.paste(im,(0,i*701+30))
 contact.save(P/'renders'/f'source{n}-before-after.png')
for f in sorted((P/'renders').glob('*.png')):
 im=Image.open(f);rows.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'size':list(im.size)})
(P/'renders/image-manifest.json').write_text(json.dumps(rows,indent=2))
