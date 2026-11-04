import pathlib,json,hashlib
from PIL import Image
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-qa-20261104');rs=json.load(open(P/'qa/R06-render-records.json'));out=[]
for r in rs:
 f=P/r['file'];im=Image.open(f);im.load();out.append({'path':r['file'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'hash_matches':hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],'bytes_match':f.stat().st_size==r['bytes'],'actual_size':list(im.size),'size_matches':list(im.size)==r['resolution'],'model_hash_matches':hashlib.sha256((P/r['model']).read_bytes()).hexdigest()==r['model_sha256'],'camera':r['camera'],'samples':r['samples'],'denoise':r['denoise']})
(Q/'R06-render-integrity.json').write_text(json.dumps({'count':len(out),'records':out},indent=2));print('count',len(out),'bad',[x for x in out if not all(x[k] for k in ['hash_matches','bytes_match','size_matches','model_hash_matches'])])
