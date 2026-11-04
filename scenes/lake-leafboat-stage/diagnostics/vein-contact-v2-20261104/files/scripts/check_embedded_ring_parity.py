import bpy,pathlib,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];p=R/'models/leaf-only-contact-candidate-v2.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
shell=bpy.data.objects['LEAF_001_ThinConcaveShell'];m=shell.data;m.calc_loop_triangles();vv=[shell.matrix_world@v.co for v in m.vertices];tree=BVHTree.FromPolygons(vv,[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True)
report=json.loads((R/'qa/support-candidate-v2.json').read_text());directions=[Vector(v).normalized() for v in [(0,0,1),(0,0,-1),(.371,.227,.901),(-.269,.414,.87),(.231,-.193,-.953)]]
def parity(p,d):
 out=[];cursor=p.copy()
 for _ in range(32):
  h,n,i,distance=tree.ray_cast(cursor,d,20)
  if h is None:break
  out.append(list(h));cursor=h+d*1e-6
 else:raise AssertionError('Ray iteration limit')
 return dict(count=len(out),inside=len(out)%2==1,hits=out)
rows=[]
for o_row in report['rows']:
 o=bpy.data.objects[o_row['name']];sides=9 if o.name.startswith('LEAF_002') else 6
 for r in o_row['rings']:
  if not r['dz']:continue
  ps=[o.matrix_world@o.data.vertices[k].co for k in range(r['ring']*sides,(r['ring']+1)*sides)]
  ps+= [(ps[j]+ps[(j+1)%sides])*.5 for j in range(sides)]
  scored=[]
  for point in ps:
   h,_,_,_=tree.ray_cast(Vector((point.x,point.y,8)),Vector((0,0,-1)),20);scored.append((point.z-h.z,point))
  gap,point=min(scored,key=lambda x:x[0]);counts=[parity(point,d) for d in directions]
  rows.append(dict(name=o.name,ring=r['ring'],point=list(point),upper_gap=gap,directions=counts,all_inside=all(c['inside'] for c in counts)))
out=dict(candidate_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='One minimum-upper-gap sample per actually shifted ring, chosen from ring vertices and edge midpoints. Five ray directions each; not a full-volume proof. Multiple surface intersections are retained, not truncated to first two.',directions=[list(d) for d in directions],rows=rows,all_inside=all(r['all_inside'] for r in rows),sampled_rings=len(rows))
(R/'qa/embedded-ring-five-ray-parity.json').write_text(json.dumps(out,indent=2)+'\n')
print('Sampled rings',len(rows),'five-ray inside',sum(r['all_inside'] for r in rows),flush=True);assert out['all_inside']
