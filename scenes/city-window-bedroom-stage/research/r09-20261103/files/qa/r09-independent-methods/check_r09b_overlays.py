from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
P=Path('/workspace/scratch/fa58bfcf0425/cityroom-refinement-20261103');O=Path(__file__).parent
out=[]
for f in sorted((P/'comparisons/R09b').glob('*-direct50.json')):
 d=json.load(open(f));ims=[Image.open(P/d[k]).convert('RGB') for k in ['source','render','output']];a,b,c=[np.asarray(i,dtype=np.int16) for i in ims];out.append({'metadata':str(f.relative_to(P)),'render':d['render'],'sizes':[i.size for i in ims],'max_formula_error':int(np.abs((a+b)//2-c).max()),'hashes':{k:hashlib.sha256((P/d[k]).read_bytes()).hexdigest() for k in ['source','render','output']},'metadata_hash_match':all(hashlib.sha256((P/d[k]).read_bytes()).hexdigest()==d[k+'_sha256'] for k in ['source','render','output'])})
(O/'R09b-overlay-integrity-independent.json').write_text(json.dumps(out,indent=2));print([(x['metadata'],x['max_formula_error'],x['metadata_hash_match']) for x in out])
