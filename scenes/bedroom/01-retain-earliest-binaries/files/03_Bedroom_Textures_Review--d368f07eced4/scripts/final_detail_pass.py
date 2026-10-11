import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/01_bedroom_material.blend'));s=bpy.context.scene
# Lower pillows as complete, physically sized objects. No camera-dependent deformation.
o=bpy.data.objects['Checker pillow 0'];o.location.z=.615;o.scale.z=.34/.42
o=bpy.data.objects['Checker pillow 1'];o.location.z=.572;o.scale.z=.20/.30
# Turn real leaf surfaces toward the room to show their observed broad silhouettes.
for q in range(12):
 o=bpy.data.objects['Curved broad plant leaf %02d'%q];ang=q*2.399;h=.81+q*.065;reach=.34+.17*math.sin(q*1.13)**2;base=Vector((2.92+math.cos(ang)*reach,-.31+math.sin(ang)*reach,h));axis=Vector((math.cos(ang),math.sin(ang),0));rot=Matrix.Rotation(math.radians(58),3,axis)
 for v in o.data.vertices:
  d=v.co-base;v.co=base+rot@Vector((d.x*1.17,d.y*1.17,d.z))
# Fill the parquet perimeter substrate with matching timber, avoiding false black holes.
o=bpy.data.objects['Floor substrate'];o.data.materials.clear();o.data.materials.append(bpy.data.materials['Oak'])
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
s.camera=bpy.data.objects['QA_wide_level'];s.cycles.samples=48;s.render.threads_mode='FIXED';s.render.threads=4
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
(R/'analysis/geometry_audit.json').write_text(json.dumps(meta,indent=2));print('FINAL_DETAIL_PASS_COMPLETE',json.dumps(meta))
