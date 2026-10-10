import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
root=Path('/workspace/scratch/fa58bfcf0425/classroom_hd_alignment_20261010');p=root/'rejected_shift';p.mkdir(exist_ok=True);(p/'qa').mkdir(exist_ok=True);s=bpy.context.scene
s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100
shifts={'R2C1':-.3,'R3C2':-.2};moved=[];reg=[]
for prefix,dy in shifts.items():
 desk=bpy.data.objects[prefix+' rounded oak desktop'];X=[desk.matrix_world@Vector(v) for v in desk.bound_box]
 for c in [o for o in bpy.data.objects if o.type=='CAMERA' and (o.name.startswith('SOURCE_') or o.name=='HD_classroom_motion_4282')]:
  a=[world_to_camera_view(s,c,v) for v in X];b=[world_to_camera_view(s,c,v+Vector((0,dy,0))) for v in X];errors=[math.hypot((u.x-v.x)*1180,(u.y-v.y)*664) for u,v in zip(a,b)];reg.append({'desk_group':prefix,'camera':c.name,'corner_rms_shift_px':math.sqrt(sum(e*e for e in errors)/len(errors))})
 for o in bpy.data.objects:
  if o.name.startswith(prefix+' '):o.location.y+=dy;moved.append(o.name)
bpy.context.view_layer.update();s['candidate_status']='REJECTED diagnostic trial: count-only movements without proven source identities';bpy.ops.wm.save_as_mainfile(filepath=str(p/'REJECTED_only_count_trial.blend'),compress=True)
(p/'qa/change_manifest.json').write_text(json.dumps({'status':'REJECTED; never replaces main verification version','shared_group_y_shifts':shifts,'moved_objects':moved,'projection_regression_all_source_cameras':reg,'reject_reason':'Source identity unproved; C corners shift 41 and26 px to create left-edge fragments. Camera changes could redistribute error but cannot be justified by count alone.'},indent=2))
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.image_settings.file_format='PNG'
for cam in ['C','D']:
 s.camera=bpy.data.objects['SOURCE_'+cam];s.render.filepath=str(p/f'{cam}_normal_material.png');bpy.ops.render.render(write_still=True)
# Exact same primary-ray ID routine as baseline, on the shared candidate.
code=(root/'scripts/finalize_audit.py').read_text().split('# Desktop visibility:')[1].split('\n',1)[1]
exec(code)
# Restore unchanged source for higher-sample main review pictures; never copy rejected geometry into main.
bpy.ops.wm.open_mainfile(filepath=str(root/'Classroom_HD_Evidence_REVIEW.blend'));s=bpy.context.scene;s.cycles.samples=64;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3
for name,cam in [('classroom_4284_wide','SOURCE_C'),('classroom_5447_key','SOURCE_D')]:
 s.camera=bpy.data.objects[cam];s.render.filepath=str(root/'renders'/f'{name}_64samples.png');bpy.ops.render.render(write_still=True)
print('REJECTED TRIAL AND MAIN PREVIEWS COMPLETE')
