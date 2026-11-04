import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).parent;R=Path('/workspace/scratch/fa58bfcf0425/keyring-hall-candidate-20261104/versions/R06/models/keyring-material.blend');bpy.ops.wm.open_mainfile(filepath=str(R));dg=bpy.context.evaluated_depsgraph_get();B={}
for n in ['stage-central-solid','stage-step-ring','stage-outer-floor']:
 o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();B[n]=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True);e.to_mesh_clear()
def hits(x,y):return [{'object':n,'z':h[0].z} for n,b in B.items() if (h:=b.ray_cast(Vector((x,y,5)),Vector((0,0,-1)),10))[0] is not None]
out={};central=[(x*.2,y*.2) for x in range(-24,25) for y in range(-24,25) if (x*.2)**2+(y*.2)**2<4.85**2];out['central_interior_grid']={'step':.2,'radius_limit':4.85,'samples':len(central),'misses':[(x,y) for x,y in central if not hits(x,y)]}
for name,r,aa,bb in [('step_mid',5.5,-math.pi,math.pi),('outer_mid',7.5,-2.0,2.0),('intentional_between_central_step',5.01,-math.pi,math.pi),('intentional_between_step_outer',6.01,-2,2)]:
 pts=[(r*math.sin(a:=aa+(bb-aa)*i/180),r*math.cos(a)) for i in range(181)];out[name]={'radius':r,'angle_range':[aa,bb],'samples':len(pts),'hits':sum(bool(hits(x,y)) for x,y in pts)}
(O/'floor-rays.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
