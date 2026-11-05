import bpy,bmesh,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
Q=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(Q/'frozen/models/material.blend'));s=bpy.context.scene;meshes=[o for o in s.objects if o.type=='MESH'];new=[o for o in meshes if o.name.startswith('SIGN_')]
def geo(o):
 o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];t=[tuple(x.vertices) for x in o.data.loop_triangles];b=BVHTree.FromPolygons(v,t,all_triangles=True);bounds=[(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)];return v,t,b,bounds
G={o.name:geo(o) for o in meshes};out={'new':{},'pairs':[]}
for o in new:
 v,t,tree,b=G[o.name];selfpairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(t[i])&set(t[j])];bm=bmesh.new();bm.from_mesh(o.data);seen=set();components=[]
 for vert in bm.verts:
  if vert in seen:continue
  todo=[vert];seen.add(vert);comp=[]
  while todo:
   a=todo.pop();comp.append(a)
   for e in a.link_edges:
    z=e.other_vert(a)
    if z not in seen:seen.add(z);todo.append(z)
  components.append(len(comp))
 out['new'][o.name]={'vertices':len(v),'triangles':len(t),'world_min_triangle_area':min((v[b]-v[a]).cross(v[c]-v[a]).length*.5 for a,b,c in t),'component_vertex_counts':components,'euler':len(bm.verts)-len(bm.edges)+len(bm.faces),'nonadjacent_triangle_self_pairs':selfpairs,'bounds':b};bm.free()
 for p in meshes:
  if o==p or (p in new and p.name<o.name):continue
  vv,tt,bt,bb=G[p.name]
  if all(b[i][1]>=bb[i][0] and bb[i][1]>=b[i][0] for i in range(3)):
   out['pairs'].append({'a':o.name,'b':p.name,'aabb':True,'surface_triangle_pairs':len(tree.overlap(bt))})
# Actual front perpendicular mask of current Bold, against producer finite hit count (not regenerate pre-cleanup here).
f=next(o for o in new if 'font_proxy' in o.name);tree=G[f.name][2];mask=[]
for j in range(180):
 for i in range(640):mask.append(tree.ray_cast(Vector((-1.52+(i+.5)*3.04/640,2.8,2.74+(j+.5)*.83/180)),Vector((0,1,0)),1)[0] is not None)
out['font_mask']={'size':[640,180],'hits':sum(mask),'misses':len(mask)-sum(mask),'scope':'current saved Bold only, not independent precleanup rerun or source glyph match'}
(Q/'contact.json').write_text(json.dumps(out,indent=2));print('DONE')
