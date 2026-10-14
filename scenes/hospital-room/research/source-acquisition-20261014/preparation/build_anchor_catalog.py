from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).parent;R=ROOT/'restored';audit=json.loads((R/'native_feature_audit.json').read_text());sources=json.loads((R/'source_recovery_checks.json').read_text())
source_records={}
for s in sources:
 p=R/Path(s['file']).name
 actual=hashlib.sha256(p.read_bytes()).hexdigest();size=list(Image.open(p).size)
 assert actual==s['sha256'] and size==[1920,1080]
 source_records[s['view']]={'source_video':'BV1GqXMByE1s','seconds':s['seconds'],'filename':p.name,'sha256':actual,'actual_dimensions':size,'coordinate_system':'x_right_y_down_native_pixels','transform':'none','native_bytes_verified_this_review':True,'partition':{'A':'historical_train','G':'historical_train','B':'historical_heldout','H':'historical_heldout','F':'historical_regression'}[s['view']]}
records=[]
for frame,v in audit['views'].items():
 for f in v['features']:
  n=f['name'];kind=f['kind'];model=None;branch=None;status='source_observation_only';guard=[]
  if n.startswith('central_member_black_jamb'):
   model='Window • calibrated vertical mullion.002';branch='beige_side_visible_border' if 'beige_side' in n else 'opposite_visible_border';status='candidate_mesh_family_location_supported_NOT_exact_vertex';guard=['Specify actual visible front/bevel/side edge after camera projection and visibility test; do not equate world-X extrema with pixel left/right.']
  elif n.startswith('window_right_group_mid_black'):
   model='Window • calibrated vertical mullion.003';branch='image_left' if n.endswith('left') else 'image_right';status='candidate_mesh_family_requires_continuous_identity';guard=['Name is image-local; confirm room/window rank and visible face before fit.']
  elif n.startswith('window_right_group_wall_jamb'):
   model='Window • calibrated vertical mullion.004';branch='image_left' if n.endswith('left') else 'image_right';status='candidate_mesh_family_requires_continuous_identity'
  elif n.startswith('main_window_mid_black'):
   model='Window • calibrated vertical mullion.001';branch='image_left' if n.endswith('left') else 'image_right';status='candidate_mesh_family_requires_continuous_identity'
  elif n=='curtain_outer_right':
   model='Curtain • rebuilt uniform eight-fold drape';branch='visible_outer_right';status='conditional_surface_family_NOT_fold_vertex';guard=['Gray folded/slotted surface distinct from beige member; model eight folds and fabric identity are not verified.','Cloth/pleat silhouette need not be same material vertex across views.']
  elif n.startswith('track_'):
   model=['Curtain rail • forward overhead beam','Curtain rail • forward overhead beam.001'];branch=n.removeprefix('track_');status='candidate_long_member_order_only';guard=['Two visible long members and short pieces observed; same-Z versus different-Z cross-section unresolved.','End cap is not measured hidden pillar contact; nearest connector indices are not cross-frame IDs.']
  elif n.startswith('bed_far_board'):
   model='Bed • observed endboard, consistent width';branch='compound_left_shoulder_and_upper_NEEDS_SPLIT';status='conditional_endboard_family_NOT_head_or_foot_identified';guard=['Split left vertical/rounded shoulder/upper/right branches before comparison.','Do not pair equal polyline sample indices across views; bed ownership and head/foot direction require connection evidence.']
  elif kind in ['soft_radiometric_transition','surface_shading_or_crease']:
   status='EXCLUDED_AS_RIGID_GEOMETRY';branch='radiometric_only';guard=['Not a verified physical pillar corner; never fit this as a mesh edge or point.']
  elif n=='pale_gray_region_left':
   status='UNRESOLVED_SURFACE_IDENTITY';branch='visible_boundary_only';guard=['Behind-glass surface, reveal or separate architectural surface unresolved.','Do not extend through person or sofa, and do not rename as beige pillar.']
  records.append({'anchor_id':frame+':'+n,'frame':frame,'source_sha256':source_records[frame]['sha256'],'source_annotation':{'library_file_id':'libfile_314acb211b7c8191ac563653ecbf14e5','version':0,'feature_name':n},'source_points':f['points'],'source_kind':kind,'uncertainty_px':f['uncertainty_px'],'semantic_branch':branch,'mesh_family_candidate':model,'identity_state':status,'geometric_residual_allowed_now':False,'reason_not_scoring':'No new calibrated view or verified per-view named projection/visibility supplied in this preparation round.','guards':guard,'original_note':f.get('note','')})
d=json.loads((R/'annotations_native_1920x1080.json').read_text())
exceptions=[]
for f in d['features']:
 if f.get('valid_for_geometry_metrics') is False or 'ivory_pier_to_curtain' in f['id'] or 'glass_to_lightgray' in f['id'] or 'rail_first_fully' in f['id'] or 'nearest_curtain' in f['id']:
  exceptions.append({'legacy_id':f['id'],'legacy_kind':f['kind'],'legacy_use':f['optimization_use'],'new_use':'reference_only_no_automatic_reuse','note':f.get('erratum_reason',f.get('note'))})
out={'status':'PREPARATION_ONLY_NO_NEW_GEOMETRY_FIT_OR_RENDER','old_model_status':{'D':'NOT_ACCEPTED','J1':'REJECTED','H_original_85px_claim':'WITHDRAWN_INVALID_CALIBRATION'},'sources':source_records,'anchors':records,'legacy_annotation_exclusions':exceptions,'mandatory_scoring_gate':['Native frame provenance and pixel dimensions verified','Exact source semantic branch and object identity reviewed','Camera/intrinsics nuisance assumptions explicit; patient-eye prior never replaced by free camera','Visible candidate mesh branch from exact named object supplied, not all-object convex hull','Occluded/clipped parts excluded and unsupported sections rejected','Physical intersection and foreground/background ordering checked independently','Metric is conditional screen-space diagnostic, never automatic model acceptance']}
(ROOT/'source_anchor_catalog.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(len(records),'anchors; sources',list(source_records))
