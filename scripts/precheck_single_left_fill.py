import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent.parent;src=P.parent/'cyber-roof-cloud-r06-20261105/models/roof-r06b-experiment.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
N=144;cx,cy,cz,scale=-11.6,3.7,6.25,1.3;front,back=3.72,3.80
outline=[]
for i in range(N):
 a=2*math.pi*i/N;r=1+.17*math.sin(5*a)+.08*math.sin(9*a);outline.append((cx+scale*1.6*r*math.cos(a),cz+scale*.65*r*math.sin(a)))
vs=[(cx,front,cz)]+[(x,front,z) for x,z in outline]+[(cx,back,cz)]+[(x,back,z) for x,z in outline];faces=[];off=N+1
for i in range(N):
 a=i+1;b=(i+1)%N+1;faces += [(0,a,b),(off,off+b,off+a),(a,off+a,off+b,b)]
me=bpy.data.meshes.new('READ_ONLY_PROPOSAL_cloud0_fill');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
normal={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'boundary':sum(e.is_boundary for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)};bm.to_mesh(me);bm.free();me.calc_loop_triangles();vv=[v.co.copy() for v in me.vertices];tt=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(vv,tt,all_triangles=True)
def bounds(v):return [[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)]
bb=bounds(vv);out={'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'status':'IN_MEMORY READ-ONLY PRECHECK; no .blend/.glb/render saved; existing objects untouched','hypothesis':'fill original authored CLOUD_0 radial outline at y3.72..3.80; preserve original three tubes. This follows model layout, not a traced source silhouette.','source_limits':'left clipped closure, back, thickness and exact shape inferred; source10 existing side cloud out of frame, not evidence of same source object','body_vertices':len(vv),'body_triangles':len(tt),'body_bounds':bb,'body_topology':normal,'pairs':[]}
selfpairs=tree.overlap(tree);out['non_shared_vertex_self_overlap_pairs']=[list(p) for p in selfpairs if p[0]<p[1] and not set(tt[p[0]])&set(tt[p[1]])]
for o in s.objects:
 if o.type!='MESH':continue
 vo=[o.matrix_world@v.co for v in o.data.vertices];bo=bounds(vo)
 if not all(bb[i][0]<=bo[i][1] and bo[i][0]<=bb[i][1] for i in range(3)):continue
 o.data.calc_loop_triangles();tri=[tuple(t.vertices) for t in o.data.loop_triangles];bt=BVHTree.FromPolygons(vo,tri,all_triangles=True);pairs=tree.overlap(bt)
 entry={'object':o.name,'existing_bounds':bo,'expected_contact':o.name.startswith('CLOUD_0'),'aabb_overlap':True,'triangle_overlap_count':len(pairs),'first_triangle_id_pairs':[list(p) for p in pairs[:32]],'caution':'BVH triangle-overlap diagnostic, not certified volume-penetration magnitude'}
 out['pairs'].append(entry)
out['conclusion']='Do not apply: neighboring triangle intersections exist' if any(p['triangle_overlap_count'] and not p['expected_contact'] for p in out['pairs']) else 'No neighboring triangle surface intersections found by this finite check; not full containment/visibility validation'
(P/'results/left-fill-precheck.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));bpy.data.meshes.remove(me)
