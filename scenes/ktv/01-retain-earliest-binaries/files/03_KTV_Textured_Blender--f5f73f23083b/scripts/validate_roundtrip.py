import bpy,os,json,hashlib,math
from mathutils import Vector,kdtree
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def mesh_data(objs):
 d={};tri=[];mi=[1e20]*3;ma=[-1e20]*3;area=0
 for o in objs:
  vs=[tuple(o.matrix_world@v.co) for v in o.data.vertices];o.data.calc_loop_triangles();d[o.name]=vs
  for p in vs:
   for j in range(3):mi[j]=min(mi[j],p[j]);ma[j]=max(ma[j],p[j])
  for t in o.data.loop_triangles:
   pts=[Vector(vs[i]) for i in t.vertices];tri.append(sorted(tuple(round(x,4) for x in p) for p in pts));area+=(pts[1]-pts[0]).cross(pts[2]-pts[0]).length/2
 return d,{'mesh_objects':len(objs),'triangles':len(tri),'bounds_min':mi,'bounds_max':ma,'surface_area_m2':area,'triangle_hash_rounded_1e4':hashlib.sha256(repr(sorted(tri)).encode()).hexdigest(),'all_meshes_have_uv':all(bool(o.data.uv_layers) for o in objs)}
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Xingtong_KTV_Textured.blend')
baseobjs=[o for o in bpy.context.scene.objects if o.type=='MESH' and not any(c.name=='09_Optional_Moving_Balloon_Dog' for c in o.users_collection)]
_,native_textured_all=mesh_data([o for o in bpy.context.scene.objects if o.type=='MESH'])
base,bs=mesh_data(baseobjs);results={'source':bs,'scope':'All stage/city/sky-decoration meshes except the separately supplied optional moving balloon dog. Native textured and white Blends include the identical dog collection hidden by default.'}
for variant in ['Textured','White']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ROOT+'/models/Xingtong_KTV_'+variant+'.glb')
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];imp,s=mesh_data(objs)
 s['same_object_names']=set(imp)==set(base);errors=[];missing=[]
 for name,verts in base.items():
  if name not in imp:missing.append(name);continue
  for a,b in [(verts,imp[name]),(imp[name],verts)]:
   kd=kdtree.KDTree(len(b))
   for i,p in enumerate(b):kd.insert(p,i)
   kd.balance()
   for p in a:errors.append(kd.find(p)[2])
 s['max_bidirectional_vertex_error_m']=max(errors);s['missing_objects']=missing
 s['triangle_count_matches_source']=s['triangles']==bs['triangles'];s['bounds_max_error_m']=max(abs(s[k][i]-bs[k][i]) for k in ['bounds_min','bounds_max'] for i in range(3))
 s['surface_area_relative_error']=abs(s['surface_area_m2']/bs['surface_area_m2']-1)
 s['all_used_images_embedded']=all(n.image and n.image.packed_file for m in bpy.data.materials if m.use_nodes and m.users for n in m.node_tree.nodes if n.type=='TEX_IMAGE')
 s['pass']=s['same_object_names'] and s['triangle_count_matches_source'] and s['max_bidirectional_vertex_error_m']<1e-4 and s['surface_area_relative_error']<1e-5 and s['all_meshes_have_uv'] and s['all_used_images_embedded']
 results[variant]=s
 bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/qa/roundtrip_'+variant+'.blend',compress=True)
sourcewhite=json.load(open(ROOT+'/qa/blender_white_geometry.json'));sourcetex=json.load(open(ROOT+'/qa/blender_textured_geometry.json'))
results['white_textured_native_geometry_identical']=sourcewhite['world_triangle_coordinate_sha256']==sourcetex['world_triangle_coordinate_sha256']
results['white_textured_GLB_geometry_identical']=results['White']['triangle_hash_rounded_1e4']==results['Textured']['triangle_hash_rounded_1e4']
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Xingtong_KTV_White.blend')
_,native_white_all=mesh_data([o for o in bpy.context.scene.objects if o.type=='MESH'])
results['native_all_mesh_count']=native_white_all['mesh_objects']
results['native_all_geometry_including_hidden_dog_identical']=native_white_all['triangle_hash_rounded_1e4']==native_textured_all['triangle_hash_rounded_1e4']
results['PASS']=results['native_all_geometry_including_hidden_dog_identical'] and results['White']['pass'] and results['Textured']['pass'] and results['white_textured_native_geometry_identical'] and results['white_textured_GLB_geometry_identical']
json.dump(results,open(ROOT+'/qa/roundtrip_validation.json','w'),indent=2);print(json.dumps(results,indent=2))
