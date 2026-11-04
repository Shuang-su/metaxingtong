import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();fixes=[]
for names in [['decor cluster 01 fragment 03','decor cluster 01 fragment 08'],['decor cluster 05 fragment 02','decor cluster 05 fragment 03']]:
 vs=[]
 for name in names:
  o=bpy.data.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh();vs += [ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 low=min(v.z for v in vs)
 for name in names:
  ob=bpy.data.objects[name];parent_inv=ob.parent.matrix_world.inverted().to_3x3() if ob.parent else None;delta=Vector((0,0,-low));ob.location += parent_inv@delta if parent_inv else delta
 fixes.append(dict(objects=names,world_z_translation=-low,inference='Ground abstract connected cluster; actual source fragment arrangement unknown.'))
bpy.context.view_layer.update();scene['version']='R07';scene['status']='CONDITIONAL / source FAILED; no acceptance'
(ROOT/'qa/R07_ground_contact_fixes.json').write_text(json.dumps(fixes,indent=2))
# Exact same source/check cameras and aspect. No per-camera appearance changes.
scene.render.resolution_x=320;scene.render.resolution_y=176;scene.camera=bpy.data.objects['SRC_a16_f027'];scene.cycles.use_denoising=False
scene.view_layers['MATERIAL'].use=True;scene.view_layers['WHITE'].use=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R07_twistframe_hall.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R07_twistframe_hall.glb'),export_format='GLB',export_apply=True,export_cameras=True,export_lights=True,export_extras=True)
def fp():
 dg=bpy.context.evaluated_depsgraph_get();geo=[];cam=[]
 for ob in sorted(bpy.data.objects,key=lambda o:o.name):
  if ob.type in {'MESH','CURVE'}:
   ev=ob.evaluated_get(dg);me=ev.to_mesh();geo.append((ob.name,[tuple(ev.matrix_world@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]));ev.to_mesh_clear()
  if ob.type=='CAMERA':cam.append((ob.name,[list(v) for v in ob.matrix_world],ob.data.type,ob.data.lens,ob.data.ortho_scale))
 return dict(geometry_sha256=hashlib.sha256(json.dumps(geo,separators=(',',':')).encode()).hexdigest(),cameras_sha256=hashlib.sha256(json.dumps(cam,separators=(',',':')).encode()).hexdigest(),geometric_objects=len(geo),cameras=len(cam))
a=fp();clay=bpy.data.materials['WHITE_CHECK neutral']
for ob in bpy.data.objects:
 if ob.type in {'MESH','CURVE'}:ob.data.materials.clear();ob.data.materials.append(clay)
b=fp();(ROOT/'qa/R07_material_white_identity.json').write_text(json.dumps(dict(material=a,white=b,identical=a==b),indent=2))
scene['white_original']='Separate editable white original; same geometry and cameras.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R07_twistframe_hall_white.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R07_twistframe_hall_white.glb'),export_format='GLB',export_apply=True,export_cameras=True,export_lights=True,export_extras=True)
