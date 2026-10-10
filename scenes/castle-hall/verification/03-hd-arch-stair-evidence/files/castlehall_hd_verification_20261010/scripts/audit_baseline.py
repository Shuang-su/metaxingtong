import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=R.parent/'castle_hall_fullroom/models/Xingtong_Castle_Hall_FullRoom.blend'
bpy.ops.wm.open_mainfile(filepath=str(P))
S=bpy.context.scene
out={'model':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'objects':len(S.objects),'meshes':sum(o.type=='MESH' for o in S.objects),'cameras':[],'geometry':[]}
for o in S.objects:
 if o.type=='CAMERA':out['cameras'].append(dict(name=o.name,loc=list(o.location),rot=list(o.rotation_euler),lens=o.data.lens,sensor=o.data.sensor_width,shift=[o.data.shift_x,o.data.shift_y]))
 elif o.type=='MESH':
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  out['geometry'].append(dict(name=o.name,collection=[c.name for c in o.users_collection],bbox=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],hidden=o.hide_render))
(R/'qa/baseline_inventory.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='geometry'},indent=2))
