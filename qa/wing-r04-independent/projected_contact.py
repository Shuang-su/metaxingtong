import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
Q=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(Q/'frozen/models/material.blend'));out={}
for side in ['L','R']:
 body=bpy.data.objects[f'SIGN_{side}_closed_shallow_wing'];body.data.calc_loop_triangles();bv=[body.matrix_world@v.co for v in body.data.vertices];bt=[tuple(t.vertices) for t in body.data.loop_triangles];tree=BVHTree.FromPolygons(bv,bt,all_triangles=True)
 for name in [f'SIGN_{side}_layer_0',f'SIGN_{side}_layer_1',f'SIGN_{side}_curl_proxy']:
  o=bpy.data.objects[name];o.data.calc_loop_triangles();v=[o.matrix_world@v.co for v in o.data.vertices];points=v+[sum((v[i] for i in t.vertices),Vector())/3 for t in o.data.loop_triangles];bad=[]
  for i,p in enumerate(points):
   origin=Vector((p.x,3.0,p.z));hit=tree.ray_cast(origin,Vector((0,1,0)),.5)[0]
   if hit is None:
    loc,nor,face,dist=tree.find_nearest(Vector((p.x,3.16,p.z)));bad.append({'sample_index':i,'is_vertex':i<len(v),'world':list(p),'distance_to_body_at_front_plane':dist,'nearest':list(loc) if loc else None})
  out[name]={'vertices_plus_triangle_centroids':len(points),'missing_body_projected_hits':bad,'note':'Projection coverage only, not every cross-section or solid containment/continuous contact proof.'}
(Q/'projected_contact.json').write_text(json.dumps(out,indent=2));print('DONE',[(n,len(x['missing_body_projected_hits'])) for n,x in out.items()])
