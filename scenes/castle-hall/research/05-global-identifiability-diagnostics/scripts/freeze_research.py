from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1];OLD=R.parent/'castlehall_shared_white_v1_20261010';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
old=json.loads((OLD/'SHA256.json').read_text());models=[]
for e in old['files']:
 if e['path'].startswith('models/'):
  p=OLD/e['path'];actual=sha(p);models.append(dict(path=e['path'],expected_sha256=e['sha256'],actual_sha256=actual,unchanged=actual==e['sha256']))
oldreport={'time_utc':now,'old_frozen_manifest_sha256':sha(OLD/'SHA256.json'),'expected_manifest_sha256':'3851d15e380269972189eba4365ba51dde7b18fb9d595d85c78437a65f814bd2','models':models};assert all(e['unchanged'] for e in models);assert oldreport['old_frozen_manifest_sha256']==oldreport['expected_manifest_sha256'];(R/'qa/frozen_QAr2_unchanged.json').write_text(json.dumps(oldreport,indent=2))
# Exact arithmetic audit source-source overlay and fixed core crops.
a=np.array(Image.open(R/'inputs/motion_right_to_front_verified/042.jpg').crop((0,27,1180,691)).convert('RGB'));b=np.array(Image.open(R/'inputs/motion_right_to_front_verified/049.jpg').crop((0,27,1180,691)).convert('RGB'));o=np.array(Image.open(R/'qa/source_042_049_direct50.png').convert('RGB'));assert np.array_equal(o,((a.astype(np.uint16)+b)/2).astype(np.uint8));cropok=[]
for i in [35,42,49]:
 original=np.array(Image.open(R/f'inputs/motion_right_to_front_verified/{i:03}.jpg').crop((0,27,1180,691)));actual=np.array(Image.open(R/f'qa/selected_{i:03}_core.png'));cropok.append({'frame':i,'identical':bool(np.array_equal(original,actual))});assert cropok[-1]['identical']
(R/'qa/image_arithmetic_audit.json').write_text(json.dumps({'source_source_overlay_50pct_exact':True,'images_warped':False,'crop':[0,27,1180,691],'crops':cropok,'note':'Arithmetic audit only, not camera or source acceptance.'},indent=2))
seqs=[]
for name,role in [('motion_right_to_front_verified','used continuous sequence;155 original screenshots archived'),('motion_4527_continuous','auxiliary frontal run;not fitted;metadata/contact only archived'),('motion_side_front_active','auxiliary frontal run;not fitted;metadata only archived'),('motion_side_to_front','excluded paused duplicate batch;one time only;metadata only archived')]:
 m=json.loads((R/'inputs'/name/'metadata.json').read_text());seqs.append({'directory':'inputs/'+name,'role':role,'n_screenshots':len(m['frames']),'first_before':m['frames'][0]['before']['time'],'last_after':m['frames'][-1]['after']['time'],'metadata_path':'inputs/'+name+'/metadata.json'})
(R/'source_ledger.json').write_text(json.dumps({'source_url':'https://www.bilibili.com/video/BV1aw411T7ws/','source_event':'2023-11-10 19点场 回城堡咯','capture_environment':'current cloud browser only','decoded':[1920,1080],'viewport':[1180,757],'fixed_core_crop':[0,27,1180,691],'core_size':[1180,664],'not_native_1920_export':True,'static_inputs':'inputs_sha256.json','heldout_image':'inputs/hall_C_4426_paused_core.png','heldout_policy':'coverage viewing only;no points/fits/validation leaked into training','sequences':seqs,'accepted_model_update':False,'source_acceptance':False},indent=2,ensure_ascii=False))
files=[]
for p in R.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(R).as_posix()
 if p.suffix=='.pyc' or rel in ['SHA256.json','ISSUE_figure_manifest.json'] or '/__pycache__/' in rel:continue
 # Auxiliary captures are not fitted, so keep provenance metadata plus existing overview but avoid duplicate unused raw images.
 if any(rel.startswith('inputs/'+n+'/') for n in ['motion_4527_continuous','motion_side_front_active','motion_side_to_front']):
  if p.name not in ['metadata.json','contact.jpg']:continue
 files.append(p)
priority=['qa/continuous_parallax_042_049.jpg','qa/focal_profile_rear_wall.png','qa/column_identity_review.jpg','qa/floor_direction_review.jpg','inputs/motion_right_to_front_verified/contact.jpg','qa/source_coverage_contact.jpg','qa/source_042_049_direct50.png','qa/near_plinth_042_detail.png','qa/stair_step_042_detail.png']
figs=[]
for p in files:
 if p.suffix.lower() not in ['.png','.jpg','.jpeg']:continue
 rel=p.relative_to(R).as_posix();typ='raw continuous source' if rel.startswith('inputs/motion_right_to_front_verified/') and p.stem.isdigit() else 'figure / source / diagnostic'
 figs.append({'path':rel,'sha256':sha(p),'bytes':p.stat().st_size,'kind':typ,'main_order':priority.index(rel)+1 if rel in priority else None})
figs.sort(key=lambda x:(x['main_order'] or 1000,x['path']));(R/'ISSUE_figure_manifest.json').write_text(json.dumps({'stage':'Global identifiability diagnosis; NO MODEL CHANGE; source unaccepted','figures':figs,'all_reference_warped':False,'source_overlay_note':'qa/source_042_049_direct50.png is unaligned source-source50%, NOT model comparison.'},indent=2,ensure_ascii=False));files.append(R/'ISSUE_figure_manifest.json')
manifest={'stage':'CastleHall global identifiability diagnostic only; model unchanged; no source acceptance','frozen_utc':now,'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'excluded_auxiliary_raw_images':'Not used for model/camera analysis;metadata with roles and capture hashes retained. Main155 continuous originals fully included.'};assert all(e['bytes']<18000000 for e in manifest['files']);(R/'SHA256.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False));print('files',len(files),'figures',len(figs),'bytes',sum(e['bytes'] for e in manifest['files']),'max',max(e['bytes']for e in manifest['files']),'manifest_sha',sha(R/'SHA256.json'))
