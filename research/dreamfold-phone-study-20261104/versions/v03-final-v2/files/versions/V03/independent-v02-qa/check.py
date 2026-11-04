import bpy,bmesh,pathlib,json,hashlib,math,sys
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
sys.path.insert(0,'/workspace/scratch/fa58bfcf0425/lakeleaf-vein-contact-audit-20261104/scripts');from triangle_distance import triangle_triangle2
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/dreamfold-phone-study-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-dreamfold-phone-v02-qa-20261104');R={};S={}
def snap():
 d={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();v=[tuple(o.matrix_world@p.co)for p in o.data.vertices];fi=[tuple(t.vertices)for t in o.data.loop_triangles];bm=bmesh.new();bm.from_mesh(o.data)
  d[o.name]={'vertices':v,'faces':[tuple(p.vertices)for p in o.data.polygons],'triangles':fi,'uv':[[tuple(x.uv)for x in uv.data]for uv in o.data.uv_layers],'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)};bm.free()
 return d
for mode in ['material','white']:
 f=P/'models'/f'phone-{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;S[mode]=snap();R[mode]={'blend_sha':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_count':len(S[mode]),'render_size':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'film_transparent':s.render.film_transparent,'cameras':{o.name:{'matrix':[list(r)for r in o.matrix_world],'lens':o.data.lens,'sensor_fit':o.data.sensor_fit,'frame':[tuple(v)for v in o.data.view_frame(scene=s)]}for o in s.objects if o.type=='CAMERA'},'audit':{n:{k:v[k]for k in ['nonmanifold','degenerate','signed_volume']}for n,v in S[mode].items()}}
 f=P/'models'/f'phone-{mode}.glb';bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(f));g=snap();err={}
 for n,a in S[mode].items():
  b=g[n];errs=[]
  for x,y in [(a['vertices'],b['vertices']),(b['vertices'],a['vertices'])]:
   kd=KDTree(len(y))
   for i,v in enumerate(y):kd.insert(v,i)
   kd.balance();errs.append(max(kd.find(v)[2]for v in x))
  err[n]=max(errs)
 R[mode].update({'glb_sha':hashlib.sha256(f.read_bytes()).hexdigest(),'glb_mesh_count':len(g),'glb_camera_count':sum(o.type=='CAMERA'for o in bpy.context.scene.objects),'glb_bidirectional_nearest_vertex_error':err})
R['shared']={n:S['material'][n]==S['white'][n]for n in S['material']};D=S['material'];ts={n:[[d['vertices'][i]for i in t]for t in d['triangles']]for n,d in D.items()};trees={n:BVHTree.FromPolygons(d['vertices'],d['triangles'],all_triangles=True)for n,d in D.items()}
def dist(a,b):
 best=math.inf
 for x in ts[a]:
  xl=[min(p[i]for p in x)for i in range(3)];xh=[max(p[i]for p in x)for i in range(3)]
  for y in ts[b]:
   lo=sum(max(0,min(p[i]for p in y)-xh[i],xl[i]-max(p[i]for p in y))**2for i in range(3))
   if lo>best:continue
   best=min(best,triangle_triangle2(x,y))
   if best==0:return 0.
 return math.sqrt(best)
R['all_pair_surface_distance']={}
for j,a in enumerate(D):
 for b in list(D)[j+1:]:R['all_pair_surface_distance'][a+' / '+b]={'distance':dist(a,b),'bvh_face_pairs':len(trees[a].overlap(trees[b]))}
(Q/'technical.json').write_text(json.dumps(R,indent=2));print('DONE')
