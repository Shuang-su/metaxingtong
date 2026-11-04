import bpy,pathlib,math,json
from mathutils import Vector
D=pathlib.Path(__file__).resolve().parent;p=D.parent/'forest-diagnostic-replay-20261104/models/R14_anchor-diagnostic_white.blend';bpy.ops.wm.open_mainfile(filepath=str(p));deps=bpy.context.evaluated_depsgraph_get();target=Vector((-6.183115,5.271026,-.04));rows=[]
for z in [.2,.4,.6,1.]:
 for i in range(16):
  a=i*math.tau/16;loc=target+Vector((1.3*math.cos(a),1.3*math.sin(a),z));v=target-loc;r=bpy.context.scene.ray_cast(deps,loc,v.normalized(),distance=v.length)
  rows.append({'loc':list(loc),'target':list(target),'hit':r[4].name if r[0] else None,'distance':(r[1]-loc).length if r[0] else None,'target_distance':v.length})
(D/'camera-candidates.json').write_text(json.dumps(rows,indent=2));print([x for x in rows if x['hit'] is None])
