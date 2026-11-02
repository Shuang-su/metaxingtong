from pathlib import Path
import json,hashlib,struct,ast
from PIL import Image
import numpy as np
root=Path('/workspace/scratch/fa58bfcf0425');out=root/'camp-remake-20261102-source-audit';src=root/'recovered-source-candidates/camp';manifest=json.load(open(src/'recovery_manifest.json'));rows=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f in manifest['frames']:
 p=src/Path(f['path']).name;b=p.read_bytes();im=Image.open(p);im.load();ihdr=list(struct.unpack('>II',b[16:24]));rows.append({'path':str(p.relative_to(root)),'bytes':len(b),'sha256':sha(p),'dimensions_decoded':list(im.size),'dimensions_IHDR':ihdr,'matches_original_sha':sha(p)==f['original_sha256'],'matches_recovery_sha':sha(p)==f['recovered_sha256'],'matches_dimensions':list(im.size)==f['dimensions']==ihdr,'matches_bytes':len(b)==f['bytes'],'new_capture':False})
dp=root/'depth-validation-20261102/camp-tool-validation';rep=json.load(open(dp/'report.json'));dr=[]
for f in rep['outputs']:
 p=dp/f['path'];d={'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p),'hash_matches_report':sha(p)==f['sha256'],'bytes_match_report':p.stat().st_size==f['bytes']}
 if p.suffix=='.npy':
  a=np.load(p,allow_pickle=False);d.update(shape=list(a.shape),dtype=str(a.dtype),nonfinite=int((~np.isfinite(a)).sum()),min=float(a.min()),max=float(a.max()))
 else:
  im=Image.open(p);im.load();a=np.asarray(im);d.update(size=list(im.size),mode=im.mode,dtype=str(a.dtype))
  if 'classes' in p.name or 'confidence' in p.name:d['value_counts']={str(int(v)):int(c) for v,c in zip(*np.unique(a,return_counts=True))}
 dr.append(d)
roll=root/'reconstruction-recovery/camp/code-candidates/roll';rm=json.load(open(roll/'RECOVERY_MANIFEST.json'));rr=[]
for f in rm['files']:
 p=roll/f['file'];d={'path':str(p.relative_to(root)),'sha256':sha(p),'matches_recovery_candidate_sha':sha(p)==f['sha256_current_candidate'],'original_sha_verified':False}
 if p.suffix=='.py':ast.parse(p.read_text());d['syntax_only']='pass, no execution'
 rr.append(d)
required=['qa/heldout_r03/frozen_geometry_anchors.json','qa/R07_actual_model_anchor_check.json','qa/heldout_r03/fixed_model_camera_cases.json'];oldroot=Path('/workspace/shared/desert-camp-build-20261031/scenes/desert-tent-camp');deps=[{'path':str(oldroot/p),'currently_exists':(oldroot/p).exists()} for p in required]
weights=root/'depth-validation-20261102/model/model.safetensors'
j={'source_PNG_checks':rows,'depth_source_matches_current_1566':rep['source']['sha256']==next(a['sha256'] for a in rows if '1566.' in a['path']),'depth_method_report':rep['method'],'depth_outputs_checks':dr,'weights_actual_sha256':sha(weights),'weights_hash_matches_report':sha(weights)==rep['method']['weights_sha256'],'roll_script_checks':rr,'roll_missing_dependencies':deps,'scope':'read-only byte/shape/AST checks; no inference, no camera optimization, no model or production branch writes'}
(out/'audit.json').write_text(json.dumps(j,ensure_ascii=False,indent=2));print(json.dumps({'source_checks':rows,'depth_files':len(dr),'all_depth_hash_match':all(x['hash_matches_report'] for x in dr),'dependencies':deps},indent=2))
