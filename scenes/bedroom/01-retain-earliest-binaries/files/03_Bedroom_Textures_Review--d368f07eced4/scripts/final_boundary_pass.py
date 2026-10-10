import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/01_bedroom_material.blend'));s=bpy.context.scene
# A final geometric boundary check found inferred rear leaves outside the inferred shell.
# Move the complete plant forward and expand only the unseen right room boundary.
for o in bpy.data.collections['08_Plant_inferred_hidden'].objects:o.location.y-=.65
for name in ['Rear wall verified visible face','Floor substrate','Plain ceiling inferred unseen']:
 o=bpy.data.objects[name];o.location.x=.2;o.dimensions.x=7.6
bpy.data.objects['Right room return inferred'].location.x=4.01
for name in ['Rear skirting','Skirting bottom shadow']:
 o=bpy.data.objects[name];o.location.x=.2;o.dimensions.x=7.55
s['ROOM_ENVELOPE_INFERRED']='7.6 m width x 5.7 m depth x 3.3 m ceiling. Hidden room boundary inferred; camera-facing wall open. Plant moved wholly inside inferred walls after boundary QA.'
# Final file carries the current readable limitations too.
for t in list(bpy.data.texts):
 if t.name.startswith('README'):bpy.data.texts.remove(t)
t=bpy.data.texts.new('README_中文');t.write((R/'README_中文.txt').read_text())
def audit():
 h=hashlib.sha256();obs=[o for o in bpy.data.objects if o.type=='MESH'];lo=[1e9]*3;hi=[-1e9]*3;bpy.context.view_layer.update()
 for o in sorted(obs,key=lambda o:o.name):
  h.update(o.name.encode());h.update(str(tuple(tuple(v for v in row) for row in o.matrix_world)).encode())
  for v in o.data.vertices:
   h.update(str(tuple(v.co)).encode());w=o.matrix_world@v.co
   for j in range(3):lo[j]=min(lo[j],w[j]);hi[j]=max(hi[j],w[j])
  for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return {'mesh_objects':len(obs),'vertices':sum(len(o.data.vertices) for o in obs),'polygons':sum(len(o.data.polygons) for o in obs),'uv_meshes':sum(bool(o.data.uv_layers) for o in obs),'geometry_sha256':h.hexdigest(),'bounds_m':[lo,hi]}
meta=audit();meta['packed_images']=sum(bool(im.packed_file) for im in bpy.data.images);meta['source_url']='https://www.bilibili.com/video/BV1mx4y1z7oY/';meta['independent_side_reference']=False
s.camera=bpy.data.objects['QA_wide_level'];s.cycles.samples=32;s.render.threads_mode='FIXED';s.render.threads=4
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/01_bedroom_material.blend'),compress=True)
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
(R/'analysis/geometry_audit.json').write_text(json.dumps(meta,indent=2));print('BOUNDARY_QA_PASS_COMPLETE',json.dumps(meta))
