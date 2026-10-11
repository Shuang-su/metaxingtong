import bpy,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Terrace_Polished.blend');s=bpy.context.scene
for o in s.objects:
 if o.type=='LIGHT':
  if o.data.type=='SUN':o.rotation_euler=(-.65,-.25,-.15);o.data.energy=3;o.data.angle=.04
  else:o.data.energy*=.45
s.world.node_tree.nodes['Background'].inputs[1].default_value=.3;s.render.resolution_percentage=65;s.cycles.samples=24;s.render.filepath=ROOT+'/renders/Lighting_Test.png';bpy.ops.render.render(write_still=True)
