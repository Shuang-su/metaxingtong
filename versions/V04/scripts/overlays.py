from PIL import Image
from pathlib import Path
import hashlib,json
V=Path(__file__).resolve().parents[1];R=V.parents[1];source=Image.open(R/'sources/reta2-7.img').convert('RGB')
for variant in ['material','white']:
 a=Image.open(V/f'renders/{variant}-source7.png');assert a.size==source.size==(1080,603);b=Image.new('RGBA',a.size,(0,0,0,255));b.alpha_composite(a);Image.blend(source,b.convert('RGB'),.5).save(V/f'renders/{variant}-source7-direct50.png')
files=[]
for p in sorted((V/'renders').glob('*.png')):
 im=Image.open(p);d={'path':str(p.relative_to(V)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'size':im.size,'mode':im.mode}
 if im.mode=='RGBA':d['alpha_bbox']=im.getchannel('A').getbbox()
 files.append(d)
(V/'qa/render-manifest.json').write_text(json.dumps(files,indent=2))
