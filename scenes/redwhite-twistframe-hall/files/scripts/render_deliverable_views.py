import bpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
mode=sys.argv[sys.argv.index('--')+1];out=ROOT/'renders'/'R06';out.mkdir(exist_ok=True)
scene.render.threads_mode='FIXED';scene.render.threads=4;scene.cycles.use_denoising=False
scene.view_layers['MATERIAL'].use=True;scene.view_layers['WHITE'].use=False
if mode=='main':
 scene.camera=bpy.data.objects['SRC_a16_f027'];scene.render.resolution_x=960;scene.render.resolution_y=528;scene.cycles.samples=96
 scene.render.filepath=str(out/'MAIN_material_960x528.png');bpy.ops.render.render(write_still=True)
elif mode=='checks':
 # Explicit model-only white diagnostic with fixed neutral fill, not source-appearance evidence.
 scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.8,.8,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 for o in bpy.data.objects:
  if o.type=='LIGHT':o.data.color=(1,1,1)
 scene.render.resolution_x=640;scene.render.resolution_y=352;scene.cycles.samples=32
 for c in sorted([o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('CHECK')],key=lambda o:o.name):
  scene.camera=c;scene.render.filepath=str(out/(c.name+'_white_diagnostic_640x352.png'));bpy.ops.render.render(write_still=True)
