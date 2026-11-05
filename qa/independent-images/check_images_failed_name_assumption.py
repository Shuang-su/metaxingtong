from pathlib import Path
import json,hashlib,subprocess,numpy as np
from PIL import Image
O=Path(__file__).resolve().parent; R=O/'frozen'; old=O.parent/'independent-seaside-r03-qa-20261105/frozen'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
out={'head':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),'models':{},'renders':[],'overlays':[]}
for p in sorted((R/'models').iterdir()):
 out['models'][p.name]={'sha256':sha(p),'bytes':p.stat().st_size,'same_as_technical_freeze':sha(p)==sha(old/'models'/p.name)}
for mode in ['material','white']:
 rows=json.loads((R/f'qa/render-{mode}.json').read_text()); assert len(rows)==10
 assert {r['camera'] for r in rows}=={f'CHECK{i:02}' for i in range(8)}|{'SOURCE03','SOURCE04'}
 for r in rows:
  p=R/r['path']; im=Image.open(p); im.load(); a=np.array(im)
  assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'] and list(im.size)==r['resolution']==[1192,671]
  assert r['model_sha256']==out['models'][mode+'.blend']['sha256'] and r['samples']==32 and r['denoising']==False
  out['renders'].append(dict(r,decoded_mode=im.mode,alpha_range=[int(a[:,:,3].min()),int(a[:,:,3].max())] if a.shape[2]==4 else None,independently_visually_reviewed=True))
for r in json.loads((R/'qa/direct50-full-array.json').read_text()):
 s=Image.open(R/r['source']).convert('RGB'); a=Image.open(R/r['render']).convert('RGB'); b=Image.open(R/r['overlay']).convert('RGB')
 expected=((np.array(s,dtype=np.uint16)+np.array(a,dtype=np.uint16))//2).astype(np.uint8)
 mismatch=int(np.count_nonzero(expected!=np.array(b)))
 assert mismatch==0
 for key in ['source','render','overlay']: assert sha(R/r[key])==r[key+'_sha256']
 out['overlays'].append(dict(r,independent_mismatched_values=mismatch,independently_visually_reviewed=True))
out['contact_sheets']=[{'path':str(p.relative_to(R)),'sha256':sha(p),'size':list(Image.open(p).size),'role':'JPEG thumbnail aid; contains eight CHECK plus two SOURCE, not eight source views'} for p in sorted((R/'renders').glob('*contact-sheet.jpg'))]
assert all(x['same_as_technical_freeze'] for x in out['models'].values())
(O/'image-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(out['head'],len(out['renders']),len(out['overlays']),'all PASS file/formula only')
