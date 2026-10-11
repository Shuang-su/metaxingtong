import bpy,os,json,hashlib,math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Xingtong_KTV_Textured.blend');sc=bpy.context.scene
sc.render.resolution_percentage=100;sc.cycles.samples=64;sc.render.threads=6
for im in bpy.data.images:
 if im.source=='FILE':im.filepath='//../textures/'+os.path.basename(im.filepath);im.pack()
# Semantic metadata survives glTF extras. Unknown geometry is clearly separated in names.
for o in sc.objects:
 if o.type=='MESH':
  o['reconstruction']='editable mesh; image references are never used as scene billboards'
  o['evidence_scope']='procedural remote approximation' if 'City_' in o.name or 'Distant_sky' in o.name else ('inferred off-camera extent' if 'INFERRED' in o.name else 'visible stage object or approximate hidden back face')
# Core exports deliberately omit only the optional moving red balloon dog.
def core():return sorted([o for o in sc.objects if o.type=='MESH' and not any(c.name=='09_Optional_Moving_Balloon_Dog' for c in o.users_collection)],key=lambda x:x.name)
def stats(objs):
 tri=[];mi=[1e20]*3;ma=[-1e20]*3;area=0
 for o in objs:
  me=o.data;me.calc_loop_triangles()
  for v in me.vertices:
   p=o.matrix_world@v.co
   for j in range(3):mi[j]=min(mi[j],p[j]);ma[j]=max(ma[j],p[j])
  for t in me.loop_triangles:
   pts=[o.matrix_world@me.vertices[i].co for i in t.vertices];tri.append(sorted(tuple(round(x,4) for x in p) for p in pts));area+=(pts[1]-pts[0]).cross(pts[2]-pts[0]).length/2
 return {'mesh_objects':len(objs),'triangles':len(tri),'bounds_min':mi,'bounds_max':ma,'world_surface_area_m2':area,'all_meshes_have_uv':all(bool(o.data.uv_layers) for o in objs),'world_triangle_coordinate_sha256':hashlib.sha256(repr(sorted(tri)).encode()).hexdigest(),'object_names':[o.name for o in objs]}
def select_only(objs):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0]
def export(path,objs):
 select_only(objs)
 bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True,export_image_format='AUTO')
 bpy.ops.object.select_all(action='DESELECT')
def render(name,cam,empty=False):
 bpy.data.collections['02_Inflated_Armchairs'].hide_render=empty;bpy.data.collections['08_Optional_Star_Companion'].hide_render=empty
 sc.camera=bpy.data.objects[cam];sc.render.filepath=ROOT+'/renders/'+name+'.png';bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['PANORAMA_Level_Full_Component_Set']
sc['stage_boundary_note']='The blue inner border follows visible evidence; outside support and hidden front/depth are inferred and not a complete room.'
bpy.data.collections['09_Optional_Moving_Balloon_Dog']['note']='Mobile/animated prop. Hidden by default; not a camera anchor.'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Xingtong_KTV_Textured.blend',compress=True)
json.dump(stats(core()),open(ROOT+'/qa/blender_textured_geometry.json','w'),indent=2)
export(ROOT+'/models/Xingtong_KTV_Textured.glb',core())
# Separate optional prop export preserves all its geometry without forcing it visible in the stage GLB.
dogcoll=bpy.data.collections['09_Optional_Moving_Balloon_Dog'];dogcoll.hide_viewport=False;dogcoll.hide_render=False
dog=[o for o in dogcoll.objects if o.type=='MESH'];export(ROOT+'/models/Optional_Moving_Balloon_Dog.glb',dog);dogcoll.hide_viewport=True;dogcoll.hide_render=True
for name,cam,empty in [('Final_Textured_Panorama','PANORAMA_Level_Full_Component_Set',False),('Final_Textured_Match_A','MATCH_A_01h15m29s',False),('Final_Textured_Match_B','MATCH_B_00h35m17s',False),('Final_Textured_Empty_Stage','MATCH_D_01h58m39s_empty',True),('Final_Textured_Telescope_Detail','DETAIL_Telescope_Lamp',True)]:render(name,cam,empty)
# Same meshes, transformations, collections, and cameras, neutral clay material only.
bpy.data.collections['02_Inflated_Armchairs'].hide_render=False;bpy.data.collections['08_Optional_Star_Companion'].hide_render=False
w=bpy.data.materials.new('Neutral_white_clay');w.diffuse_color=(.67,.67,.67,1);w.use_nodes=True;p=w.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.67,.67,.67,1);p.inputs['Roughness'].default_value=.72
for o in sc.objects:
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(w)
  for poly in o.data.polygons:poly.material_index=0
for o in sc.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1)
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.8
sc.camera=bpy.data.objects['PANORAMA_Level_Full_Component_Set']
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Xingtong_KTV_White.blend',compress=True)
json.dump(stats(core()),open(ROOT+'/qa/blender_white_geometry.json','w'),indent=2)
export(ROOT+'/models/Xingtong_KTV_White.glb',core())
for name,cam,empty in [('Final_White_Panorama','PANORAMA_Level_Full_Component_Set',False),('Final_White_Match_A','MATCH_A_01h15m29s',False),('Final_White_Match_B','MATCH_B_00h35m17s',False),('Final_White_Empty_Stage','MATCH_D_01h58m39s_empty',True)]:render(name,cam,empty)
print('FINAL_MODELS_AND_RENDERS_COMPLETE',flush=True)
