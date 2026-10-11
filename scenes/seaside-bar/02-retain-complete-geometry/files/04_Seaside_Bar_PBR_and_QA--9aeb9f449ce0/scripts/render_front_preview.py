import bpy
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom';bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_textured.blend');S=bpy.context.scene;S.camera=bpy.data.objects['01_前方全貌'];S.cycles.samples=96;S.render.resolution_x=1000;S.render.resolution_y=750;S.render.filepath=R+'/renders/01_前方全貌_材质.png';bpy.ops.render.render(write_still=True)
