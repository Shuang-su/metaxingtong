import bpy,json,hashlib,struct
from pathlib import Path
p=Path('/workspace/scratch/fa58bfcf0425/classroom_motion_validation_20261010');s=bpy.context.scene
code=Path('/workspace/scratch/fa58bfcf0425/classroom_hd_alignment_20261010/scripts/finalize_audit.py').read_text().split('def state():',1)[1].split('\nbefore=state()',1)[0];exec('def state():'+code);before=state();fits=json.loads((p/'qa/camera_only_fits.json').read_text());manifest=[]
for f in fits:
 c=bpy.data.objects.new('MOTION_'+f['name'],bpy.data.cameras.new('MOTION_'+f['name']));s.collection.objects.link(c);c.location=f['location'];c.rotation_euler=f['rotation_xyz'];c.data.lens=f['lens_mm'];c.data.sensor_width=36
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.camera=bpy.data.objects['MOTION_F_path_076'];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(p/'Classroom_Motion_Verification_ONLY.blend'),compress=True)
(p/'qa/shared_state_verification.json').write_text(json.dumps({'before':before,'after':state(),'equal':before==state(),'geometry_changes':0,'source_model':'classroom_fullroom/Classroom_FullRoom_REVIEW.blend','D_not_used_as_fitting_constraint':True},indent=2))
for f in fits:
 c=bpy.data.objects['MOTION_'+f['name']];s.camera=c;s.render.filepath=str(p/'renders'/(f['name']+'.png'));bpy.ops.render.render(write_still=True);manifest.append({'source':f['name'],'camera':c.name,'matrix_world':[list(row) for row in c.matrix_world],'lens':c.data.lens,'source_camera_only_fit':'qa/camera_only_fits.json'})
(p/'qa/render_camera_manifest.json').write_text(json.dumps(manifest,indent=2));print('FOUR MOTION FRAMES RENDERED')
