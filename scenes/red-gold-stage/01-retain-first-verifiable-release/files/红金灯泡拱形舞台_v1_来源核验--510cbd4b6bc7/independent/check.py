import bpy,bmesh,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/scratch/fa58bfcf0425/red_gold_stage_v1'
res={'hashes':{}}
for t in ['textured','white']:
 for ext in ['blend','glb']:
  p=R+'/models/red_gold_stage_'+t+'.'+ext;res['hashes'][p.split('/')[-1]]=hashlib.sha256(open(p,'rb').read()).hexdigest()
def geom():
 ds={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  m=o.data;m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles];bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  ds[o.name]={'o':o,'v':v,'f':f,'bvh':BVHTree.FromPolygons(v,f,all_triangles=True),'topology':{'nonmanifold':sum(not e.is_manifold for e in bm.edges),'inconsistent_edges':sum(not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True),'degenerate':sum((v[b]-v[a]).cross(v[c]-v[a]).length<1e-10 for a,b,c in f)}};bm.free()
 return ds
def inside(d,p):
 if any(p[k]<min(v[k] for v in d['v'])-1e-6 or p[k]>max(v[k] for v in d['v'])+1e-6 for k in range(3)):return False
 near=d['bvh'].find_nearest(p)
 if near[0] is None:return False
 return (p-near[0]).dot(near[1])<=1e-6
bpy.ops.wm.open_mainfile(filepath=R+'/models/red_gold_stage_textured.blend');bpy.context.view_layer.update();d=geom()
res['topology']={k:x['topology'] for k,x in d.items() if x['topology']['nonmanifold'] or x['topology']['inconsistent_edges'] or x['topology']['volume']<=0 or x['topology']['degenerate']}
res['column_gaps']=[]
for name in ['悬挂支柱_-4.75','悬挂支柱_4.75']:
 o=d[name]['o'];p=Vector((o.location.x,o.location.y,max(v.z for v in d[name]['v'])));hit=d['帘顶部悬挂横梁']['bvh'].ray_cast(p+Vector((0,0,1e-6)),Vector((0,0,1)))
 res['column_gaps'].append({'column':name,'top':list(p),'ray_distance_to_beam_exit_or_entry':hit[3],'top_inside_beam':inside(d['帘顶部悬挂横梁'],p)})
res['bulbs']=[]
for n,x in d.items():
 if '灯泡' not in n:continue
 o=x['o'];back=max(x['v'],key=lambda p:p.y);front=min(x['v'],key=lambda p:p.y)
 supports=[k for k,v in d.items() if '灯泡' not in k and inside(v,back)]
 pierced=[k for k,v in d.items() if '灯泡' not in k and inside(v,front)]
 res['bulbs'].append({'name':n,'back_support':supports,'front_inside_structure':pierced})
res['mounts']=[]
for side in ['左','右']:
 x=-4.3 if side=='左' else 4.3
 for yy in [.225,.38]:
  p=Vector((x,yy,4.97));res['mounts'].append({'point':list(p),'inside':[k for k,v in d.items() if '灯泡' not in k and inside(v,p)]})
res['curtain_beam_surface_intersections']=len(d['褶皱黑帘_闭合薄实体']['bvh'].overlap(d['帘顶部悬挂横梁']['bvh']))
res['front_hemisphere_intrusions']=[]
structure={k:x for k,x in d.items() if '灯泡' not in k}
for n,x in d.items():
 if '灯泡' not in n:continue
 cy=x['o'].location.y
 for p in x['v']:
  if p.y>cy+1e-6:continue
  hits=[k for k,y in structure.items() if inside(y,p)]
  if hits:res['front_hemisphere_intrusions'].append({'bulb':n,'point':list(p),'hits':hits})
res['dense_target_rays']=[]
for label,targets,rays in [
 ('arch_trim_board_seams',[x for k,x in d.items() if '拱台' in k or '侧景板' in k],[(Vector((r*math.cos(a),-.1,.6+r*math.sin(a))),Vector((0,1,0))) for r in [4.601,4.649,4.651,5.149,5.151,5.199,5.201] for a in [math.pi*j/720 for j in range(1,720)]]),
 ('riser_top_and_seams',[x for k,x in d.items() if '台阶实体' in k],[(Vector((x,y,1)),Vector((0,0,-1))) for x in [-6.499+12.998*j/260 for j in range(261)] for y in [-1.649,-1.23,-1.221,-1.219,-1.21,-.801,-.799,-.79,0,1,2.799]])]:
 misses=[]
 for p,v in rays:
  if not any(x['bvh'].ray_cast(p,v,2)[0] is not None for x in targets):misses.append(list(p))
 res['dense_target_rays'].append({'label':label,'count':len(rays),'miss_count':len(misses),'examples':misses[:5]})
res['contact_graph_note']='Exact BVH surface intersections plus vertex containment; coplanar/tangent-only contacts may be included by 1e-6 signed nearest threshold.'
adj={k:set() for k in d}
ns=list(d)
for i,a in enumerate(ns):
 av=d[a]['v'];alo=[min(p[k] for p in av) for k in range(3)];ahi=[max(p[k] for p in av) for k in range(3)]
 for b in ns[i+1:]:
  bv=d[b]['v'];blo=[min(p[k] for p in bv) for k in range(3)];bhi=[max(p[k] for p in bv) for k in range(3)]
  if any(ahi[k]<blo[k]-1e-6 or bhi[k]<alo[k]-1e-6 for k in range(3)):continue
  if d[a]['bvh'].overlap(d[b]['bvh']) or any(inside(d[b],p) for p in av) or any(inside(d[a],p) for p in bv):adj[a].add(b);adj[b].add(a)
seen=set();groups=[]
for n in ns:
 if n in seen:continue
 todo=[n];g=[]
 while todo:
  k=todo.pop()
  if k in seen:continue
  seen.add(k);g.append(k);todo.extend(adj[k]-seen)
 groups.append(g)
res['real_geometry_components']=groups
res['column_neighbors']={k:list(v) for k,v in adj.items() if '悬挂支柱' in k}
# Independent true imports, triangle-position multiset signature as well as nearest geometry.
def trisig(ds):
 return sorted(tuple(sorted(tuple(round(z,5) for z in ds[n]['v'][i]) for i in f)) for n in ds for f in ds[n]['f'])
def haus(a,b):
 kd=KDTree(len(b))
 for i,p in enumerate(b):kd.insert(p,i)
 kd.balance();return max(kd.find(p)[2] for p in a)
def centers(ds):return [sum((x['v'][i] for i in f),Vector())/3 for x in ds.values() for f in x['f']]
res['roundtrip']={}
base=trisig(d)
for t in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/red_gold_stage_'+t+'.blend');bpy.context.view_layer.update();before=geom();sig=trisig(before)
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=R+'/models/red_gold_stage_'+t+'.glb');bpy.context.view_layer.update();after=geom()
 res['roundtrip'][t]={'source_mesh_count':len(before),'import_mesh_count':len(after),'triangles_source':sum(len(v['f']) for v in before.values()),'triangles_import':sum(len(v['f']) for v in after.values()),'rounded_1e_5_triangle_multiset_equal':sig==trisig(after),'symmetric_triangle_centroid_distance':max(haus(centers(before),centers(after)),haus(centers(after),centers(before))),'matches_textured_geometry':sig==base,'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images]}
json.dump(res,open(R+'/independent/geometry_checks.json','w'),ensure_ascii=False,indent=2)
print('INDEPENDENT_DONE')
