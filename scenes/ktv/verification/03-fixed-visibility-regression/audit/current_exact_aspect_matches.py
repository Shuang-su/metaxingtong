import bpy
R='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery'
for variant in ['','_White']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/KTV_Complete_Open_Stage'+variant+'.blend');sc=bpy.context.scene
 sc.render.resolution_x=891;sc.render.resolution_y=501;sc.render.resolution_percentage=100
 for n in ['MATCH_A_01h15m29s','MATCH_B_00h35m17s','MATCH_D_01h58m39s_empty']:
  sc.camera=bpy.data.objects[n];sc.render.filepath=R+'/renders/'+n+('_white' if variant else '')+'.png';bpy.ops.render.render(write_still=True)
