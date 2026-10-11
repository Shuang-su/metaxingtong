import bpy,bmesh,json,hashlib,os,math
from mathutils import Vector
from collections import Counter
from mathutils.bvhtree import BVHTree
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1';Q=R+'/qa/independent';out={'units':'相对模型单位，非测绘实米','files':{}}
for fn in sorted(os.listdir(R+'/models')):
 if fn.endswith(('.blend','.glb')):out['files'][fn]=hashlib.sha256(open(R+'/models/'+fn,'rb').read()).hexdigest()
def facts():
 ret={}; tris=[]; by_object={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  me=o.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  ret[o.name]={'triangles':len(me.loop_triangles),'nonmanifold_edges_welded':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'degenerate_triangles':sum(t.area<1e-12 for t in me.loop_triangles),'materials':[m.name for m in me.materials]};bm.free()
  ot=[tuple(sorted(tuple(float(v) for v in (o.matrix_world@me.vertices[i].co)) for i in t.vertices)) for t in me.loop_triangles];tris.extend(ot);by_object[o.name]=Counter(ot)
 return ret,Counter(tris),by_object
for typ in ['textured','white']:
 path=R+'/models/dark_cell_'+typ+'.blend';bpy.ops.wm.open_mainfile(filepath=path);s=bpy.context.scene;bpy.context.view_layer.update();src,tri,src_by=facts();rec={'source':src}
 if typ=='textured':
  deps=bpy.context.evaluated_depsgraph_get();rays=[]
  # Test full-width/high passage through entrance and gate, excluding floor and overhead fixtures.
  for nm,x0,x1,y0,y1,z0,z1 in [('入口',2.0,2.80,-3.5,-2.9,.02,2.35),('敞门',2.22,2.87,-.3,1.25,.15,2.35)]:
   hits=[];n=0
   for i in range(51):
    for k in range(101):
     x=x0+(x1-x0)*i/50;z=z0+(z1-z0)*k/100;n+=1;h=s.ray_cast(deps,Vector((x,y0,z)),Vector((0,1,0)),distance=y1-y0)
     if h[0]:hits.append({'x':x,'z':z,'object':h[4].name})
   rays.append({'region':nm,'samples':n,'blocked':len(hits),'examples':hits[:8]})
  rec['passage_dense_rays']=rays
  # World-space surface intersections/contact graph; finite solids remain separate objects.
  objects=[o for o in s.objects if o.type=='MESH'];trees={}
  for o in objects:trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],epsilon=1e-5)
  contacts={o.name:[] for o in objects}
  for i,a in enumerate(objects):
   for b in objects[i+1:]:
    if trees[a.name].overlap(trees[b.name]):contacts[a.name].append(b.name);contacts[b.name].append(a.name)
  rec['physical_surface_contact_graph']=contacts
  rec['no_detected_surface_contact']=[n for n,v in contacts.items() if not v]
  # Derive current shell dimensions from actual world-space solids, then fire near-contact rays.
  def bounds(name):
   o=bpy.data.objects[name];v=[o.matrix_world@Vector(c) for c in o.bound_box];return [[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]]
  xmin=bounds('推定_左墙')[1][0];xmax=bounds('推定_右墙')[0][0];yb=bounds('推定_后墙')[0][1];yf=bounds('推定_前墙左')[1][1];zf=bounds('推定_厚地板')[1][2];zt=bounds('推定_厚顶板')[0][2]
  seam=[]
  for label in ['后墙上下','侧墙上下','地顶四周']:
   misses=[];n=0
   for e in [.00001,.0001,.001,.01,.03]:
    for i in range(301):
     t=i/300;xx=xmin+e+(xmax-xmin-2*e)*t;yy=yf+e+(yb-yf-2*e)*t
     if label=='后墙上下':tests=[((xx,yb-e,zf+e),(0,1,0)),((xx,yb-e,zt-e),(0,1,0))]
     elif label=='侧墙上下':tests=[((x,y,z),d) for x,d in [(xmin+e,(-1,0,0)),(xmax-e,(1,0,0))] for y in [yy] for z in [zf+e,zt-e]]
     else:tests=[((x,y,z),d) for x,y in [(xx,yf+e),(xx,yb-e),(xmin+e,yy),(xmax-e,yy)] for z,d in [(zf+e,(0,0,-1)),(zt-e,(0,0,1))]]
     for p,d in tests:
      h=s.ray_cast(deps,Vector(p),Vector(d),distance=.5);n+=1
      if not h[0]:misses.append(p)
   seam.append({'region':label,'samples':n,'misses':len(misses),'examples':misses[:8]})
  rec['shell_dense_near_seams']=seam
  # Independently sample full area-light footprints toward their physical covers.
  lighting=[]
  for o in s.objects:
   if o.type!='LIGHT' or o.data.type!='AREA':continue
   bad=[];n=0
   for i in range(11):
    for j in range(11):
     x=o.data.size*(i/10-.5);y=o.data.size_y*(j/10-.5);origin=o.matrix_world@Vector((x,y,0));direction=o.matrix_world.to_3x3()@Vector((0,0,1));h=s.ray_cast(deps,origin,direction,distance=.5);n+=1
     if not h[0] or '灯罩' not in h[4].name:bad.append({'i':i,'j':j,'first_hit':h[4].name if h[0] else None})
   lighting.append({'name':o.name,'samples':n,'bad_cover_hits':len(bad),'examples':bad[:5]})
  rec['full_light_face_cover_tests']=lighting
 # Record complete scene render before actual deletion/import. Fixed camera and physical lights retained for apples-to-apples material check.
 s.render.resolution_percentage=50;s.cycles.samples=16;s.cycles.use_denoising=False;s.render.filepath=Q+'/'+typ+'_blend.png';bpy.ops.render.render(write_still=True)
 for o in list(s.objects):
  if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=R+'/models/dark_cell_'+typ+'.glb');bpy.context.view_layer.update();imp,tri2,imp_by=facts();rec['actual_import']=imp;rec['world_triangle_exact_multiset_equal']=tri==tri2;rec['exact_triangle_difference_count']=sum((tri-tri2).values())+sum((tri2-tri).values());
 # Distance from all triangle vertices and centroids to the other actual surface, robust to triangulation and rounding boundaries.
 def surface_distance(a,b):
  bv=[];faces=[]
  for tt in b:
   faces.append(tuple(range(len(bv),len(bv)+3)));bv.extend(tt)
  tree=BVHTree.FromPolygons(bv,faces,all_triangles=True);mx=0
  for tt in a:
   pts=[Vector(v) for v in tt];pts.append(sum(pts,Vector())/3)
   for v in pts:
    h=tree.find_nearest(v);mx=max(mx,h[3])
  return mx
 rec['symmetric_surface_distance_units']=max(surface_distance(tri,tri2),surface_distance(tri2,tri));rec['object_surface_distances_units']={n:max(surface_distance(a,imp_by[n]),surface_distance(imp_by[n],a)) for n,a in src_by.items()};rec['triangles_source']=sum(tri.values());rec['triangles_glb']=sum(tri2.values());rec['visibility_animation']={'actions':len(bpy.data.actions),'hidden_meshes':[o.name for o in s.objects if o.type=='MESH' and(o.hide_render or o.hide_viewport)]}
 s.render.filepath=Q+'/'+typ+'_glb_same_camera_lights.png';bpy.ops.render.render(write_still=True);out[typ]=rec
json.dump(out,open(Q+'/independent_result.json','w'),ensure_ascii=False,indent=2)
