import bpy,pathlib,json
from mathutils import Vector
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-source15-qa-20261104');r=json.loads((Q/'trial18-correspondences.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(P/'models/R07_material.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();c=Vector(r['camera']['camera_position'])
for p in r['points']:
 v=Vector(p['world_target'])-c;length=v.length;hit,loc,normal,idx,obj,mat=s.ray_cast(dg,c,v.normalized(),distance=length-.0001);p['closer_hit_1e4']={'object':obj.name,'distance_before_target':length-(loc-c).length} if hit else None
(Q/'trial18-visibility.json').write_text(json.dumps(r,indent=2));print([(p['id'],p['source_pixel'],p['closer_hit_1e4']) for p in r['points']])
