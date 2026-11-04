from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).parent;R=O.parent/'dreamfold-phone-v04-diagnosis-20261104'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.load(open(R/'frozen-manifest.json'));out={'manifest_files':len(m),'manifest_exact':all(sha(R/x['path'])==x['sha256'] and (R/x['path']).stat().st_size==x['bytes'] for x in m),'images':[],'overlays':[]}
a=np.array(Image.open(R/'source7-original.img').convert('RGB')).astype('uint16')
for n in [40,45]:
 p=R/f'preview-angle-{n}.png';im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,(0,0,0,255));b=np.array(Image.alpha_composite(bg,im).convert('RGB')).astype('uint16');c=np.array(Image.open(R/f'preview-angle-{n}-direct50.png').convert('RGB'));out['overlays'].append({'angle':n,'black_alpha_then_floor50_max_error':int(abs(c.astype(int)-((a+b)//2).astype(int)).max())})
for n in ['preview-angle-40.png','preview-angle-45.png','preview-angle-45-side.png']:
 p=R/n;im=Image.open(p);out['images'].append({'file':n,'sha256':sha(p),'size':im.size})
(O/'images.json').write_text(json.dumps(out,indent=2));print(out)
