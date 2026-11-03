from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
p=Path('/workspace/shared/metaxingtong-production-20261103'); out=Path('/workspace/shared/novelty-review-20261103/qa')
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
r={'method':'Independent full-array RGB uint16 sum // 2; no resampling. Formula correctness is not geometric acceptance.','models':{},'renders':[],'overlays':[]}
for f in sorted((p/'models'/name) for name in ['R08_material.blend','R08_white.blend','R08_material.glb','R08_white.glb']):
 if f.suffix in ['.blend','.glb']:r['models'][f.name]=h(f)
for f in sorted([*(p/'renders/R08_material').glob('*.png'),*(p/'renders/R08_white').glob('*.png')]):
 im=Image.open(f); im.load();r['renders'].append({'path':str(f.relative_to(p)),'sha256':h(f),'size':im.size,'nonblank':len(im.getextrema())>0 and any(a!=b for a,b in im.convert('RGB').getextrema())})
for f in sorted((p/'comparisons/R08').glob('*-direct50.json')):
 m=json.loads(f.read_text()); files=[p/m[k] for k in ['source','render','output']]; ims=[Image.open(x).convert('RGB') for x in files]; arrays=[np.asarray(x,dtype=np.uint16) for x in ims]; same=len(set(x.size for x in ims))==1
 r['overlays'].append({'metadata':str(f.relative_to(p)),'sizes':[i.size for i in ims],'same_size':same,'max_formula_error':int(np.abs((arrays[0]+arrays[1])//2-arrays[2]).max()) if same else None,'hashes_match_metadata':all(h(ff)==m[k+'_sha256'] for ff,k in zip(files,['source','render','output']))})
r['all_28_render_files_present']=len(r['renders'])==28;r['all_12_overlay_files_present']=len(r['overlays'])==12
(out/'R08-final-image-integrity-independent.json').write_text(json.dumps(r,indent=2));print(len(r['renders']),len(r['overlays']),r['models'])
