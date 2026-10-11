import bpy,os,json,hashlib,math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Terrace_Polished.blend');sc=bpy.context.scene
sc.render.resolution_percentage=100;sc.cycles.samples=48
# Wide-view structural QA repairs: extend visible deck below shifted arch,
# and close the support/chain connections to the verified overhead beams.
for o in sc.objects:
 if o.type=='MESH' and o.name.startswith('Deck_board'):
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.x>4.80:p.x+=1.43
   v.co=inv@p
 if o.name=='Pergola_left_visible_support':o.dimensions.z+=.4;o.location.z+=.2
 if o.name.startswith('Suspension_chain'):
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   p.z=2.36+(p.z-2.36)*1.1
   v.co=o.matrix_world.inverted()@p
for im in bpy.data.images:
 if im.source=='FILE':im.filepath='//../textures/'+os.path.basename(im.filepath);im.pack()
sc['Scope']='Visible seasonal terrace autumn dressing only; no unseen home interior, opposite boundary or complete roof perimeter reconstructed.'
sc['Scale']='Relative proportion reconstruction. Absolute metric scale is assumed, not surveyed.'
sc['Reference']='https://www.bilibili.com/video/BV1g64y1P7VV/ 29:46, 31:57, 45:27'
def core():return sorted([o for o in sc.objects if o.type=='MESH'],key=lambda x:x.name)
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

def render(name,cam):
 sc.camera=bpy.data.objects[cam];sc.render.filepath=ROOT+'/renders/'+name+'.png'
 boost=1.5 if cam.startswith('WIDE') and 'Textured' in name else 1
 for o in sc.objects:
  if o.type=='LIGHT':o.data.energy*=boost
 bpy.ops.render.render(write_still=True)
 for o in sc.objects:
  if o.type=='LIGHT':o.data.energy/=boost
sc.camera=bpy.data.objects['WIDE_Level_Terrace']
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Xingtong_Seasonal_Terrace_Textured.blend',compress=True)
json.dump(stats(core()),open(ROOT+'/qa/blender_textured_geometry.json','w'),indent=2)
export(ROOT+'/models/Xingtong_Seasonal_Terrace_Textured.glb',core())
for name,cam in [('Final_Textured_Match_A','MATCH_A_29m46s'),('Final_Textured_Wide','WIDE_Level_Terrace'),('Final_Textured_Oblique','WIDE_Oblique_Geometry')]:render(name,cam)
w=bpy.data.materials.new('Neutral_white_clay');w.diffuse_color=(.67,.67,.67,1);w.use_nodes=True;p=w.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.67,.67,.67,1);p.inputs['Roughness'].default_value=.72
for o in core():
 o.data.materials.clear();o.data.materials.append(w)
 for p in o.data.polygons:p.material_index=0
for o in sc.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1);o.data.energy*=1.25
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.13,.13,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65
sc.camera=bpy.data.objects['WIDE_Level_Terrace'];bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Xingtong_Seasonal_Terrace_White.blend',compress=True)
json.dump(stats(core()),open(ROOT+'/qa/blender_white_geometry.json','w'),indent=2)
export(ROOT+'/models/Xingtong_Seasonal_Terrace_White.glb',core())
for name,cam in [('Final_White_Match_A','MATCH_A_29m46s'),('Final_White_Wide','WIDE_Level_Terrace'),('Final_White_Oblique','WIDE_Oblique_Geometry')]:render(name,cam)
