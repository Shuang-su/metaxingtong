from pathlib import Path
import numpy as np,json,hashlib
R=Path('/workspace/scratch/fa58bfcf0425/keyring-underbridge-r07-20261104');O=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((R/'results/source-primary-visibility.json').read_text());out={'model_hash_matches':sha(R/'models/r07b-material.blend')==d['model_sha256'],'method_script_sha256':sha(R/'scripts/primary_visibility.py'),'summary_sha256':sha(R/'results/source-primary-visibility.json'),'log_sha256':sha(R/'results/source-primary-visibility.log'),'arrays':[],'reran_rays':False}
for x in d['sources']:
 p=R/f"results/source{x['source']}-primary-object-id.npy";a=np.load(p,allow_pickle=False);vals,counts=np.unique(a,return_counts=True);out['arrays'].append({'source':x['source'],'sha256':sha(p),'hash_matches':sha(p)==x['mask_sha256'],'shape':list(a.shape),'dtype':str(a.dtype),'sample_count':int(a.size),'values_counts':dict(zip(map(str,vals),map(int,counts))),'summary_count_match':all(int((a==r['id']).sum())==r['pixel_center_first_hits'] for r in x['counts'])})
(O/'array-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
