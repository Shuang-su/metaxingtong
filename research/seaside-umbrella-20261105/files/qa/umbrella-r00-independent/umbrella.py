import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
Q=Path(__file__).parent;old=Q.parent/'independent-seaside-wing-r05-qa-20261105/frozen/models/material.blend'
bpy.ops.wm.open_mainfile(filepath=str(old));names=[f'U02 canopy segment {i}' for i in range(8)];base={n:[bpy.data.objects[n].matrix_world@v.co for v in bpy.data.objects[n].data.vertices] for n in names}
bpy.ops.wm.open_mainfile(filepath=str(Q/'frozen/models/material.blend'));s=bpy.context.scene;meshes=[o for o in s.objects if o.type=='MESH']
def geo(o):
 o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];t=[tuple(x.vertices) for x in o.data.loop_triangles];return v,t,BVHTree.FromPolygons(v,t,all_triangles=True),[(min(p[i] for p in v),max(p[i] for p in v)) for i in range(3)]
G={o.name:geo(o) for o in meshes};out={'canopy':{},'pairs':[],'pole_pairs':[]}
for n in names:
 v,t,b,a=G[n];old=base[n];planes=[]
 for orig,ids in [([0,1,2],[0]+list(range(2,27))),([5,6,7],[1]+list(range(27,52)))]:
  p0,p1,p2=[old[i] for i in orig];norm=(p1-p0).cross(p2-p0).normalized();planes.append(max(abs((v[i]-p0).dot(norm)) for i in ids))
 out['canopy'][n]={'six_anchor_max':max(min((x-old[i]).length for x in v) for i in [0,1,2,5,6,7]),'outer_inner_top_plane_max_dist':planes,'nonshared_vertex_self_pairs':[(i,j) for i,j in b.overlap(b) if i<j and not set(t[i])&set(t[j])],'triangle_count':len(t)}
 for other in meshes:
  if other.name==n or (other.name in names and other.name<n):continue
  vv,tt,bb,aa=G[other.name]
  if all(a[i][1]>=aa[i][0] and aa[i][1]>=a[i][0] for i in range(3)):out['pairs'].append({'canopy':n,'other':other.name,'surface_triangle_pairs':len(b.overlap(bb))})
pole=bpy.data.objects['U01 umbrella pole'];v,t,b,a=G[pole.name]
for o in meshes:
 if o==pole:continue
 vv,tt,bb,aa=G[o.name]
 if all(a[i][1]>=aa[i][0] and aa[i][1]>=a[i][0] for i in range(3)):out['pole_pairs'].append({'other':o.name,'surface_triangle_pairs':len(b.overlap(bb))})
out['packed_images']=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),'packed_sha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None,'filepath':i.filepath,'color_space':i.colorspace_settings.name} for i in bpy.data.images if i.source=='FILE']
# Compare actual native vs imported UV sets keyed by rounded world positions; UV split duplicates remain sets, not index claims.
def uvsets():
 out={}
 for n in names:
  o=bpy.data.objects[n];d=o.data;out[n]=sorted(set(tuple(round(x,5) for x in o.matrix_world@d.vertices[d.loops[k].vertex_index].co)+tuple(round(x,5) for x in uv.uv) for k,uv in enumerate(d.uv_layers.active.data)))
 return out
u=uvsets();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(Q/'frozen/models/material.glb'));w=uvsets();out['glb_uv_sets_world_round5']={n:u[n]==w[n] for n in names}
(Q/'umbrella.json').write_text(json.dumps(out,indent=2));print('DONE')
