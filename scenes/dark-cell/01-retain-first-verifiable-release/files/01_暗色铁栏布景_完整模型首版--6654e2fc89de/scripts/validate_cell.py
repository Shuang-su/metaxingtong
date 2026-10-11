import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.kdtree import KDTree
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1'
def summary():
 out={'mesh_objects':0,'vertices':0,'triangles':0,'degenerate_triangles':0,'invalid_normals':0,'nonfinite_uv':0,'missing_uv':[],'open_objects':[],'nonpositive_volume':[]};coords=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  out['mesh_objects']+=1;me=o.data;me.calc_loop_triangles();out['vertices']+=len(me.vertices);out['triangles']+=len(me.loop_triangles);coords.extend(tuple(o.matrix_world@v.co) for v in me.vertices)
  for t in me.loop_triangles:
   a,b,c=[me.vertices[i].co for i in t.vertices]
   if (b-a).cross(c-a).length<1e-10:out['degenerate_triangles']+=1
  out['invalid_normals']+=sum(not all(math.isfinite(x) for x in p.normal) or p.normal.length<.1 for p in me.polygons)
  if not me.uv_layers:out['missing_uv'].append(o.name)
  for uv in me.uv_layers:out['nonfinite_uv']+=sum(not all(math.isfinite(x) for x in p.uv) for p in uv.data)
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);edges=[e for e in bm.edges if not e.is_manifold]
  if edges:out['open_objects'].append({'name':o.name,'nonmanifold_edges':len(edges)})
  if bm.calc_volume(signed=True)<=0:out['nonpositive_volume'].append(o.name)
  bm.free()
 out['bounds_min']=[min(v[i] for v in coords) for i in range(3)];out['bounds_max']=[max(v[i] for v in coords) for i in range(3)]
 return out,coords
res={};verts_by={}
for typ in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/dark_cell_'+typ+'.blend');S=bpy.context.scene;bpy.context.view_layer.update();before,v1=summary();verts_by[typ]=v1
 if typ=='textured':
  deps=bpy.context.evaluated_depsgraph_get();tests=[]
  cases={
   '地板密集':[((x,y,.01),(0,0,-1)) for x in [-3.19+i*.0638 for i in range(101)] for y in [-3.09+j*.0538 for j in range(101)]],
   '天花密集':[((x,y,4.29),(0,0,1)) for x in [-3.19+i*.0638 for i in range(101)] for y in [-3.09+j*.0538 for j in range(101)]],
   '后墙近缝':[((x,2.29,z),(0,1,0)) for x in [-3.199+i*.06398 for i in range(101)] for z in [.001+j*.04298 for j in range(101)]],
   '两侧墙近缝':[((sgn*3.199,y,z),(sgn,0,0)) for sgn in [-1,1] for y in [-3.099+j*.05398 for j in range(101)] for z in [.001+k*.08596 for k in range(51)]],
  }
  for kind,rays in cases.items():
   misses=[]
   for a,d in rays:
    hit,*_=S.ray_cast(deps,Vector(a),Vector(d),distance=.4)
    if not hit:misses.append(a)
   tests.append({'name':kind,'samples':len(rays),'miss_count':len(misses),'miss_examples':misses[:12]})
  res['dense_shell_rays']=tests
  # Passage tests: small centerline ray steps through true front portal and open gate.
  passage=[]
  for a,d,length in [((2.4,-3.6,1.5),(0,1,0),.8),((2.55,-.25,1.5),(0,1,0),.65)]:
   hit,*_=S.ray_cast(deps,Vector(a),Vector(d),distance=length);passage.append({'origin':a,'length':length,'unobstructed':not hit})
  res['entrance_and_gate_clearance_rays']=passage
  res['bar_socket_design']={'bar_bottom':.07,'lower_rail_top':.13,'bar_top':3.31,'upper_rail_bottom':3.245,'socket_overlap_bottom':.06,'socket_overlap_top':.065,'count':13,'gate_hinges':3,'note':'所有主栏嵌入上下实体轨；门框与铰链为实体装配。'}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=R+'/models/dark_cell_'+typ+'.glb');bpy.context.view_layer.update();after,v2=summary()
 def dist(a,b):
  kd=KDTree(len(b))
  for i,v in enumerate(b):kd.insert(v,i)
  kd.balance();return max(kd.find(v)[2] for v in a)
 res[typ]={'source':before,'true_glb_reimport':after,'symmetric_vertex_distance_units':max(dist(v1,v2),dist(v2,v1)),'triangle_count_match':before['triangles']==after['triangles'],'images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.name!='Render Result']}
 bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/roundtrip_'+typ+'.blend')
res['white_textured_identical_vertex_coordinates']=sorted(verts_by['textured'])==sorted(verts_by['white'])
json.dump(res,open(R+'/qa/geometry_validation.json','w'),ensure_ascii=False,indent=2)
