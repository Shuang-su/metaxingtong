import bpy,json,sys,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
Q=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(Q/'frozen/models/material.blend'));D={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();v=[tuple(o.matrix_world@x.co)for x in o.data.vertices];inds=[tuple(t.vertices)for t in o.data.loop_triangles];ts=[[v[i]for i in t]for t in inds];D[o.name]={'v':v,'t':ts,'bvh':BVHTree.FromPolygons(v,inds,all_triangles=True),'box':[(min(p[k]for p in v),max(p[k]for p in v))for k in range(3)]}
def intersects(a,b):return all(a[k][1]>=b[k][0]and b[k][1]>=a[k][0]for k in range(3))
def dist(a,b):
 best=1e99
 for x in a['t']:
  xb=[(min(p[k]for p in x),max(p[k]for p in x))for k in range(3)]
  for y in b['t']:
   yb=[(min(p[k]for p in y),max(p[k]for p in y))for k in range(3)];lower=sum(max(xb[k][0]-yb[k][1],yb[k][0]-xb[k][1],0)**2 for k in range(3))
   if lower>best:continue
   best=min(best,triangle_triangle2(x,y))
 return math.sqrt(best)
r={'bvh_relations':{},'actual_triangle_distances':{}}
for n in D:
 if not n.startswith(('U','A','W02','R02')):continue
 a=D[n];r['bvh_relations'][n]={m:len(a['bvh'].overlap(b['bvh']))for m,b in D.items()if m!=n and intersects(a['box'],b['box'])and a['bvh'].overlap(b['bvh'])}
for m in D:
 if m.startswith(('U02','U03')):r['actual_triangle_distances']['U01 umbrella pole -> '+m]=dist(D['U01 umbrella pole'],D[m])
(Q/'contact.json').write_text(json.dumps(r,indent=2));print('DONE')
