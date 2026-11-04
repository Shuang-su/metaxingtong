import bpy,pathlib,json
from mathutils import Matrix,Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/R04_material.blend'))
# Two additional distinct cups supported by native 3050 and adjacent 3051; precise canonical position provisional.
for old,new,delta,mat in [(3,9,(-1.35,.15,0),'Petal_pale'),(4,10,(-.05,-2.25,0),'Petal_pink')]:
 for ob in list(bpy.context.scene.objects):
  if ob.name.startswith('FLOWER_%02d_'%old):
   copy=ob.copy();copy.data=ob.data.copy();copy.name=ob.name.replace('FLOWER_%02d_'%old,'FLOWER_%02d_'%new);bpy.context.collection.objects.link(copy);copy.location+=Vector(delta);copy['inference']='Distinct additional cup visible in 3050/3051; precise 3D placement, stem and shape inferred'
   if '_petal_' in copy.name:copy.data.materials.clear();copy.data.materials.append(bpy.data.materials[mat])
# Conditional camera fit, exact selected parameters retained; no scene/world transform per view.
f=json.loads((ROOT/'qa/R05-camera-training.json').read_text());t=f['trials'][f['chosen_trial']];R=Matrix(t['camera_to_world']);p=Vector(t['parameters'][:3]);o=bpy.data.objects['SOURCE_F_top'];o.matrix_world=R.to_4x4();o.matrix_world.translation=p;o.data.lens=50;o['conditional_training']='11 manually hypothesized giant flower centres; no holdout, source still failed'
s=bpy.context.scene;s.camera=o;s.cycles.use_denoising=False;s.cycles.samples=32
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R05_material.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R05_material.glb'),export_format='GLB',export_apply=True,export_cameras=True)
white=bpy.data.materials.get('WHITE_clay')
if white is None:white=bpy.data.materials.new('WHITE_clay');white.use_nodes=True;white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R05_white.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R05_white.glb'),export_format='GLB',export_apply=True,export_cameras=True)
print('R05_SAVED',len([o for o in s.objects if o.type=='MESH']))
