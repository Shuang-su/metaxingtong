import bpy,pathlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/R06_material.blend'))
for name,tex in [('Bark','bark_color'),('Leaf','leaf_color'),('Moss_and_earth','moss_color')]:
 m=bpy.data.materials[name]
 for node in m.node_tree.nodes:
  if node.type=='TEX_IMAGE':node.image=bpy.data.images.load(str(ROOT/'textures'/(tex+'-r07.png')),check_existing=True);node.image.pack();node.image.filepath='//../textures/'+tex+'-r07.png'
locations=[(12,-6,11),(9,9,14),(-5,11,13),(-12,3,10),(-10,-8,15),(0,-12,7),(0,-1,18),(6,-7,1.5)]
for i,p in enumerate(locations):
 o=bpy.data.objects['CHECK_%02d'%(i+1)];o.location=p;o.rotation_euler=(Vector((0,0,4))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=28;o['source_width']=1280;o['source_height']=720;o['role']='diagnostic check angle, not a source camera; no hidden objects or extra lights'
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=32;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R07_material.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R07_material.glb'),export_format='GLB',export_apply=True,export_cameras=True)
white=bpy.data.materials.get('WHITE_clay')
if white is None:white=bpy.data.materials.new('WHITE_clay');white.use_nodes=True;white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R07_white.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R07_white.glb'),export_format='GLB',export_apply=True,export_cameras=True)
print('R07_SAVED',len([o for o in s.objects if o.type=='MESH']))
