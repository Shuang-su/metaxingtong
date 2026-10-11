import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'bedroom_blockout.blend'));s=bpy.context.scene
# Globally reduce low headboard height after a broad proportion review, not per camera.
for o in bpy.data.objects:
 if o.name.startswith('Headboard tall'):
  o.location.z=.457;o.scale.z=.826/.90
 if o.name.startswith('Wall comic poster'):
  if o.type=='MESH' and o.name.endswith('UV print'):
   for v in o.data.vertices:v.co.z-=.189
  else:o.location.z-=.189
# Globally tune nightstand proportions and its entire accessory group.
for o in bpy.data.collections['06_Bedside_cabinet'].objects:
 o.location.x=1.49+(o.location.x-1.49)*1.055-.085;o.scale.x*=1.055
for o in bpy.data.collections['07_Lamp_clock_frames'].objects:
 if o.name.startswith('Wall comic poster'):continue
 if o.name=='Small bedside framed portrait UV print':
  for v in o.data.vertices:v.co.x-=.06
 elif o.name.startswith(('Small bedside framed portrait','Portrait easel')):o.location.x-=.06
 elif o.name.startswith(('Mushroom','Orange mushroom','Lamp ')):
  if o.name=='Orange mushroom lamp domed shade':
   for v in o.data.vertices:v.co.x-=.055;v.co.z=.7+(v.co.z-.7)*.89
  else:o.location.x-=.055;o.location.z=.7+(o.location.z-.7)*.89;o.scale.z*=.89
 else:o.location.x-=.075
# Smoother broad folds, maintaining the same bed footprint and using no camera-dependent geometry.
for name in ['Checker duvet with irregular soft drape','Ivory sheet lower drape']:
 o=bpy.data.objects[name]
 for v in o.data.vertices:
  x,y,z=v.co
  if abs(x)<1.0:
   baseline=.516 if name.startswith('Checker') else .481
   v.co.z=baseline+(z-baseline)*.40
# Whole-room roof is inferred. No false connection to any other room.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-2.75,3.345));o=bpy.context.object;o.name='Plain ceiling inferred unseen';o.dimensions=(7.2,5.7,.09);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for c in list(o.users_collection):c.objects.unlink(o)
bpy.data.collections['01_Room_envelope_inferred'].objects.link(o);o.data.materials.append(bpy.data.materials['Wall']);uv=o.data.uv_layers.new(name='UVMap') if not o.data.uv_layers else o.data.uv_layers.active
for p in o.data.polygons:
 for li in p.loop_indices:
  v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.y)
# Camera-only calibrated full front. Close is same camera axis and a zoom/shift.
p=json.loads((R/'analysis/front_camera_fit.json').read_text())['parameters'];x,y,z,pitch,lens,_=p
c=bpy.data.objects['MATCH_front_50m07_same_axis'];c.location=(x,y,z);c.rotation_euler=Vector((0,math.cos(pitch),-math.sin(pitch))).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
cc=bpy.data.objects['MATCH_close_50m10_same_axis'];cc.location=c.location;cc.rotation_euler=c.rotation_euler;cc.data.lens=lens*1.971;cc.data.shift_x=.016;cc.data.shift_y=.0465
# A true level wide view, with verticals kept vertical; no model warp.
for n in ['QA_wide_level','QA_opposite_level']:
 cam=bpy.data.objects[n];cam.data.shift_y=-.045
s.render.resolution_percentage=100;s.cycles.samples=64;s.cycles.max_bounces=7;s.view_settings.exposure=-.9
s['BED_ASSUMPTIONS']='Bed outer 2.29 x 2.30 m, mattress 2.19 x 2.27 m, mattress top 0.50 m, headboard top 0.87 m. Dimensions inferred.'
s['CAMERA_EVIDENCE']='Front wide and front close are same viewing direction. Tight view implemented by 1.971x lens zoom and sensor shift; NOT independent side validation.'
s['ROOM_ENVELOPE_INFERRED']='7.2 m width x 5.7 m depth x 3.3 m ceiling. Side walls, ceiling, planter details and rear geometry inferred. Camera-facing wall intentionally open for inspectability.'
# Give packed images a portable relative source path too.
for im in bpy.data.images:
 if im.source=='FILE':im.filepath='//../textures/'+Path(im.filepath).name

def audit():
 h=hashlib.sha256();obs=[o for o in bpy.data.objects if o.type=='MESH'];lo=[1e9]*3;hi=[-1e9]*3
 bpy.context.view_layer.update()
 for o in sorted(obs,key=lambda o:o.name):
  h.update(o.name.encode());h.update(str(tuple(tuple(v for v in row) for row in o.matrix_world)).encode())
  for v in o.data.vertices:
   h.update(str(tuple(v.co)).encode());w=o.matrix_world@v.co
   for j in range(3):lo[j]=min(lo[j],w[j]);hi[j]=max(hi[j],w[j])
  for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return {'mesh_objects':len(obs),'vertices':sum(len(o.data.vertices) for o in obs),'polygons':sum(len(o.data.polygons) for o in obs),'uv_meshes':sum(bool(o.data.uv_layers) for o in obs),'geometry_sha256':h.hexdigest(),'bounds_m':[lo,hi]}
meta=audit();meta['packed_images']=sum(bool(im.packed_file) for im in bpy.data.images);meta['source_url']='https://www.bilibili.com/video/BV1mx4y1z7oY/';meta['independent_side_reference']=False
readme=(R/'README_中文.txt')
if readme.exists():t=bpy.data.texts.new('README_中文');t.write(readme.read_text())
s.camera=bpy.data.objects['QA_wide_level'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/01_bedroom_material.blend'),compress=True)
def export(path):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.objects:
  if o.type in ['MESH','CAMERA']:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
export(R/'models/03_bedroom_material.glb')
for cam,f in [('QA_wide_level','normal_material'),('MATCH_front_50m07_same_axis','front_material'),('MATCH_close_50m10_same_axis','close_material'),('QA_opposite_level','opposite_material')]:
 s.camera=bpy.data.objects[cam];s.render.filepath=str(R/'renders'/(f+'.png'));bpy.ops.render.render(write_still=True)
white=bpy.data.materials.new('Neutral white clay');white.use_nodes=True;b=white.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.65,.65,.65,1);b.inputs['Roughness'].default_value=.82
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
 if o.type=='LIGHT':o.data.color=(1,1,1)
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.5,.5,1);s.view_settings.exposure=-.5;s['VERSION']='Exact same geometry in white material; all artwork planes are white. No reference image textures.'
meta['white_geometry_sha256']=audit()['geometry_sha256'];meta['white_material_geometry_identical']=meta['geometry_sha256']==meta['white_geometry_sha256'];meta['white_material_geometry_audit']=audit()
for m in list(bpy.data.materials):
 if m.users==0:bpy.data.materials.remove(m)
for im in list(bpy.data.images):
 if im.users==0:bpy.data.images.remove(im)
s.camera=bpy.data.objects['QA_wide_level'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/02_bedroom_white.blend'),compress=True);export(R/'models/04_bedroom_white.glb')
for cam,f in [('QA_wide_level','normal_white'),('MATCH_front_50m07_same_axis','front_white')]:
 s.camera=bpy.data.objects[cam];s.render.filepath=str(R/'renders'/(f+'.png'));bpy.ops.render.render(write_still=True)
(R/'analysis/geometry_audit.json').write_text(json.dumps(meta,indent=2));print('BEDROOM_FINAL_EXPORTED',json.dumps(meta))
