from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
P=Path('/workspace/scratch/fa58bfcf0425/cyber-roof-cloud-r06-20261105');Q=Path(__file__).parent
rows=[]
for f in sorted((P/'research-r06').glob('*r06b*.png')):
 im=Image.open(f);im.load();rows.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'size':im.size,'mode':im.mode})
r={'images':rows,'models':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in (P/'models').glob('*r06b*')},'overlay':[]}
for n in [10,11]:
 s=np.asarray(Image.open(P/f'sources/{n}.webp').convert('RGB')).astype('uint16');t=np.asarray(Image.open(P/f'research-r06/r06b-experiment-SOURCE{n}.png').convert('RGB')).astype('uint16');o=np.asarray(Image.open(P/f'research-r06/source{n}-r06b-direct50.png').convert('RGB'));r['overlay'].append({'source':n,'dimensions':list(o.shape),'max_abs_floor50_error':int(np.abs(o.astype(int)-((s+t)//2).astype(int)).max())})
(Q/'image-integrity.json').write_text(json.dumps(r,indent=2));print(r['overlay'])
