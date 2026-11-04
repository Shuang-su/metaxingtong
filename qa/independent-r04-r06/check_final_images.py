from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
p=Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');q=Path(__file__).resolve().parent
rows=[]
for r in json.load(open(p/'qa/R06-overlay-records.json')):
 a,b,c=[np.array(Image.open(p/r[k]).convert('RGB'),dtype=np.uint16) for k in ['source','render','overlay']];target=(a+b+1)//2
 rows.append({'record':r,'hashes_match':{k:hashlib.sha256((p/r[k]).read_bytes()).hexdigest()==r[k+'_sha256'] for k in ['source','render','overlay']},'shape':list(a.shape),'max_error':int(np.max(abs(c.astype(int)-target.astype(int)))),'different_channels':int(np.count_nonzero(c!=target))})
(q/'R06-overlays-all6.json').write_text(json.dumps(rows,indent=2))
records=json.load(open(p/'qa/R06-render-records.json'));out=[]
for r in records:
 f=p/r['file'];im=Image.open(f);im.load();out.append({'record':r,'sha_match':hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],'bytes_match':f.stat().st_size==r['bytes'],'resolution_match':list(im.size)==r['resolution'],'model_sha_match':hashlib.sha256((p/r['model']).read_bytes()).hexdigest()==r['model_sha256']})
(q/f'R06-render-integrity-{len(out)}.json').write_text(json.dumps(out,indent=2));print('overlays',len(rows),'renders',len(out),'all pass',all(all(v for k,v in o.items() if k!='record') for o in out))
