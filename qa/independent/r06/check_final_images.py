from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).parent;R=Path('/workspace/scratch/fa58bfcf0425/keyring-hall-candidate-20261104');V=R/'versions/R06';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();im=lambda p:np.array(Image.open(p).convert('RGB'));out={}
manifest=json.loads((V/'docs/comparison-manifest.json').read_text());out['manifest_sha']=sha(V/'docs/comparison-manifest.json');out['records']=[]
for rec in manifest['records']:
 p=R/rec['path'];out['records'].append({'path':rec['path'],'sha_match':sha(p)==rec['sha256'],'bytes_match':p.stat().st_size==rec['bytes'],'size_match':list(Image.open(p).size)==rec['dimensions']})
out['render_inventory']=[]
for p in sorted((V/'renders').glob('*.png')):
 a=Image.open(p);a.load();out['render_inventory'].append({'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size,'size':list(a.size),'channel255_fraction':float(np.mean(np.array(a.convert('RGB'))==255))})
out['overlay_checks']=[];out['strip_checks']=[]
for n in [17,20,21]:
 a=im(R/f'sources/{n}.webp').astype(np.uint16)
 for v in ['material','white']:
  b=im(V/f'renders/{"white-" if v=="white" else ""}source{n}-conditional.png').astype(np.uint16);c=((a+b)//2).astype(np.uint8);p=V/f'comparisons/source{n}-{v}-direct50.png';out['overlay_checks'].append({'path':str(p.relative_to(R)),'sha256':sha(p),'max_error':int(abs(c.astype(int)-im(p).astype(int)).max())});st=V/f'comparisons/source{n}-{v}-source-render-overlay.png';out['strip_checks'].append({'path':str(st.relative_to(R)),'sha256':sha(st),'all_pixels_equal':bool(np.array_equal(im(st),np.concatenate([a.astype(np.uint8),b.astype(np.uint8),c],axis=1)))})
out['crop_checks']=[]
for q in manifest['crops']:
 n=q['source'];x1,y1,x2,y2=q['xyxy'];a=im(R/f'sources/{n}.webp').astype(np.uint16);b=im(V/f'renders/source{n}-conditional.png').astype(np.uint16);c=((a+b)//2).astype(np.uint8);expected=np.concatenate([i[y1:y2,x1:x2].astype(np.uint8) for i in [a,b,c]],axis=1);p=V/f'comparisons/crop-{n}-{q["object"]}-source-render-overlay.png';out['crop_checks'].append({'path':str(p.relative_to(R)),'sha256':sha(p),'size':list(Image.open(p).size),'all_pixels_equal':bool(np.array_equal(expected,im(p)))})
out['models']={p.name:sha(p) for p in (V/'models').glob('*') if p.suffix in ['.blend','.glb']};old=json.loads((O/'check.json').read_text());out['model_hashes_unchanged']=out['models']==old['hashes'];out['material_images_unchanged']=all(sha(R/i['file'])==i['sha256'] for i in json.loads((O/'material-image-integrity.json').read_text())['images']);out['main_alias_exact']=sha(V/'renders/main-material.png')==sha(V/'renders/inspection-05.png');(O/'final-image-integrity.json').write_text(json.dumps(out,indent=2));print({'renders':len(out['render_inventory']),'record_matches':all(all(x[k] for k in ['sha_match','bytes_match','size_match']) for x in out['records']),'overlay_errors':[x['max_error'] for x in out['overlay_checks']],'strips':all(x['all_pixels_equal'] for x in out['strip_checks']),'crops':all(x['all_pixels_equal'] for x in out['crop_checks']),'model_unchanged':out['model_hashes_unchanged'],'material_images_unchanged':out['material_images_unchanged']})
