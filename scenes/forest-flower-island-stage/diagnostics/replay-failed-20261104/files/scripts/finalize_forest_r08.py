import bpy,pathlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/R07_material.blend'))
for n,p in [('CHECK_02',(5,5,9)),('CHECK_03',(-4,5,8)),('CHECK_05',(-5,-5,8))]:
 o=bpy.data.objects[n];o.location=p;o.rotation_euler=(Vector((0,0,4.3))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=24
s=bpy.context.scene
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R08_material.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R08_material.glb'),export_format='GLB',export_apply=True,export_cameras=True)
w=bpy.data.materials.get('WHITE_clay')
if w is None:w=bpy.data.materials.new('WHITE_clay');w.use_nodes=True;w.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(w)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R08_white.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R08_white.glb'),export_format='GLB',export_apply=True,export_cameras=True)
