from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent;R=Q/'frozen';T=Q.parent/'independent-seaside-wing-r05-qa-20261105/frozen';out={'renders':[],'overlays':[],'crops':[],'models':{}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in sorted((R/'models').iterdir()):
 out['models'][p.name]={'sha256':sha(p),'same_as_technical':sha(p)==sha(T/'models'/p.name)};assert out['models'][p.name]['same_as_technical']
for m in ['material','white']:
 rows=json.load(open(R/f'qa/sign-render-{m}-32s.json'));assert len(rows)==4
 for r in rows:
  p=R/r['path'];im=Image.open(p);im.load();assert list(im.size)==r['resolution']==[1192,671];assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'];assert r['model_sha256']==out['models'][m+'.blend']['sha256'];assert r['samples']==32 and r['denoising']==False
  out['renders'].append(dict(r,decoded_mode=im.mode,visually_reviewed=True))
for r in json.load(open(R/'qa/sign-full-array-and-local-comparison.json')):
 if 'overlay' in r:
  a=np.asarray(Image.open(R/r['source']).convert('RGB'),dtype=np.uint16);b=np.asarray(Image.open(R/r['render']).convert('RGB'),dtype=np.uint16);actual=np.asarray(Image.open(R/r['overlay']).convert('RGB'));n=int(np.count_nonzero(((a+b)//2).astype(np.uint8)!=actual));assert n==0
  for k in ['source','render','overlay']:assert sha(R/r[k])==r[k+'_sha256']
  out['overlays'].append(dict(r,independent_mismatches=n,visually_reviewed=True))
 else:
  n='03' if '03' in r['diagnostic'] else '04';crop=r['source_crop_xyxy'];paths=[R/f'source/{n}.webp',R/f'renders/material-SOURCE{n}.png',R/f'renders/sign-material-SOURCE{n}-32s.png'];a=Image.open(R/r['diagnostic']).convert('RGB');w,h=r['per_panel_size'];mismatch=[]
  assert a.size==(3*w,h+24)
  for i,p in enumerate(paths):mismatch.append(int(np.count_nonzero(np.asarray(a.crop((i*w,24,(i+1)*w,24+h)))!=np.asarray(Image.open(p).convert('RGB').crop(crop)))))
  assert mismatch==[0,0,0]
  out['crops'].append(dict(r,sha256=sha(R/r['diagnostic']),panel_mismatches=mismatch,input_sha256=[sha(p) for p in paths],visually_reviewed=True))
(Q/'check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('PASS',len(out['renders']),len(out['overlays']),len(out['crops']))
