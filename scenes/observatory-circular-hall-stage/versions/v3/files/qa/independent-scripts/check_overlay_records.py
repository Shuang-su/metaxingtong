import json,pathlib,hashlib,numpy as np
from PIL import Image
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-qa-20261104')
r=json.load(open(P/'qa/R06-overlay-records.json'));out=[]
for e in r:
 a,b,c=[np.asarray(Image.open(P/e[k]).convert('RGB')) for k in ['source','render','overlay']];d=((a.astype('uint16')+b.astype('uint16')+1)//2).astype('uint8');out.append({'overlay':e['overlay'],'shape':list(c.shape),'different_channels':int(np.count_nonzero(c!=d)),'max_error':int(abs(c.astype('int16')-d.astype('int16')).max()),'hash_matches':{k:hashlib.sha256((P/e[k]).read_bytes()).hexdigest()==e[k+'_sha256'] for k in ['source','render','overlay']},'record':e})
(Q/'R06-overlays-partial-4.json').write_text(json.dumps(out,indent=2));print([(v['overlay'],v['different_channels'],v['hash_matches']) for v in out])
