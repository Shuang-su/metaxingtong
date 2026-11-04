from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).parent;R=Path('/workspace/scratch/fa58bfcf0425/keyring-hall-candidate-20261104');V=R/'versions/R06';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out={'models':{p.name:sha(p) for p in (V/'models').glob('*') if p.suffix in ['.blend','.glb']},'images':[],'overlays':[]}
for p in sorted((V/'renders').glob('*.png')):
 if p.name.startswith('white-'):continue
 im=Image.open(p);im.load();out['images'].append({'file':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size,'size':list(im.size),'mode':im.mode,'alpha_range':list(im.getchannel('A').getextrema()) if im.mode=='RGBA' else None})
for n in [17,20,21]:
 s=R/f'sources/{n}.webp';r=V/f'renders/source{n}-conditional.png';p=V/f'comparisons/source{n}-material-direct50.png';a=np.array(Image.open(s).convert('RGB'),dtype=np.uint16);b=np.array(Image.open(r).convert('RGB'),dtype=np.uint16);c=np.array(Image.open(p).convert('RGB'),dtype=np.uint16);e=np.abs(((a+b)//2).astype(int)-c.astype(int));out['overlays'].append({'file':str(p.relative_to(R)),'sha256':sha(p),'source_sha':sha(s),'render_sha':sha(r),'size':list(Image.open(p).size),'bytes':p.stat().st_size,'max_channel_error':int(e.max()),'different_channels':int(np.count_nonzero(e))})
out['main_exact_alias_inspection05']=sha(V/'renders/main-material.png')==sha(V/'renders/inspection-05.png');(O/'material-image-integrity.json').write_text(json.dumps(out,indent=2));print(json.dumps({'images':len(out['images']),'alias':out['main_exact_alias_inspection05'],'errors':[x['max_channel_error'] for x in out['overlays']]}))
