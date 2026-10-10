import bpy,bmesh,json,math,os
from mathutils import Vector
from mathutils.kdtree import KDTree
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom'
def summary():
 out={'mesh_objects':0,'vertices':0,'triangles':0,'degenerate_triangles':0,'invalid_normals':0,'nonfinite_uv':0,'missing_uv':[],'open_components':[],'closed_components':0};coords=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  out['mesh_objects']+=1;me=o.data;me.calc_loop_triangles();out['vertices']+=len(me.vertices);out['triangles']+=len(me.loop_triangles)
  coords.extend([tuple(o.matrix_world@v.co) for v in me.vertices])
  for t in me.loop_triangles:
   a,b,c=[me.vertices[i].co for i in t.vertices]
   if (b-a).cross(c-a).length<1e-10:out['degenerate_triangles']+=1
  out['invalid_normals']+=sum(not all(math.isfinite(x) for x in p.normal) or p.normal.length<.1 for p in me.polygons)
  if not me.uv_layers:out['missing_uv'].append(o.name)
  for uv in me.uv_layers:
   out['nonfinite_uv']+=sum(not all(math.isfinite(x) for x in p.uv) for p in uv.data)
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);edges=[e for e in bm.edges if not e.is_manifold]
  if edges:out['open_components'].append({'name':o.name,'nonmanifold_edges':len(edges)})
  else:out['closed_components']+=1
  bm.free()
 out['bounds_min']=[min(v[i] for v in coords) for i in range(3)];out['bounds_max']=[max(v[i] for v in coords) for i in range(3)]
 return out,coords
result={};source_vertices_by_variant={}
for typ in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');S=bpy.context.scene;bpy.context.view_layer.update();before,verts=summary();source_vertices_by_variant[typ]=verts
 if typ=='textured':
  deps=bpy.context.evaluated_depsgraph_get();rays=[]
  for name,start,dir in [('main_opening',(0,-.5,2.8),(0,1,0)),('left_opening',(-3.95,-.5,2.8),(0,1,0)),('solid_wall',(-3.2,-.5,2.8),(0,1,0)),('floor',(0,-1,1),(0,0,-1)),('left_service_entry',(-5,-1,.4),(1,0,0)),('right_service_entry',(5,-1,.4),(-1,0,0))]:
   hit,loc,norm,idx,obj,mat=S.ray_cast(deps,Vector(start),Vector(dir),distance=20);rays.append({'test':name,'hit':hit,'object':obj.name if obj else None,'point':list(loc) if hit else None})
  result['rays']=rays
  def contains(name,point):
   o=bpy.data.objects[name];q=o.matrix_world.inverted()@Vector(point);bb=[Vector(v) for v in o.bound_box];return all(min(v[i] for v in bb)-1e-5 <= q[i] <= max(v[i] for v in bb)+1e-5 for i in range(3))
  result['brace_endpoints']=[{'side':'left','lower_inside_mount':contains('左撑杆_实体安装座',(-2.59,.87,3.27)),'upper_inside_lifted_panel':contains('Lifted_wood_awning_panel',(-2.59,1.90,4.18))},{'side':'right','lower_inside_mount':contains('右撑杆_实体安装座',(3.57,.87,3.27)),'upper_inside_lifted_panel':contains('Lifted_wood_awning_panel',(3.57,1.90,4.18))}]
  result['brace_test_note']='端点变换到安装座/掀板局部包围盒内检查；安装座与窗框有正体积交叠。非结构承载分析。'
  lamp=bpy.data.objects['Cylindrical_amber_table_lamp'];v=[lamp.matrix_world@Vector(c) for c in lamp.bound_box];result['lamp_bounds']={'min':[min(x[i] for x in v) for i in range(3)],'max':[max(x[i] for x in v) for i in range(3)],'hatch_min_z':4.1,'main_opening_x':[-2.64,3.62],'wall_front_y':.91,'assessment':'发光圆柱整体位于开口前方，低于掀板；不穿墙/掀板。'}
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=R+'/models/seaside_bar_complete_'+typ+'.glb');bpy.context.view_layer.update();after,v2=summary()
 def dist(a,b):
  kd=KDTree(len(b))
  for i,v in enumerate(b):kd.insert(v,i)
  kd.balance();return max(kd.find(v)[2] for v in a)
 result[typ]={'source':before,'true_glb_reimport':after,'symmetric_vertex_distance_units':max(dist(verts,v2),dist(v2,verts)),'triangle_count_match':before['triangles']==after['triangles']}
 bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/roundtrip_'+typ+'.blend')
result['white_textured_identical_vertex_coordinates']=sorted(source_vertices_by_variant['textured'])==sorted(source_vertices_by_variant['white'])
json.dump(result,open(R+'/qa/geometry_validation.json','w'),ensure_ascii=False,indent=2)
