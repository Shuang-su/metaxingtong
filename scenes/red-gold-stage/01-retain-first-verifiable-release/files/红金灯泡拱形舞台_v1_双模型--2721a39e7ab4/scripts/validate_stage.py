import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.kdtree import KDTree
R='/workspace/scratch/fa58bfcf0425/red_gold_stage_v1'
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
 bpy.ops.wm.open_mainfile(filepath=R+'/models/red_gold_stage_'+typ+'.blend');S=bpy.context.scene;bpy.context.view_layer.update();before,v1=summary();verts_by[typ]=v1
 if typ=='textured':
  deps=bpy.context.evaluated_depsgraph_get();tests=[]
  for kind in ['stage_facade','floor','arch_seam']:
   misses=[];count=0
   if kind=='stage_facade':rays=[((x,-3,z),(0,1,0)) for x in [-6.45+i*12.9/130 for i in range(131)] for z in [.65+j*5.65/57 for j in range(58)]]
   elif kind=='floor':rays=[((x,y,.1),(0,0,-1)) for x in [-7.9+i*15.8/80 for i in range(81)] for y in [-7.4+j*11.8/60 for j in range(61)]]
   else:rays=[((r*math.cos(t),-3,.6+r*math.sin(t)),(0,1,0)) for r in [4.595,4.61,4.648,4.652,5.148,5.152,5.198,5.202] for t in [math.pi*i/360 for i in range(1,360)]]
   for a,d in rays:
    hit,loc,norm,idx,obj,mat=S.ray_cast(deps,Vector(a),Vector(d),distance=30);count+=1
    if not hit:misses.append(a)
   tests.append({'name':kind,'samples':count,'miss_count':len(misses),'miss_examples':misses[:12]})
  res['dense_rays']=tests
  # Test lamp back-poles contacting closed gold rails; sockets intentionally embedded.
  supports=[o for o in S.objects if o.type=='MESH' and '金边_' in o.name]
  lamp_checks=[]
  for o in S.objects:
   if '灯排灯泡' not in o.name:continue
   p=o.location+Vector((0,.062,0));inside=[]
   for b in supports:
    q=b.matrix_world.inverted()@p;bb=[Vector(v) for v in b.bound_box]
    if all(min(v[i] for v in bb)-1e-5<=q[i]<=max(v[i] for v in bb)+1e-5 for i in range(3)):inside.append(b.name)
   lamp_checks.append({'lamp':o.name,'support':inside})
  res['lamp_back_pole_contacts']={'count':len(lamp_checks),'unsupported':[x for x in lamp_checks if not x['support']]}
  res['support_design']={'curtain_bottom_z':.6,'stage_top_z':.6,'curtain_top_z':5.5,'beam_bottom_z':5.42,'back_leg_bottom_z':.6,'back_foot_bottom_z':.6,'floor_top_z':0,'base_riser_bottom_z':0,'note':'帘顶嵌入横梁；悬挂柱/后台柱/支脚落于台面。灯泡背极嵌入金框，发光球体不贯穿翼板。仅装配接触测试，不是承载认证。'}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=R+'/models/red_gold_stage_'+typ+'.glb');bpy.context.view_layer.update();after,v2=summary()
 def dist(a,b):
  kd=KDTree(len(b))
  for i,v in enumerate(b):kd.insert(v,i)
  kd.balance();return max(kd.find(v)[2] for v in a)
 res[typ]={'source':before,'true_glb_reimport':after,'symmetric_vertex_distance_units':max(dist(v1,v2),dist(v2,v1)),'triangle_count_match':before['triangles']==after['triangles'],'images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.name!='Render Result']}
 bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/roundtrip_'+typ+'.blend')
res['white_textured_identical_vertex_coordinates']=sorted(verts_by['textured'])==sorted(verts_by['white'])
json.dump(res,open(R+'/qa/geometry_validation.json','w'),ensure_ascii=False,indent=2)
