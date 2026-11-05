from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from PIL import Image
P=Path('/workspace/scratch/fa58bfcf0425/cyber-roof-paired-shell-study-20261105');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'head':subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip(),'images':[],'overlays':[],'strips':[],'recipes':{}}
for x in json.loads((P/'renders/image-manifest.json').read_text()):
 p=P/x['path'];im=Image.open(p);im.load();r['images'].append({'path':x['path'],'sha256':sha(p),'sha_match':sha(p)==x['sha256'],'bytes_match':p.stat().st_size==x['bytes'],'size_match':list(im.size)==x['size'],'mode':im.mode,'alpha_range':im.getchannel('A').getextrema() if 'A' in im.getbands() else None})
for n in ['10','11']:
 a=np.array(Image.open(P/f'sources/{n}.webp').convert('RGB'));panels=[a]
 for st in ['baseline','candidate']:
  im=P/f'renders/{st}-source{n}-8s.png';b=np.array(Image.open(im).convert('RGB'));c=np.array(Image.open(P/f'renders/{st}-source{n}-direct50.png').convert('RGB'));expected=((a.astype('uint16')+b.astype('uint16'))//2).astype('uint8');r['overlays'].append({'source':n,'state':st,'shape':list(c.shape),'mismatch_channels':int(np.count_nonzero(c!=expected))});panels.append(b)
  rec=json.loads((P/f'renders/{st}-source{n}-recipe.json').read_text());r['recipes'][st+n]=rec
  assert rec['image_sha256']==sha(im) and rec['bytes']==im.stat().st_size
  assert rec['construction_script_sha256']==sha(P/'scripts/single_pair_candidate.py') and rec['render_script_sha256']==sha(P/'scripts/render_single_diagnostic.py')
  assert rec['input_sha256']==sha(P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend')
 strip=np.array(Image.open(P/f'renders/source{n}-before-after.png').convert('RGB'))
 r['strips'].append({'source':n,'panel_mismatches':[int(np.count_nonzero(strip[i*701+30:i*701+701]!=p)) for i,p in enumerate(panels)],'header_excluded':30})
r['recipe_comparison']={}
for n in ['10','11']:
 a=r['recipes']['baseline'+n];b=r['recipes']['candidate'+n];skip={'mode','parameter','actual_mesh_hashes','actual_geometry_collection_sha256','image_sha256','bytes'}
 r['recipe_comparison'][n]={'other_field_differences':[k for k in a if k not in skip and a[k]!=b[k]],'changed_meshes':[k for k in a['actual_mesh_hashes'] if a['actual_mesh_hashes'][k]!=b['actual_mesh_hashes'][k]]}
r['cross_camera_geometry_equal']={s:r['recipes'][s+'10']['actual_mesh_hashes']==r['recipes'][s+'11']['actual_mesh_hashes'] for s in ['baseline','candidate']}
(O/'check.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['recipes','images']},indent=2))
