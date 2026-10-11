import bpy,os,json,hashlib,math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Garden_Polished.blend');sc=bpy.context.scene
sc.render.resolution_percentage=100;sc.cycles.samples=32;sc.cycles.use_denoising=False
# Source-matched nighttime glass: dark mottled blue, with nearly black mullions.
for im in bpy.data.images:
 if im.source=='FILE' and 'cyan_glass_basecolor' in im.name:im.reload()
p=bpy.data.materials['cyan_glass'].node_tree.nodes['Principled BSDF'];p.inputs['Emission Strength'].default_value=.035
p=bpy.data.materials['dark_stem'].node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.012,.016,.023,1)
for o in sc.objects:
 if o.type=='LIGHT':o.data.energy*=.64
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.17
# Overlay-guided final fit: source path is broader and farther arch slightly wider.
for o in sc.objects:
 if o.type=='MESH' and (o.name.startswith('Purple_path_paving') or o.name.startswith('Low_flowerbed_stone_edge')):
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;p.x*=1.14;v.co=inv@p
for o in bpy.data.collections['05_Far_Floral_Arch'].objects:
 if o.type=='MESH':
  for v in o.data.vertices:v.co.x*=1.10
for o in sc.objects:
 if o.name.startswith('Front_flowerbed_stone_edge'):o.location.z-=.008;o.location.y+=.018
cam=bpy.data.objects['MATCH_A_00h25m11s'];cam.rotation_euler=(Vector((.57,4,-.16))-cam.location).to_track_quat('-Z','Y').to_euler()

for im in bpy.data.images:
 if im.source=='FILE':im.filepath='//../textures/'+os.path.basename(im.filepath);im.pack()
for o in sc.objects:
 if o.type=='MESH':
  o['evidence_scope']='visible entrance patch; dimensions and hidden surface closures approximate'
  o['reconstruction']='editable mesh; no source image planes; procedural materials'
sc['Scope']='Visible garden entrance patch only. No roof, reverse garden, interior, full castle, or hall connection inferred.'
sc['Scale']='Relative proportions camera fitted; world metre scale is arbitrary.'
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
sc.camera=bpy.data.objects['WIDE_Level_Entrance']
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Xingtong_Castle_Garden_Textured.blend',compress=True)
json.dump(stats(core()),open(ROOT+'/qa/blender_textured_geometry.json','w'),indent=2)
export(ROOT+'/models/Xingtong_Castle_Garden_Textured.glb',core())
for name,cam in [('Final_Textured_Match_A','MATCH_A_00h25m11s'),('Final_Textured_Match_B','MATCH_B_00h21m59s'),('Final_Textured_Wide','WIDE_Level_Entrance'),('Final_Textured_Oblique','WIDE_Oblique_Visible_Patch')]:render(name,cam)
w=bpy.data.materials.new('Neutral_white_clay');w.diffuse_color=(.67,.67,.67,1);w.use_nodes=True;p=w.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.67,.67,.67,1);p.inputs['Roughness'].default_value=.72
for o in core():
 o.data.materials.clear();o.data.materials.append(w)
 for p in o.data.polygons:p.material_index=0
for o in sc.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1);o.data.energy*=1.25
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.13,.13,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65
sc.camera=bpy.data.objects['WIDE_Level_Entrance'];bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Xingtong_Castle_Garden_White.blend',compress=True)
json.dump(stats(core()),open(ROOT+'/qa/blender_white_geometry.json','w'),indent=2)
export(ROOT+'/models/Xingtong_Castle_Garden_White.glb',core())
for name,cam in [('Final_White_Match_A','MATCH_A_00h25m11s'),('Final_White_Wide','WIDE_Level_Entrance'),('Final_White_Oblique','WIDE_Oblique_Visible_Patch')]:render(name,cam)
