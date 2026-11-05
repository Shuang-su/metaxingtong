from pathlib import Path
import json,hashlib,subprocess,collections
from PIL import Image
P=Path('/workspace/scratch/fa58bfcf0425/cyber-roof-cloud-r06-20261105');Q=Path(__file__).parent
old=json.loads((P/'models/roof-r06b-recovery.json').read_text());new=json.loads((P/'models/roof-r06b-recovery-description-corrected.json').read_text());c=json.loads((P/'research-r06/render-products-correction.json').read_text())
r={'head':subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip(),'changes_from_basis':subprocess.check_output(['git','-C',str(P),'diff','--name-status',c['basis'],'HEAD'],text=True),'changed_keys':[k for k in old.keys()|new.keys()if old.get(k)!=new.get(k)],'other_fields_equal':{k:old[k]==new[k]for k in old if k!='render_products'},'restore_script_mentions_render_products':'render_products' in (P/'scripts/restore_r06b_glb.py').read_text(),'counts':{},'files':[]}
for key in ['actual_new_renders','historical_inherited_pngs','new_derived_comparisons']:
 r['counts'][key]=len(c[key])
 for a in c[key]:
  f=P/a['path'];im=Image.open(f);im.load();r['files'].append({'path':a['path'],'group':key,'hash_equal':hashlib.sha256(f.read_bytes()).hexdigest()==a['sha256'],'bytes_equal':f.stat().st_size==a['bytes'],'dimensions_equal':list(im.size)==a['dimensions'],'script_exists':(P/a['script']).exists()if 'script'in a else None})
r['roles']=dict(collections.Counter(a['role']for a in c['actual_new_renders']));r['renders_history_complete']=set(str(p.relative_to(P))for p in (P/'renders').glob('*.png'))==set(a['path']for a in c['historical_inherited_pngs'])
prior=json.loads(Path('/workspace/scratch/fa58bfcf0425/independent-cyber-cloud-r06b-qa-20261105/image-integrity.json').read_text());r['original_models_unchanged']={p:hashlib.sha256((P/p).read_bytes()).hexdigest()==h for p,h in prior['models'].items()};r['previous_image_hashes_unchanged']={a['path']:hashlib.sha256((P/a['path']).read_bytes()).hexdigest()==a['sha256']for a in prior['images']}
r['metadata_sha']={p:hashlib.sha256((P/p).read_bytes()).hexdigest()for p in ['models/roof-r06b-recovery.json','models/roof-r06b-recovery-description-corrected.json','research-r06/render-products-correction.json','research-r06/render-products-correction.zh.md']}
(Q/'check.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items()if k not in ['files','previous_image_hashes_unchanged','other_fields_equal']});print('allfile',all(x['hash_equal']and x['bytes_equal']and x['dimensions_equal']for x in r['files']));print('priorimages',all(r['previous_image_hashes_unchanged'].values()))
