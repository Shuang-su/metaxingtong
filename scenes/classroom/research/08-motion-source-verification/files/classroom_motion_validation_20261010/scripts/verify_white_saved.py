import bpy,json,re,hashlib
from pathlib import Path
from mathutils import Vector
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010/tracked_desks_white');tops=[];left=[]
for o in bpy.data.objects:
 if 'observed rectangular top' in o.name:
  v=[o.matrix_world@Vector(q) for q in o.bound_box];tops.append({'name':o.name,'dimensions':list(o.dimensions),'location':list(o.location),'top_z':max(q.z for q in v)})
 if re.match(r'^(R[1-4]C[1-4]\b|V4 R[2-4]Outer[LR]\b|V4 ObservedRearD\d+\b)',o.name) or o.name.startswith(('Desk front empty label mount','Desk perforated ochre front rail')):left.append(o.name)
j={'two_observed_top_meshes':tops,'old_student_group_and_detached_fittings_remaining':left,'two_top_count':len(tops),'shared_template_same_dimensions':len(tops)==2 and all(abs(a-b)<1e-5 for a,b in zip(tops[0]['dimensions'],tops[1]['dimensions'])),'all_three_joint_cameras_present':all('JOINT_F_path_'+n in bpy.data.objects for n in ['073','076','080']),'not_total_room_desk_count':True};(p/'qa/saved_white_model_verification.json').write_text(json.dumps(j,indent=2));print(json.dumps(j))
