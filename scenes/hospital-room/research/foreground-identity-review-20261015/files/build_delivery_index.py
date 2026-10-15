from pathlib import Path
import json,hashlib,mimetypes
R=Path(__file__).resolve().parent
primary=['README_床端与前景身份复核_20261015.md','independent_visual/foreground_identity_evidence.png','independent_visual/independent_visual_review.md','independent_visual/evidence.html','foreground_model_first_hits.json','prior_annotation_correction_proposal.json','independent_visual/foreground_identity_points.json','independent_visual/source_manifest.json']
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or p.name in ['delivery_index.json','pending_library_uploads.json'] or '__pycache__' in p.parts: continue
 rel=str(p.relative_to(R));b=p.read_bytes();files.append(dict(relative_path=rel,absolute_path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),mime_type=mimetypes.guess_type(p.name)[0] or 'application/octet-stream',role='primary' if rel in primary else 'supporting_evidence',library_state='not_uploaded_this_stage',recommended_library_artifact_type='other'))
index=dict(status='SOURCE_IDENTITY_REVIEW_FROZEN_NO_GEOMETRY_CHANGE',source_fidelity_accepted=False,CURRENT_change_allowed=False,format='ordinary originals, no ZIP',root_mapping={'identity':str(R)},file_count=len(files),total_bytes=sum(f['bytes'] for f in files),all_under_18MiB=all(f['bytes']<18*1024**2 for f in files),primary_order=primary,primary_missing=[x for x in primary if not(R/x).exists()],files=files,limits=['No new geometry/camera in this batch','5476/5477/5663/5668/5693/6063 are viewport JPEG, not native residual inputs','665 wood-table identity high-confidence; G/H/N640 pale foreground unresolved','Old model first-hit occupancy is not source identity proof','Old annotation files unchanged; correction proposal additive'])
(R/'delivery_index.json').write_text(json.dumps(index,indent=2,ensure_ascii=False))
ordered=[next(f for f in files if f['relative_path']==x) for x in primary]+[f for f in files if f['relative_path'] not in primary]
for name in ['delivery_index.json']:
 p=R/name;b=p.read_bytes();ordered.append(dict(relative_path=name,absolute_path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),mime_type='application/json',role='index',library_state='not_uploaded_this_stage',recommended_library_artifact_type='other'))
(R/'pending_library_uploads.json').write_text(json.dumps({'status':'FROZEN_FOR_DEDICATED_UPLOAD_WORKER; geometry worker attempted no Library writes','files':ordered},indent=2,ensure_ascii=False))
print(index['file_count'],index['total_bytes'],index['primary_missing'])
