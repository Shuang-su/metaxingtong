import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R03_material.blend'));old={o.name:[tuple(o.matrix_world@v.co)for v in o.data.vertices]for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R04_material.blend'));mem=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH'and o.name.startswith('WING_'):
  o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];mem.append((o.name,BVHTree.FromPolygons(vs,[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True)))
out={};diff={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];ov=old.get(o.name);diff[o.name]=None if ov is None else (len(vs)!=len(ov) or any(tuple(v)!=w for v,w in zip(vs,ov)))
 if not o.name.startswith('VEIN_'):continue
 rows=[]
 for a in range(0,len(vs),10):
  ring=vs[a:a+10];deltas=[ring[i]-Vector(ov[a+i]) for i in range(10)];center=sum(ring,Vector())/10;ds=sum(deltas,Vector())/10;hit={}
  for n,b in mem:
   k=0
   for i,v in enumerate(ring):
    vec=ring[(i+1)%10]-v;length=vec.length
    if length:
     pt,nn,ix,dist=b.ray_cast(v,vec/length,length+1e-8)
     if pt is not None:k+=1
   if k:hit[n]=k
  rows.append({'ring':a//10,'mean_movement':ds.length,'rigid_translation_spread':max((d-ds).length for d in deltas),'membrane_boundary_segment_hits':hit})
 out[o.name]=rows
(O/'rings.json').write_text(json.dumps({'removed':sorted(set(old)-set(diff)),'world_geometry_changed':diff,'rings':out,'scope':'All 10 ring boundary straight segments tested against actual membrane triangles; no-hit is not standalone proof of separation (whole ring can be contained), hit verifies a sampled section surface crossing, not between-section full tube contact.'},indent=2));print('DONE')
