import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
D=Path('/workspace/shared/metaxingtong-production-20261103/models');O=Path('/workspace/shared/novelty-review-20261103/qa');p=D/'R06_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
verts=[];faces=[];names=[];bounds={}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('WALL_','FLOOR_','CEILING_')):continue
 w=[o.matrix_world@v.co for v in o.data.vertices];offset=len(verts);verts+=w
 for f in o.data.polygons:faces.append(tuple(offset+i for i in f.vertices));names.append(o.name)
 bounds[o.name]={'min':[min(v[k] for v in w) for k in range(3)],'max':[max(v[k] for v in w) for k in range(3)]}
b=BVHTree.FromPolygons(verts,faces,all_triangles=False)
tests=[]
def ray(label,origin,direction,expect):
 loc,norm,idx,dist=b.ray_cast(Vector(origin),Vector(direction).normalized(),50)
 tests.append({'label':label,'origin':origin,'direction':direction,'expected':expect,'hit':None if idx is None else names[idx],'hit_position':None if loc is None else list(loc),'distance':dist})
for y in [-6.5,0,4.8]:
 for z in [.09,3,7.3]:
  for s in [-1,1]:ray(f'side_{s}_{y}_{z}',[0,y,z],[s,0,0],'solid wall')
for x in [-6.4,0,6.4]:
 for z in [.09,3,7.3]:ray(f'front_{x}_{z}',[x,0,z],[0,-1,0],'solid wall')
for x in [-6.4,-4,-2,0,4.5,5.3,6.4]:
 for z in [.09,3,7.3]:ray(f'rear_{x}_{z}',[x,0,z],[0,1,0],'window opening permitted at midheight only; sill/top/side solid')
for x,y in [(-6.4,-6.5),(6.4,-6.5),(-6.4,4.8),(6.4,4.8),(0,0)]:
 ray(f'floor_{x}_{y}',[x,y,3],[0,0,-1],'floor');ray(f'ceiling_{x}_{y}',[x,y,3],[0,0,1],'ceiling')
r={'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'selected_shell_bounds':bounds,'rays':tests,'limits':'Finite representative ray samples only. Real window opening deliberately excluded from shell. No proof of complete seamlessness, intersections or source dimensions.'};(O/'R06-shell-samples.json').write_text(json.dumps(r,indent=2))
print('no hits',[(x['label'],x['expected']) for x in tests if x['hit'] is None]);print('sill',bounds['WALL_rear_sill'])
