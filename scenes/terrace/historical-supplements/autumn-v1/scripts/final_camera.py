import bpy,os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Terrace_Polished.blend');s=bpy.context.scene
for o in s.objects:
 if o.type=='LIGHT':
  if o.data.type=='SUN':o.rotation_euler=(-.65,-.25,-.15);o.data.energy=3;o.data.angle=.04
  else:o.data.energy*=.6
s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
# Fit right architectural boundary to cropped source: feature wall wider and arch
# mostly outside front camera, while full geometry stays visible in wide cameras.
for o in bpy.data.collections['08_Arch_Threshold_Only'].objects:o.location.x+=.85
C=bpy.data.collections['06_Cedar_Feature_Wall']
for o in list(C.objects):
 if o.name=='Feature_wall_backing':o.dimensions.x+=.85;o.location.x+=.425
 if o.name=='Small_roof_overhang':o.dimensions.x+=.85;o.location.x+=.425
 if o.name.startswith('Pergola_white'):o.location.z+=.12
for i in range(8):
 src=bpy.data.objects['Vertical_cedar_wall_board'];o=src.copy();o.data=src.data.copy();C.objects.link(o);o.location.x=3.9+i*.104
# Same front composition but top pergola naturally crops in tighter source camera.
cam=bpy.data.objects['MATCH_A_29m46s'];cam.location=(.15,-10.1,2.47);cam.rotation_euler=(Vector((.15,.65,1.66))-cam.location).to_track_quat('-Z','Y').to_euler()
# A wider native overview retains the whole visible patch for geometry inspection.
cam=bpy.data.objects['WIDE_Level_Terrace'];cam.location=(.4,-13.5,4);cam.rotation_euler=(Vector((.55,.5,2))-cam.location).to_track_quat('-Z','Y').to_euler()
s.camera=bpy.data.objects['MATCH_A_29m46s'];bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Terrace_Polished.blend',compress=True)
s.render.resolution_percentage=65;s.cycles.samples=24;s.render.filepath=ROOT+'/renders/Iteration_04.png';bpy.ops.render.render(write_still=True)
