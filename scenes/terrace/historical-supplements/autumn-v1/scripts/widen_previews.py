import bpy,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for variant in ['Textured','White']:
 p=R+'/models/Xingtong_Seasonal_Terrace_'+variant+'.blend';bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene
 for name,lens in [('WIDE_Level_Terrace',30),('WIDE_Oblique_Geometry',30)]:bpy.data.objects[name].data.lens=lens
 s.camera=bpy.data.objects['WIDE_Level_Terrace'];bpy.ops.wm.save_as_mainfile(filepath=p,compress=True)
 for suffix,cam in [('Wide','WIDE_Level_Terrace'),('Oblique','WIDE_Oblique_Geometry')]:
  s.camera=bpy.data.objects[cam];s.render.filepath=R+'/renders/Final_'+variant+'_'+suffix+'.png';bpy.ops.render.render(write_still=True)
