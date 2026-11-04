import json,pathlib,numpy as np,hashlib
from PIL import Image
p=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-tabletop-qa-20261104');out={'renders':[],'crops':[]}
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for r in json.loads((p/'qa/R11-render-records.json').read_text()):
 f=p/r['path'];out['renders'].append({'path':r['path'],'sha256':sha(f),'hash_pass':sha(f)==r['sha256'],'bytes_pass':f.stat().st_size==r['bytes'],'size':Image.open(f).size,'model_hash_pass':sha(p/r['model'])==r['model_sha256']})
for r in json.loads((p/'qa/R11-crop-records.json').read_text()):
 a=np.array(Image.open(p/r['output']).convert('RGB'));b=np.concatenate([np.array(Image.open(p/s['path']).convert('RGB').crop(r['crop_box']))for s in r['sources']],axis=0)
 out['crops'].append({'path':r['output'],'sha256':sha(p/r['output']),'hash_pass':sha(p/r['output'])==r['sha256'],'max_error':int(np.abs(a.astype(int)-b.astype(int)).max())})
(q/'R11-images.json').write_text(json.dumps(out,indent=2));print(out)
