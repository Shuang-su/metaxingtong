from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).parent;R=O.parent/'keyring-underbridge-r07-20261104'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGB'))
files=[f'{v}-source{n}-conditional.png' for v in ['material','white'] for n in [17,20,21]]+['material-inspection-05.png','diagnostic-b-baseline.png','diagnostic-b-candidate.png']
out={'raw':[],'overlays':[],'strips':[]}
for f in files:
 p=R/'renders'/f;im=Image.open(p);a=np.array(im);out['raw'].append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'size':im.size,'mode':im.mode,'alpha_range':[int(a[:,:,3].min()),int(a[:,:,3].max())] if a.shape[-1]==4 else None})
for n in [17,20,21]:
 a=arr(R/f'inputs/{n}.webp')
 for v in ['material','white']:
  b=arr(R/f'renders/{v}-source{n}-conditional.png');c=arr(R/f'comparisons/source{n}-{v}-direct50.png');expected=((a.astype('uint16')+b.astype('uint16'))//2).astype('uint8');out['overlays'].append({'source':n,'variant':v,'max_error':int(abs(c.astype(int)-expected.astype(int)).max())});s=arr(R/f'comparisons/source{n}-{v}-source-render-overlay.png');out['strips'].append({'source':n,'variant':v,'all_pixels_equal':bool(np.array_equal(s,np.concatenate([a,b,c],axis=1)))})
pair=arr(R/'comparisons/diagnostic-b-before-after.png');out['diagnostic_pair_pixels_equal']=bool(np.array_equal(pair[24:],np.concatenate([arr(R/'renders/diagnostic-b-baseline.png'),arr(R/'renders/diagnostic-b-candidate.png')],axis=1)))
rows=json.load(open(R/'docs/comparison-manifest.json'))['records'];out['manifest_records']=len(rows);out['manifest_exact']=all(sha(R/x['path'])==x['sha256'] and (R/x['path']).stat().st_size==x['bytes'] and list(Image.open(R/x['path']).size)==x['size'] for x in rows)
out['main_alias_exact']=sha(R/'renders/main-material.png')==sha(R/'renders/material-inspection-05.png')
rec=json.load(open(R/'docs/render-records.json'));out['seven_render_model_records_match']=all(x['model_sha256']==sha(R/('models/r07b-white.blend' if x['file'].split('/')[-1].startswith('white') else 'models/r07b-material.blend')) for x in rec)
d=json.load(open(R/'docs/diagnostic-render-state.json'));out['diagnostic_state_keys']=[list(x) for x in d];out['diagnostic_lights_equal']=d[0]['lights']==d[1]['lights'];out['diagnostic_world_equal']=all(d[0][k]==d[1][k] for k in ['world_background','world_strength'])
out['diagnostic_camera_exact']=all(d[0][k]==d[1][k] for k in ['camera_matrix','camera_lens'])
(O/'image-integrity.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
