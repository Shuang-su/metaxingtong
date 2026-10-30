import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parents[1]
def snap():
 s=bpy.context.scene;out={}
 for frame in [1,2]:
  s.frame_set(frame);bpy.context.view_layer.update();rows=[]
  for o in sorted(s.objects,key=lambda x:x.name):
   if o.type=='MESH':rows.append([o.name,[[float(v) for v in vert.co] for vert in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[[float(v) for v in row] for row in o.matrix_world],o.hide_render])
  out[str(frame)]=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
 return out
bpy.ops.wm.open_mainfile(filepath=str(S/'models/car_passenger_cabin_material.blend'));baseline=snap()
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_camera_only_trial.blend'));trial=snap()
assert baseline==trial
poses={o.name:(list(o.location),list(o.rotation_euler),o.data.lens) for o in bpy.context.scene.objects if o.type=='CAMERA' and o.name.startswith('SRC_S')}
bpy.ops.wm.open_mainfile(filepath=str(S/'models/car_passenger_cabin_white.blend'))
for name,(pos,rot,lens) in poses.items():o=bpy.data.objects[name];o.location=pos;o.rotation_euler=rot;o.data.lens=lens
assert snap()==baseline
bpy.context.scene.frame_set(1);bpy.context.scene['camera_study_status']='Rejected camera-only diagnostic; original candidate remains unchanged'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/car_camera_only_white_trial.blend'))
(R/'fixed_geometry_verification.json').write_text(json.dumps({'mesh_vertex_topology_world_matrix_and_visibility_digest_per_state':baseline,'camera_trial_matches':trial,'white_trial_matches':snap(),'same_geometry_all_states':True,'door_states':'Frame1 closed; frame2 common 54deg hinge; unchanged','scope':'No mesh edits, per-view deformation, hidden objects or state-dependent shape changes; only source camera poses/lenses differ'},indent=2)+'\n')
