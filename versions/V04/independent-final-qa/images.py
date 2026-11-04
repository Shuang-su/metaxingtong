from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).parent;R=O.parent/'dreamfold-phone-study-20261104';V=R/'versions/V04'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.load(open(V/'qa/render-manifest.json'));out={'manifest_exact':True,'records':rows,'overlays':[],'states':[]}
for r in rows:
 p=V/r['path'];im=Image.open(p);out['manifest_exact'] &= sha(p)==r['sha256'] and p.stat().st_size==r['bytes'] and list(im.size)==r['size'] and im.mode==r['mode']
 if im.mode=='RGBA':out['manifest_exact'] &= list(im.getchannel('A').getbbox())==r['alpha_bbox']
a=np.array(Image.open(R/'sources/reta2-7.img').convert('RGB')).astype('uint16')
for mode in ['material','white']:
 im=Image.open(V/f'renders/{mode}-source7.png');bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);b=np.array(bg.convert('RGB')).astype('uint16');c=np.array(Image.open(V/f'renders/{mode}-source7-direct50.png'));out['overlays'].append({'variant':mode,'max_error':int(abs(c.astype(int)-((a+b)//2).astype(int)).max())})
for r in json.load(open(V/'qa/actual-render-states.json')):
 mode='white' if 'white-' in r['file'] else 'material';state=json.load(open(V/f'qa/{mode}-scene-state.json'));cam=state['cameras'][r['camera']];out['states'].append({'file':r['file'],'model_hash_matches':r['blend_sha256']==sha(V/f'models/phone-{mode}.blend'),'camera_matrix_matches_saved_state':r['matrix_world']==cam['matrix_world'],'camera_lens_matches':r['lens']==cam['lens'],'actual_state':r})
(O/'image-integrity.json').write_text(json.dumps(out,indent=2));print(out['manifest_exact'],out['overlays'],[(r['model_hash_matches'],r['camera_matrix_matches_saved_state']) for r in out['states']])
