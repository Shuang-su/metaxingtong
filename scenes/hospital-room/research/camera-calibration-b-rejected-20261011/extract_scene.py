import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/camera_calibration_b');s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
cams={k:bpy.data.objects[n] for k,n in [('F','MATCH_F_Turning_Right'),('G','MATCH_G_Sofa_And_Bed'),('H','MATCH_H')]}
cs={k:{'name':o.name,'matrix_world':[list(a) for a in o.matrix_world],'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_height':o.data.sensor_height,'sensor_fit':o.data.sensor_fit,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end} for k,o in cams.items()}
objs=[]
for o in s.objects:
 if o.type!='MESH':continue
 pts={f'bbox_{i}':list(o.matrix_world@Vector(p)) for i,p in enumerate(o.bound_box)}
 pts['origin']=list(o.matrix_world.translation)
 projections={}
 for tag,cam in cams.items():
  projections[tag]={}
  for n,p in pts.items():
   v=world_to_camera_view(s,cam,Vector(p));projections[tag][n]=[v.x*1920,(1-v.y)*1080,v.z]
 objs.append({'name':o.name,'points':pts,'projections':projections,'dimensions':list(o.dimensions)})
(r/'scene_anchor_inventory.json').write_text(json.dumps({'cameras':cs,'objects':objs},indent=2))
