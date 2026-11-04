from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json
R=Path('/workspace/scratch/fa58bfcf0425/dreamfold-phone-study-20261104'); V=R/'versions/V03'; O=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=json.loads((V/'qa/white-image-manifest.json').read_text());out={'files':[]}
for r in records:
 p=R/r['file']; im=Image.open(p); im.load(); x={'file':r['file'],'sha256':sha(p),'bytes':p.stat().st_size,'size':list(im.size),'mode':im.mode};x['record_matches']=all(x[k]==r[k] for k in ['sha256','bytes','size'])
 if im.mode=='RGBA':x['alpha_bbox']=list(im.getchannel('A').getbbox());x['alpha_bbox_record_matches']=x['alpha_bbox']==r['alpha_bbox']
 out['files'].append(x)
s=Image.open(R/'sources/reta2-7.img').convert('RGB');a=Image.open(V/'renders/white-source7.png').convert('RGBA');black=Image.new('RGBA',a.size,(0,0,0,255));black.alpha_composite(a)
expected=(np.array(s,dtype=np.uint16)+np.array(black.convert('RGB'),dtype=np.uint16))//2
actual=np.array(Image.open(V/'renders/white-source7-direct-50pct.png').convert('RGB'));err=np.abs(expected.astype(int)-actual.astype(int));out['direct50']={'max_channel_error':int(err.max()),'different_channels':int(np.count_nonzero(err)),'formula':'floor((sourceRGB + RGBA render alpha-composited over black RGB)/2), native full arrays, no warp/rescale'}
out['source_sha256']=sha(R/'sources/reta2-7.img');out['model_sha256']=sha(V/'models/phone-white.blend');out['scripts']={str(p.relative_to(R)):sha(p) for p in [V/'scripts/render-white-checks.py',V/'scripts/white-overlay.py']}
(O/'white-image-integrity.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
