import bpy,json,pathlib,re
from mathutils import Vector
R=pathlib.Path('forest-diagnostic-replay-20261104').resolve();bpy.ops.wm.open_mainfile(filepath=str(R/'models/R09_material.blend'));terrain=bpy.data.objects['TERRAIN_finite_working_domain'];inv=terrain.matrix_world.inverted();results=[]
for scale in [1,1.25,1.5,2]:
 rows=[]
 for o in bpy.context.scene.objects:
  if not re.fullmatch(r'FAR_TREE_\d\d',o.name):continue
  vs=[o.matrix_world@v.co for v in o.data.vertices];z=min(v.z for v in vs);low=[v for v in vs if v.z<z+.3];c=sum(low,Vector())/len(low);x,y=c.x*scale,c.y*scale
  hit,loc,no,idx=terrain.ray_cast(inv@Vector((x,y,100)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
  rows.append(dict(tree=o.name,centre_xy=[x,y],has_terrain_beneath=hit,terrain_z=(terrain.matrix_world@loc).z if hit else None))
 results.append(dict(scale=scale,trees_without_terrain=sum(not x['has_terrain_beneath'] for x in rows),rows=rows))
(R/'qa/far-ring-terrain-check.json').write_text(json.dumps(results,indent=2));print([(x['scale'],x['trees_without_terrain']) for x in results])
