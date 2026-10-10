import bpy
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene'
for variant in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_'+variant+'.blend');s=bpy.context.scene;s.render.resolution_x=1180;s.render.resolution_y=663;s.render.resolution_percentage=100;s.cycles.samples=20;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2
 for k,n in [('A','Camera_A_reference_6170'),('B','Camera_B_reference_6435')]:
  s.camera=bpy.data.objects[n];s.render.filepath=R+'/renders/HD_'+variant+'_'+k+'.png';bpy.ops.render.render(write_still=True)
print('HD_RENDERS_COMPLETE')
