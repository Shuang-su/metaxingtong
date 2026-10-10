"""Camera-independent explicit layout states. No geometry, material, transform or animation edits."""
import hashlib,json,math

def digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def timeline_state(manifest, seconds):
 if isinstance(seconds,bool) or not isinstance(seconds,(int,float)) or not math.isfinite(seconds):
  return 'unknown'
 lo,hi=manifest['timeline']['ambiguous_transition_interval']
 if lo <= seconds <= hi:return 'unknown'
 for band in manifest['timeline']['observed_intervals']:
  if band['start'] <= seconds <= band['end']:return band['state']
 return 'unknown'

def choose_state(manifest, explicit_state=None, source_time_seconds=None):
 if source_time_seconds is not None and (isinstance(source_time_seconds,bool) or not isinstance(source_time_seconds,(int,float)) or not math.isfinite(source_time_seconds)):
  raise ValueError('Source time must be a finite numeric value or omitted')
 inferred=timeline_state(manifest,source_time_seconds)
 if explicit_state is None:
  if inferred=='unknown':raise ValueError('Unknown source-time state: use an explicit manual state for a labelled diagnostic only')
  return inferred,{'selection_mode':'observed_timeline','source_time_seconds':source_time_seconds,'timeline_result':inferred,'manual_override':False}
 if explicit_state not in manifest['states']:raise ValueError('Unknown explicit layout state')
 return explicit_state,{'selection_mode':'explicit_manual','source_time_seconds':source_time_seconds,'timeline_result':inferred,'manual_override':source_time_seconds is not None and inferred!=explicit_state}

def object_visibility(scene):
 return {o.name:{'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get(),'visible_camera':o.visible_camera} for o in sorted(scene.objects,key=lambda o:o.name) if o.type=='MESH'}

def apply_layout(scene, manifest, state_id, selection):
 """The interface intentionally has no camera parameter; only the sofa node allowlist may change."""
 if state_id not in manifest['states']:raise ValueError('Unknown explicit layout state')
 names=manifest['furnishing_group']['objects']
 if len(names)!=len(set(names)) or len(names)!=manifest['furnishing_group']['expected_count']:raise ValueError('Invalid sofa allowlist')
 if any(name not in scene.objects or scene.objects[name].type!='MESH' for name in names):raise ValueError('Missing sofa object(s)')
 dynamic={n for group in manifest['dynamic_groups'] for n in group['objects']}
 if dynamic.intersection(names):raise ValueError('Dynamic object incorrectly included in furnishing allowlist')
 before=object_visibility(scene)
 visible=manifest['states'][state_id]['sofas_visible']
 for name in names:
  obj=scene.objects[name]
  obj.hide_render=not visible
  obj.hide_viewport=not visible
 after=object_visibility(scene)
 changed=[n for n in before if before[n]!=after[n]]
 assert set(changed)<=set(names)
 assert all(before[n]==after[n] for n in before if n not in names)
 return {'state':state_id,'selection':selection,'allowed_targets':names,'changed_objects':changed,'object_visibility_before_sha256':digest(before),'object_visibility_after_sha256':digest(after),'dynamic_groups_preserved':True,'geometry_material_transform_writes':False}
