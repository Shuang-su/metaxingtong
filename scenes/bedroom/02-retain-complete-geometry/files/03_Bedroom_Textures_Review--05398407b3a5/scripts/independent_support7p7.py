import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/scratch/fa58bfcf0425/bedroom_fullroom/final7p7');bpy.ops.wm.open_mainfile(filepath=str(R/'models/01_bedroom_material.blend'));s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out=[]
for name in ['Bed recessed dark plinth','Cabinet sled foot','Cabinet sled foot.001','Plant pot lower','Large low pile bedside rug']:
 o=bpy.data.objects[name];pts=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];rs=[]
 for i in [1,3,5,7,9]:
  for j in [1,3,5,7,9]:
   p=Vector((lo[0]+(hi[0]-lo[0])*i/10,lo[1]+(hi[1]-lo[1])*j/10,lo[2]+.1));hits=[]
   for ob in s.objects:
    if ob.type!='MESH' or ob==o or not (ob.name.startswith('Herringbone oak plank') or ob.name in ['实体地板_厚0.16','Large low pile bedside rug']):continue
    inv=ob.matrix_world.inverted();aa=inv@p;bb=inv@(p+Vector((0,0,-.3)));hit,q,n,idx=ob.ray_cast(aa,(bb-aa).normalized(),distance=(bb-aa).length)
    if hit:hits.append(((ob.matrix_world@q).z,ob.name))
   z,name0=max(hits) if hits else (None,None);rs.append({'hit':bool(hits),'gap':lo[2]-z if hits else None,'support':name0})
 out.append({'object':name,'underside_z':lo[2],'samples':rs})
(R/'analysis/independent_support_check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out)
