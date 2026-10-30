import bpy,json,math,hashlib,sys
from mathutils import Vector,Matrix
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parents[1]
fit=json.loads((R/'camera_only_fit.json').read_text());g=json.loads((R/'shared_geometry.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(S/'models/car_passenger_cabin_material.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.use_denoising=False;s.cycles.samples=16;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50
def geo_digest():
 rows=[]
 for o in sorted([o for o in s.objects if o.type=='MESH'],key=lambda x:x.name):rows.append([o.name,[[float(c) for c in v.co] for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]])
 return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
assert geo_digest()==g['geometry_vertex_topology_sha256']
for id,row in fit['results'].items():
 c=bpy.data.objects['SRC_'+id+('_open' if id=='S02' else '_closed')];p=row['fitted_camera'];c.location=p[:3];yaw,pitch,roll=p[3:6];forward=Vector((math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)));right=Vector((math.sin(yaw),-math.cos(yaw),0));up=right.cross(forward);rr=right*math.cos(roll)+up*math.sin(roll);uu=-right*math.sin(roll)+up*math.cos(roll);rot=Matrix((rr,uu,-forward)).transposed();c.rotation_euler=rot.to_euler();c.data.lens=p[6]
 c['status']='Camera-only robust multi-feature trial; bounds active and heldout errors, NOT adopted'
(R/'models').mkdir(exist_ok=True);(R/'renders/camera_only_low').mkdir(parents=True,exist_ok=True)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/car_camera_only_trial.blend'))
assert geo_digest()==g['geometry_vertex_topology_sha256']
for id,row in fit['results'].items():
 s.camera=bpy.data.objects['SRC_'+id+('_open' if id=='S02' else '_closed')];s.frame_set(row['door_state']);s.render.filepath=str(R/f'renders/camera_only_low/{id}_render_960.png');bpy.ops.render.render(write_still=True)
print('FIXED_GEOMETRY_VERIFIED',geo_digest())
