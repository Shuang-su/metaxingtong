from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path('/workspace/scratch/fa58bfcf0425/cyber-ring-emissive-band-study-20261105');O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();arr=lambda p:np.array(Image.open(p).convert('RGB'));R={'images':[],'current':[],'overlays':[],'contacts':[]}
for x in json.loads((P/'renders/final-image-manifest.json').read_text()):
 f=P/x['path'];im=Image.open(f);im.load();R['images'].append({'path':x['path'],'sha_match':sha(f)==x['sha256'],'bytes_match':f.stat().st_size==x['bytes'],'size_match':list(im.size)==x['size']})
for mode in ['material','white']:
 for view in ['source11','close']:
  f=P/f'renders/v3-{mode}-{view}-32s.png';q=json.loads(f.with_name(f.stem+'-recipe.json').read_text());model=P/('export/roof-led-surface-v3'+('-white' if mode=='white' else '')+'.blend');R['current'].append({'path':str(f),'sha':sha(f),'image_match':sha(f)==q['image_sha256'],'model_match':sha(model)==q['input_sha256'],'script_match':sha(P/'scripts/render_saved_v3.py')==q['script_sha256'],'samples':q['samples'],'alpha_range':Image.open(f).getchannel('A').getextrema()})
 a=arr(P/'sources/11.webp').astype('uint16');b=arr(P/f'renders/v3-{mode}-source11-32s.png').astype('uint16');c=arr(P/f'renders/v3-{mode}-source11-direct50.png');R['overlays'].append({'mode':mode,'mismatch_channels':int(np.count_nonzero(c!=(a+b)//2)),'channels':c.size})
for name,files in [('source11-comparison.png',['sources/11.webp','renders/baseline-source11-8s.png','renders/v3-material-source11-32s.png']),('close-material-white-comparison.png',['renders/baseline-close-8s.png','renders/v3-material-close-32s.png','renders/v3-white-close-32s.png'])]:
 c=arr(P/'renders'/name);R['contacts'].append({'path':name,'mismatch_panels':[int(np.count_nonzero(c[i*701+30:i*701+701]!=arr(P/f))) for i,f in enumerate(files)],'headers_excluded':30})
prior=json.loads((O.parent/'independent-ring-led-v3-qa-20261105/check.json').read_text())['input_hashes'];R['technical_input_unchanged']={n:sha(P/'export'/n)==v for n,v in prior.items()};(O/'check.json').write_text(json.dumps(R,indent=2));print(R)
