import bpy,os
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for k in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/Xingtong_Castle_Garden_'+k+'.blend');s=bpy.context.scene;o=bpy.data.objects['WIDE_Oblique_Visible_Patch'];o.data.lens=29;o.rotation_euler=(Vector((0,-1,2.4))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=bpy.data.objects['WIDE_Level_Entrance'];bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Xingtong_Castle_Garden_'+k+'.blend',compress=True)
 s.camera=o
 for light in s.objects:
  if light.type=='LIGHT' and k=='Textured':light.data.energy*=1.5
 s.render.filepath=R+'/renders/Final_'+k+'_Oblique.png';bpy.ops.render.render(write_still=True)
