import bpy,json
from pathlib import Path
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010');q=p/'six_bay_candidate';j=json.load(open(p/'qa/B_camera_identity_exploration.json'));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.cycles.samples=32
for n,k in [('B_free_lens','six_bay_B_window_only_free_lens'),('B_front16_link','front16_two_wall_fit')]:
 c=j[k];d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=c['location'];o.rotation_euler=c['rotation'];d.lens=c['lens_mm'];d.sensor_width=36;s.camera=o;s.render.filepath=str(q/'renders'/(n+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(q/'Classroom_SixBay_BIdentity_EXPLORATORY.blend'),compress=True)
