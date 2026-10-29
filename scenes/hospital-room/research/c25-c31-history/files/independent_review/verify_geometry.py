"""Independent, read-only Blender verification. Never saves or mutates a blend.
Usage: blender -b -t 4 --python verify_geometry.py -- --blend FILE --label C23|C25 --out DIR [--baseline-state FILE] [--allow-seat]
"""
import bpy, bmesh, numpy as np, json, hashlib, argparse, sys, collections, itertools, time
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--blend',required=True);ap.add_argument('--label',required=True);ap.add_argument('--out',required=True);ap.add_argument('--baseline-state');ap.add_argument('--allow-seat',action='store_true');ap.add_argument('--skip-self',action='store_true');ap.add_argument('--topology-only',action='store_true');ap.add_argument('--changed-object',action='append');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);O=Path(a.out);O.mkdir(parents=True,exist_ok=True)
P='Chair • narrow curved wraparound back';S=['Chair • slim back support','Chair • slim back support.001'];SEAT='Chair • green seat';changed=(a.changed_object if a.changed_object else [P]+S)+([SEAT] if a.allow_seat else [])
path=Path(a.blend).resolve();before=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get()
def clean(x):
 if x is None or isinstance(x,(str,bool,int,float)):return x
 if isinstance(x,bpy.types.ID):return {'ID_type':type(x).__name__,'name':x.name}
 try:return [clean(v) for v in x]
 except:return str(x)
def rna(x):
 ret={}
 for p in x.bl_rna.properties:
  k=p.identifier
  if k in ['rna_type','name','name_full','users','use_fake_user','tag','is_evaluated','original','library','asset_data','session_uid','is_runtime_data','is_embedded_data','is_library_indirect','override_library','preview','animation_data'] or p.type in ['COLLECTION','POINTER']:continue
  try:ret[k]=clean(getattr(x,k))
  except:pass
 return ret
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def nodes(tree):
 if not tree:return None
 return {'nodes':{n.name:{'type':n.bl_idname,'properties':rna(n),'inputs':{q.identifier:clean(q.default_value)for q in n.inputs if hasattr(q,'default_value')}}for n in tree.nodes},'links':sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)for l in tree.links)}
def mesh_raw(me):
 return {'vertices':digest([list(v.co)for v in me.vertices]),'faces':digest([list(p.vertices)for p in me.polygons]),'edges':digest([list(e.vertices)for e in me.edges]),'materials':[x.name if x else None for x in me.materials],'face_materials':digest([p.material_index for p in me.polygons]),'face_smooth':digest([p.use_smooth for p in me.polygons]),'uv_layers':{q.name:digest([list(x.uv)for x in q.data])for q in me.uv_layers},'shape_keys':None if not me.shape_keys else {b.name:digest([list(v.co)for v in b.data])for b in me.shape_keys.key_blocks}}
state={'objects':{},'collections':{},'materials':{},'worlds':{},'scenes':{}}
for ob in bpy.data.objects:
 d={'type':ob.type,'properties':rna(ob),'matrix_world':[list(r)for r in ob.matrix_world],'parent':ob.parent.name if ob.parent else None,'collections':sorted(c.name for c in ob.users_collection),'visible_view_layer':ob.visible_get(),'hide_get':ob.hide_get(),'modifiers':[{'type':m.type,'name':m.name,'properties':rna(m)}for m in ob.modifiers],'constraints':[{'type':m.type,'name':m.name,'properties':rna(m)}for m in ob.constraints]}
 if ob.type=='MESH':d['mesh']=mesh_raw(ob.data)
 elif ob.data:d['data']=rna(ob.data)
 state['objects'][ob.name]=d
for c in bpy.data.collections:state['collections'][c.name]={'properties':rna(c),'objects':sorted(o.name for o in c.objects),'children':sorted(x.name for x in c.children)}
for m in bpy.data.materials:state['materials'][m.name]={'properties':rna(m),'nodes':nodes(m.node_tree)}
for w in bpy.data.worlds:state['worlds'][w.name]={'properties':rna(w),'nodes':nodes(w.node_tree)}
for sc in bpy.data.scenes:
 state['scenes'][sc.name]={'camera':sc.camera.name if sc.camera else None,'world':sc.world.name if sc.world else None,'frame':sc.frame_current,'render':rna(sc.render),'cycles':rna(sc.cycles),'view_settings':rna(sc.view_settings),'display_settings':rna(sc.display_settings),'units':rna(sc.unit_settings),'objects':sorted(o.name for o in sc.objects),'compositor':nodes(sc.node_tree),'view_layers':{v.name:{'properties':rna(v),'layer_collections':None}for v in sc.view_layers}}
 def layer(c):return {'name':c.name,'exclude':c.exclude,'holdout':c.holdout,'indirect_only':c.indirect_only,'hide_viewport':c.hide_viewport,'children':[layer(x)for x in c.children]}
 for v in sc.view_layers:state['scenes'][sc.name]['view_layers'][v.name]['layer_collections']=layer(v.layer_collection)
state=json.loads(json.dumps(state))
(O/(a.label+'_scene_state.json')).write_text(json.dumps(state,ensure_ascii=False,indent=2))
R={'label':a.label,'blend':str(path),'sha256_before':before,'method':'Evaluated mesh topology, oriented triangle edges, BVH candidate pairs with independent triangle narrow phase; double-precision arrays plus Blender float32 BVH. No blend modification. This is bounded numerical evidence, not exact certification.','allowed_changed_objects':changed,'geometry':{},'contacts':[]}
if a.baseline_state:
 base=json.load(open(a.baseline_state));diff=[]
 def walk(x,y,path):
  if type(x)!=type(y):diff.append({'path':path,'before':x,'after':y});return
  if isinstance(x,dict):
   for k in sorted(x.keys()|y.keys()):
    if k not in x or k not in y:diff.append({'path':path+'/'+k,'before':x.get(k),'after':y.get(k)})
    else:walk(x[k],y[k],path+'/'+k)
  elif x!=y:diff.append({'path':path,'before':x,'after':y})
 walk(base,state,'')
 def allowed(d):
  # Only geometry + dimensions of explicitly declared objects may change. Materials, transforms, visibility stay locked.
  return any(d['path'].startswith('/objects/'+n+'/mesh/')or d['path']in ['/objects/'+n+'/properties/dimensions','/objects/'+n+'/properties/bound_box']for n in changed)
 permitted=[d for d in diff if allowed(d)];bad=[d for d in diff if not allowed(d)]
 R['invariance']={'all_differences':diff,'permitted_geometry_difference_count':len(permitted),'unexpected_difference_count':len(bad),'unexpected_differences':bad,'pass':not bad,'coverage':'All saved objects, meshes, transforms, camera data, material node parameters, collection and view-layer visibility, worlds, scenes, render/color settings. Driver/animation linkage is not exhaustively serialized.'}

def orient2(a,b,c):return float(np.cross(b-a,c-a))
def ptri2(p,t,eps):
 s=np.array([orient2(t[i],t[(i+1)%3],p)for i in range(3)]);return np.all(s>=-eps)or np.all(s<=eps)
def segseg2(a,b,c,d,eps):
 q=np.array([orient2(a,b,c),orient2(a,b,d),orient2(c,d,a),orient2(c,d,b)])
 if q[0]*q[1]<-eps*eps and q[2]*q[3]<-eps*eps:return True
 for x,u,v,s in [(c,a,b,q[0]),(d,a,b,q[1]),(a,c,d,q[2]),(b,c,d,q[3])]:
  if abs(s)<=eps and np.all(x>=np.minimum(u,v)-eps)and np.all(x<=np.maximum(u,v)+eps):return True
 return False
def segtri(p,q,t,eps):
 e1=t[1]-t[0];e2=t[2]-t[0];direction=q-p;h=np.cross(direction,e2);det=np.dot(e1,h)
 if abs(det)<eps*eps:return False
 inv=1/det;s=p-t[0];u=inv*np.dot(s,h)
 if u<-eps or u>1+eps:return False
 qq=np.cross(s,e1);v=inv*np.dot(direction,qq);tt=inv*np.dot(e2,qq)
 return v>=-eps and u+v<=1+eps and tt>=-eps and tt<=1+eps
def tri_intersect(A,B,eps=1e-9):
 na=np.cross(A[1]-A[0],A[2]-A[0]);nb=np.cross(B[1]-B[0],B[2]-B[0]);la=np.linalg.norm(na);lb=np.linalg.norm(nb)
 if la<1e-20 or lb<1e-20:return False
 da=(B-A[0])@(na/la);db=(A-B[0])@(nb/lb)
 if (np.all(da>eps)or np.all(da<-eps)or np.all(db>eps)or np.all(db<-eps)):return False
 if np.max(np.abs(da))<=eps and np.max(np.abs(db))<=eps:
  ax=np.argmax(np.abs(na));AA=np.delete(A,ax,axis=1);BB=np.delete(B,ax,axis=1)
  return any(ptri2(x,BB,eps)for x in AA)or any(ptri2(x,AA,eps)for x in BB)or any(segseg2(AA[i],AA[(i+1)%3],BB[j],BB[(j+1)%3],eps)for i in range(3)for j in range(3))
 return any(segtri(A[i],A[(i+1)%3],B,eps)or segtri(B[i],B[(i+1)%3],A,eps)for i in range(3))
MD={}
for ob in bpy.data.objects:
 if ob.type!='MESH' or not ob.name.startswith('Chair'):continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=np.array([list(x.co)for x in me.vertices],float);m=np.array(ev.matrix_world);v=v@m[:3,:3].T+m[:3,3];f=np.array([list(x.vertices)for x in me.loop_triangles],int);polys=[list(x.vertices)for x in me.polygons];bm=bmesh.new();bm.from_mesh(me);nonmanifold_vertices=sum(not q.is_manifold for q in bm.verts);bm.free();ev.to_mesh_clear();tree=BVHTree.FromPolygons(v.tolist(),f.tolist(),all_triangles=True,epsilon=0);MD[ob.name]={'v':v,'f':f,'tree':tree,'tri':v[f]}
 tri=v[f];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
 ed=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);es=np.sort(ed,axis=1);u,inv,cnt=np.unique(es,axis=0,return_inverse=True,return_counts=True);sg=np.where(ed[:,0]<ed[:,1],1,-1);balance=np.bincount(inv,weights=sg,minlength=len(u))
 from scipy.sparse import coo_matrix
 from scipy.sparse.csgraph import connected_components
 graph=coo_matrix((np.ones(len(u)),(u[:,0],u[:,1])),shape=(len(v),len(v)));nc,labels=connected_components(graph,directed=False)
 vols=np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2]))/6;compvol=[float(vols[labels[f[:,0]]==i].sum())for i in range(nc)]
 g={'vertices':len(v),'polygons':len(polys),'triangles':len(f),'unique_edges_triangulated':len(u),'nonmanifold_vertex_count':nonmanifold_vertices,'boundary_edge_count':int(np.sum(cnt==1)),'nonmanifold_edge_count':int(np.sum(cnt!=2)),'inconsistent_oriented_edge_count':int(np.sum(balance!=0)),'connected_components':int(nc),'component_signed_volumes':compvol,'signed_volume':float(vols.sum()),'min_triangle_area':float(area.min()),'degenerate_triangle_count_area_le_1e_14':int(np.sum(area<=1e-14)),'euler_characteristic':int(len(v)-len(u)+len(f)),'finite':bool(np.all(np.isfinite(v))),'world_bounds':[v.min(0).tolist(),v.max(0).tolist()]}
 g['closed_oriented_manifold_numerical_pass']=bool(g['finite']and not g['nonmanifold_vertex_count']and not g['nonmanifold_edge_count']and not g['inconsistent_oriented_edge_count']and not g['degenerate_triangle_count_area_le_1e_14']and all(q>0 for q in compvol))
 if not a.skip_self and ob.name in changed:
  start=time.time();pairs=tree.overlap(tree);cand=[(i,j)for i,j in pairs if i<j and not np.intersect1d(f[i],f[j],assume_unique=True).size];hits=[];limit=2000000
  for i,j in cand[:limit]:
   if tri_intersect(tri[i],tri[j]):hits.append([i,j])
  g['self_intersection']={'bvh_ordered_overlap_pairs':len(pairs),'nonadjacent_unique_candidate_pairs':len(cand),'tested_pairs':min(len(cand),limit),'confirmed_numerical_triangle_intersections':len(hits),'first_100_pairs':hits[:100],'complete_within_scope':len(cand)<=limit,'pass':len(cand)<=limit and not hits,'seconds':time.time()-start,'scope':'Nonadjacent triangles with no shared mesh vertex. Shared-edge/shared-vertex pairs excluded as expected adjacency; no exact rational certificate.'}
 R['geometry'][ob.name]=g;print('GEOMETRY',ob.name,g,flush=True)
# Contact distances: evaluate vertices from both directions, evenly bounded at 10000 per mesh.
# Triangle BVH cross-overlaps are independently narrow-phase tested where present.
for n1,n2 in ([] if a.topology_only else itertools.combinations(MD,2)):
 A=MD[n1];B=MD[n2];best=(float('inf'),None);sample_counts=[]
 for src,dst,way in [(A,B,'A_to_B'),(B,A,'B_to_A')]:
  inds=np.unique(np.linspace(0,len(src['v'])-1,min(10000,len(src['v']))).astype(int));sample_counts.append(len(inds))
  for ix in inds:
   pt,n,fi,dist=dst['tree'].find_nearest(Vector(src['v'][ix]))
   if dist is not None and dist<best[0]:best=(float(dist),{'direction':way,'source_vertex_index':int(ix),'source_xyz':src['v'][ix].tolist(),'nearest_xyz':list(pt),'destination_triangle_index':int(fi)})
 gap=np.maximum(np.maximum(A['v'].min(0)-B['v'].max(0),B['v'].min(0)-A['v'].max(0)),0);bboxgap=float(np.linalg.norm(gap));pairs=[];hits=[]
 if bboxgap<1e-8:
  pairs=A['tree'].overlap(B['tree'])
  for i,j in pairs[:200000]:
   if tri_intersect(A['tri'][i],B['tri'][j]):hits.append([i,j])
 c={'objects':[n1,n2],'sampled_vertices_per_direction':sample_counts,'min_sampled_vertex_to_surface_distance':best[0],'nearest_witness':best[1],'aabb_gap_lower_bound':bboxgap,'bvh_cross_candidate_pairs':len(pairs),'tested_cross_pairs':min(len(pairs),200000),'confirmed_triangle_crossings':len(hits),'first_20_crossings':hits[:20],'cross_test_complete':len(pairs)<=200000,'contact_class':'intersecting_surfaces'if hits else 'within_0.5mm_sampled_proximity'if best[0]<=0.0005 else 'separated_sampled_surfaces','limitation':'Vertex-to-surface minimum is a finite sampled upper bound; AABB separation is a rigorous float-array geometric lower bound. Noncrossing containment is not certified by this test.'};R['contacts'].append(c);print('CONTACT',n1,n2,best[0],len(hits),flush=True)
R['sha256_after']=hashlib.sha256(path.read_bytes()).hexdigest();R['input_unchanged']=before==R['sha256_after'];(O/(a.label+'_geometry_report.json')).write_text(json.dumps(R,ensure_ascii=False,indent=2));print('DONE',a.label,flush=True)
