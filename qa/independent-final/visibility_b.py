import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(O.parent/'keyring-underbridge-r07-20261104/models/r07b-material.blend'));s=bpy.context.scene;c=s.objects['diagnostic-underbridge-fixed'];dg=bpy.context.evaluated_depsgraph_get();out={}
for n in ['inferred-low-bridge-central-step','inferred-low-bridge-step-outer']:
 o=s.objects[n];m=o.data;m.calc_loop_triangles();z=min((o.matrix_world@v.co).z for v in m.vertices);rows=[]
 for t in m.loop_triangles:
  vs=[o.matrix_world@m.vertices[i].co for i in t.vertices]
  if max(abs(v.z-z) for v in vs)>1e-6:continue
  p=sum(vs,Vector())/3;uv=world_to_camera_view(s,c,p)
  if not(uv.z>0 and 0<=uv.x<=1 and 0<=uv.y<=1):continue
  v=p-c.location;hit=s.ray_cast(dg,c.location,v.normalized(),distance=v.length+1e-4);rows.append({'triangle':t.index,'pixel':[uv.x*1192,(1-uv.y)*671],'first_object':hit[4].name if hit[0] else None})
 out[n]={'bottom_centroids_in_frame':len(rows),'first_self':sum(r['first_object']==n for r in rows),'rows':rows}
(O/'visibility-b.json').write_text(json.dumps(out,indent=2));print(out)
