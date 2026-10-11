import bpy,os,json,hashlib,math,ast
from mathutils import Vector,Matrix
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/Classroom_Refined.blend'));sc=bpy.context.scene

COL={c.name:c for c in bpy.data.collections};cur='06_Window_Wall'
tree=ast.parse((R/'scripts/build_classroom.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
M={'black':bpy.data.materials['Charcoal painted metal'],'glass':bpy.data.materials['Clean window glass'],'metal':bpy.data.materials['Warm grey tubular steel'],'mint':bpy.data.materials['Pale jade notebook'],'blue':bpy.data.materials['Desk cup blue ceramic'],'darkwood':bpy.data.materials['Dark edge stained wood']}
# An inward-opening first-bay casement is directly visible in 00:11:08 and 01:30:47.
for k in [0,1]:
 o=bpy.data.objects.get('Window glass 0_1_%d'%k)
 if o:bpy.data.objects.remove(o,do_unlink=True)
before=set(bpy.data.objects);hinge=Vector((3.97,1.00,0));ang=math.radians(24)
for yy in [0,.735]:box('Observed inward-open casement vertical',(0,yy,1.70),(.045,.035,1.58),M['black'])
for zz in [.91,1.44,2.49]:box('Observed inward-open casement horizontal',(0,.3675,zz),(.045,.77,.035),M['black'])
for zz,hh in [(1.175,.495),(1.965,1.015)]:box('Observed open casement clear glass',(0,.3675,zz),(.008,.70,hh),M['glass'],0)
rod('Open casement handle',(-.033,.66,1.70),(-.033,.66,1.84),.010,M['metal'])
for o in set(bpy.data.objects)-before:
 o.location=hinge+Matrix.Rotation(ang,3,'Z')@o.location;o.rotation_euler.z+=ang
# Window glass remains PBR, with light opacity matching the source and transmitting sunlight.
gp=M['glass'].node_tree.nodes.get('Principled BSDF');gp.inputs['Alpha'].default_value=.16;gp.inputs['Transmission Weight'].default_value=.70;M['glass'].diffuse_color=(.81,.91,.94,.16);M['glass'].surface_render_method='DITHERED'
# Bright globe silhouette; specific continent shapes remain unresolved and are not fabricated.
globe=mat('Approximate icy blue globe ornament',(.17,.60,.76),.16);p=globe.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.30;p.inputs['Emission Color'].default_value=(.08,.38,.52,1);p.inputs['Emission Strength'].default_value=.50
for o in bpy.data.objects:
 if 'desk ornament' in o.name.lower():o.data.materials.clear();o.data.materials.append(globe)
cur='08_Small_Observed_Props'
# Repeated observed desktop accessories, with repeat count following the inferred desk array.
for o in list(COL['05_Student_Desks_Chairs'].objects):
 if not 'rounded oak desktop' in o.name or o.name.startswith('Observed_front'):continue
 x,y,z=o.location;label=o.name.split(' ')[0]
 if not bpy.data.objects.get(label+' pale jade closed workbook'):box(label+' pale jade closed workbook',(x-.10,y-.015,z+.028),(.24,.17,.012),M['mint'],.002)
 box(label+' observed brown pencil case',(x-.035,y+.138,z+.059),(.23,.075,.075),M['darkwood'],.012)
 cyl(label+' repeated blue enamel cup',(x+.228,y-.012,z+.085),.036,.13,M['blue'],vertices=24)
 cyl(label+' repeated cup dark open rim',(x+.228,y-.012,z+.153),.031,.003,M['black'],vertices=24)
 # Handle is small but genuine geometry, kept separate for editing.
 tube(label+' cup curved handle',[(x+.263+math.cos(a)*.021,y-.012,z+.086+math.sin(a)*.034) for a in [i*2*math.pi/16 for i in range(17)]],.0055,M['blue'])
ca=bpy.data.objects['MATCH_B_Windows_00h35m23s'];ca.location=(-.10,3.70,1.20);ca.rotation_euler=(Vector((4,5.35,1.65))-ca.location).to_track_quat('-Z','Y').to_euler();ca.data.lens=28
bpy.context.view_layer.update()
# Keep high-quality base color but compact tiny roughness/normal maps for a portable archive.
for im in bpy.data.images:
 if im.source=='FILE' and ('_Normal' in im.name or '_Roughness' in im.name) and im.size[0]>256:
  target=512 if im.size[0]>512 else 256;im.scale(target,target);im.filepath_raw=str(R/'textures'/os.path.basename(im.filepath));im.file_format='PNG';im.save();im.pack()

sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.cycles.samples=72;sc.render.threads=5
sc.view_settings.exposure=.0
for im in bpy.data.images:
 if im.source=='FILE':im.filepath='//../textures/'+os.path.basename(im.filepath);im.pack()
for o in sc.objects:
 if o.type=='MESH':
  o['reconstruction']='Editable original reconstruction; no whole screenshot billboard; performers omitted'
  o['evidence_scope']='Approximate generic exterior' if 'INFERRED' in o.name else ('Inferred rear continuation' if any(c.name=='90_INFERRED_Rear_Enclosure' for c in o.users_collection) else 'Reference-visible object type; dimensions, hidden construction and repeated counts are estimates')
sc['source_url']='https://www.bilibili.com/video/BV1LC411V7Nh/'
sc['reference_frames']='00:15:19; 00:20:24; 00:26:16; 00:35:23; 01:00:58; 01:05:12; 01:11:24'
sc['uncertainty']='Overall depth and unseen back wall, 16 repeated student desks plus one visible side set, three left window bays and right pane continuation, physical dimensions, clock hands and outdoor buildings/trees are inferred. Black board and notice text not transcribed. Approximate partially occluded ornament and chalk motif.'
def meshes():return sorted([o for o in sc.objects if o.type=='MESH'],key=lambda o:o.name)
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
def export(path):
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes():o.select_set(True)
 bpy.context.view_layer.objects.active=meshes()[0]
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True,export_image_format='AUTO')
 bpy.ops.object.select_all(action='DESELECT')
def render(name,ca):
 sc.camera=bpy.data.objects[ca];sc.render.filepath=str(R/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['PANORAMA_Level_Front'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Classroom_Textured.blend'),compress=True)
json.dump(stats(meshes()),open(R/'qa/blender_textured_geometry.json','w'),indent=2)
export(R/'models/Xingtong_Classroom_Textured.glb')
views=[('Level_Front','PANORAMA_Level_Front'),('Level_Windows','PANORAMA_Level_Windows'),('Match_A','MATCH_A_Front_00h15m19s'),('Match_B','MATCH_B_Windows_00h35m23s'),('Match_C_Wide','MATCH_C_Wide_01h11m24s')]
for n,ca in views:render('Final_Textured_'+n,ca)
render('Final_Textured_Desk_Detail','DETAIL_Desks_Podium')
w=bpy.data.materials.new('Neutral white clay');w.diffuse_color=(.59,.59,.59,1);w.use_nodes=True;p=w.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.59,.59,.59,1);p.inputs['Roughness'].default_value=.78
for o in meshes():
 o.data.materials.clear();o.data.materials.append(w)
 for poly in o.data.polygons:poly.material_index=0
for o in sc.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1)
sc.view_settings.exposure=-.8;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.35,.35,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
sc.camera=bpy.data.objects['PANORAMA_Level_Front'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Classroom_White.blend'),compress=True)
json.dump(stats(meshes()),open(R/'qa/blender_white_geometry.json','w'),indent=2);export(R/'models/Xingtong_Classroom_White.glb')
for n,ca in views:render('Final_White_'+n,ca)
print('FINAL_MODELS_AND_RENDERS_COMPLETE',flush=True)
