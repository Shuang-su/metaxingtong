import pathlib,json,hashlib,numpy as np
from PIL import Image
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/backstage-local-study-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-backstage-layout-qa-20261104');R={}
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for ver in ['R12','R13']:
 r=[]
 for e in json.load(open(P/'qa'/f'{ver}-render-records.json')):
  f=P/e['path'];im=Image.open(f);im.load();r.append({'path':e['path'],'sha256':sha(f),'record_sha_match':sha(f)==e['sha256'],'bytes_match':len(f.read_bytes())==e['bytes'],'dimensions':im.size,'dimensions_match':list(im.size)==e['resolution'],'model':e['model'],'model_sha256':sha(P/e['model']),'model_sha_match':sha(P/e['model'])==e['model_sha256'],'camera':e['camera'],'camera_matrix':e['camera_matrix'],'samples':e['samples'],'denoise':e['denoise']})
 out={'renders':r,'crops':[]};c=P/'qa'/f'{ver}-crop-records.json'
 if c.exists():
  for e in json.load(open(c)):
   a=np.array(Image.open(P/e['output']).convert('RGB'));parts=[]
   for s in e['sources']:parts.append(np.array(Image.open(P/s['path']).convert('RGB').crop(e['crop_box'])))
   want=np.concatenate(parts,axis=0);out['crops'].append({'path':e['output'],'sha_match':sha(P/e['output'])==e['sha256'],'sources_sha_match':all(sha(P/s['path'])==s['sha256']for s in e['sources']),'max_array_error':int(np.abs(a.astype('int16')-want.astype('int16')).max()),'size':list(Image.open(P/e['output']).size)})
 R[ver]=out
(Q/'R12-R13-image-integrity.json').write_text(json.dumps(R,indent=2));print({k:{'renders':len(v['renders']),'hash_pass':all(e['record_sha_match']and e['model_sha_match']and e['dimensions_match']and e['bytes_match']for e in v['renders']),'crops':v['crops']}for k,v in R.items()})
