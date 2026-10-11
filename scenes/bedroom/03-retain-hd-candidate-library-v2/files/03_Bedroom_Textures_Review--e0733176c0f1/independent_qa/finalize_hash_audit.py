from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path('/workspace/scratch/fa58bfcf0425/bedroom_hd_revision_20261010');O=R/'independent_qa'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected=['candidate_hd_front_material_v2','candidate_hd_front_white','candidate_hd_near_material','candidate_hd_near_white','candidate_old_internal_front']+['normal_'+s for s in ['01_入口看床','02_右前看床','03_左侧沿墙','04_床尾正向','06_反向门窗','07_反向入口','09_门洞近看','10_窗洞近看']]+['normal_white_01','normal_main_hd']
manifest=json.loads((R/'analysis/frozen_inputs_manifest_v2.json').read_text());assets=[{**v,'actual_sha256':sha(v['file']),'matches':sha(v['file'])==v['sha256']} for v in manifest];finals={v['file']:v['sha256'] for v in manifest};results=[]
for n in expected:
 p=R/'renders'/n;j=p.with_suffix('.json');d=R/'renders'/(n+'_denoised.json')
 if not j.exists() or not d.exists():results.append({'name':n,'complete':False});continue
 a=json.loads(j.read_text());b=json.loads(d.read_text());out=Path(a['output']);den=d.with_suffix('.png');results.append({'name':n,'complete':True,'sidecar_sha256':sha(j),'input_file':a['input_file'],'input_sha256':a['input_sha256'],'final_v2_input':a['input_file'] in finals and a['input_sha256']==finals[a['input_file']],'output_sha256':sha(out),'output_matches':sha(out)==a['output_sha256'],'denoised_sha256':sha(den),'denoise_input_matches':b['input_sha256']==sha(out),'denoise_output_matches':b['output_sha256']==sha(den),'clip':a['clip'],'camera':a['camera']})
overlays=[]
for j in sorted((R/'review').glob('*direct50.json')):
 a=json.loads(j.read_text());src=Image.open(a['source']).convert('RGB');ren=Image.open(a['render']).convert('RGB');actual=Image.open(j.with_suffix('.png')).convert('RGB');overlays.append({'file':str(j.with_suffix('.png')),'sha256':sha(j.with_suffix('.png')),'equal_direct_50_percent':bool(np.array_equal(np.array(actual),np.array(Image.blend(src,ren,.5)))),'source_hash_matches':sha(a['source'])==a['source_sha256'],'render_hash_matches':sha(a['render'])==a['render_sha256'],'output_hash_matches':sha(j.with_suffix('.png'))==a['output_sha256']})
old=Path('/workspace/scratch/fa58bfcf0425/bedroom_fullroom/final7p7/models/01_bedroom_material.blend');report={'assets':assets,'old_original_still_frozen':sha(old)==sha(R/'frozen/bedroom_material_v1.blend'),'expected_render_count':len(expected),'renders':results,'overlays':overlays,'review_files':[{'file':str(p),'sha256':sha(p)} for p in sorted((R/'review').glob('*.jpg'))],'all_expected_complete':all(x['complete'] for x in results),'stage1_excluded':['models root four stage1 assets','renders/candidate_hd_front_material.png'],'note':'Checks bind independent QA to actual v2 assets and completed render sidecars. SHA chaining verifies artifact identity, not source reconstruction quality.'};(O/'final_audit_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'complete':report['all_expected_complete'],'count':sum(x['complete'] for x in results),'old_frozen':report['old_original_still_frozen'],'overlays':len(overlays)},indent=2))
