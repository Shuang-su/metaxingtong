from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parent;r=p/'frozen'; old=p.parent/'independent-seaside-umbrella-r00-qa-20261105/frozen'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def rgb(f):
 im=Image.open(f);im.load();return np.array(im.convert('RGB'))
out={'head':subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip(),'models':{},'renders':[],'overlays':[],'crops':[]}
for name in ['material.blend','white.blend','material.glb','white.glb','environment.json']:
 f=r/'models'/name
 if not f.exists():f=r/name
 g=old/f.relative_to(r);out['models'][str(f.relative_to(r))]={'sha256':sha(f),'same_technical_input':sha(f)==sha(g)};assert sha(f)==sha(g)
for m in ['material','white']:
 for rec in json.load(open(r/'qa'/f'umbrella-render-{m}-32s.json')):
  f=r/rec['path'];a=rgb(f);assert a.shape==(671,1192,3);assert sha(f)==rec['sha256'];assert f.stat().st_size==rec['bytes'];assert sha(r/'models'/f'{m}.blend')==rec['model_sha256'];out['renders'].append(rec)
 for s in ['03','04']:
  f=r/'renders'/f'umbrella-{m}-SOURCE{s}-direct50.png';a=rgb(r/'source'/f'{s}.webp');b=rgb(r/'renders'/f'umbrella-{m}-SOURCE{s}-32s.png');c=rgb(f);n=int(np.count_nonzero(((a.astype('uint16')+b.astype('uint16'))//2).astype('uint8')!=c));assert n==0;out['overlays'].append({'file':str(f.relative_to(r)),'sha256':sha(f),'checked_channels':int(c.size),'mismatches':n,'formula':'floor((decoded source RGB + render RGB)/2), no warp/mask/resample'})
for s,box in [('03',(960,245,1192,440)),('04',(990,105,1192,330))]:
 f=r/'renders'/f'umbrella-SOURCE{s}-native-size-before-after.png';c=rgb(f);x,y,x2,y2=box;w=x2-x;h=y2-y
 paths=[r/'source'/f'{s}.webp',r/'renders'/f'sign-material-SOURCE{s}-32s.png',r/'renders'/f'umbrella-material-SOURCE{s}-32s.png']
 dif=[]
 for i,q in enumerate(paths):dif.append(int(np.count_nonzero(c[24:24+h,i*w:(i+1)*w]!=rgb(q)[y:y2,x:x2])))
 assert dif==[0]*3;out['crops'].append({'file':str(f.relative_to(r)),'sha256':sha(f),'box':box,'panel_mismatches':dif,'header_excluded_rows':24,'before_sha256':sha(paths[1])})
(p/'check.json').write_text(json.dumps(out,indent=2));print('PASS',len(out['renders']),len(out['overlays']),len(out['crops']))
