import bpy,json,hashlib
from pathlib import Path
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010');q=p/'six_bay_candidate';changes=json.load(open(q/'qa/shared_changes.json'));expected={x['object'] for x in changes['changes']}
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for o in bpy.data.objects:
  if o.type=='CAMERA':continue
  d={'type':o.type,'matrix':[list(r) for r in o.matrix_world],'hide_render':o.hide_render,'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []}
  if o.type=='MESH':d.update(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(f.vertices) for f in o.data.polygons])
  if o.type=='LIGHT':d.update(energy=o.data.energy,color=list(o.data.color))
  out[o.name]=hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
 return out
old=snap(p/'Classroom_Motion_Verification_ONLY.blend');new=snap(q/'Classroom_SixBay_CANDIDATE.blend');actual={n for n in set(old)|set(new) if old.get(n)!=new.get(n)}
r={'expected_changed_objects':sorted(expected),'actual_changed_objects':sorted(actual),'unexpected_changes':sorted(actual-expected),'expected_but_unchanged':sorted(expected-actual),'unchanged_object_count':len(set(old)&set(new)-actual),'unchanged_non_camera_objects_match':not(actual-expected),'baseline_blend_sha256':hashlib.sha256((p/'Classroom_Motion_Verification_ONLY.blend').read_bytes()).hexdigest(),'candidate_blend_sha256':hashlib.sha256((q/'Classroom_SixBay_CANDIDATE.blend').read_bytes()).hexdigest()}
(q/'qa/object_change_audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
