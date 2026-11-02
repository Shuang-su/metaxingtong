import bpy,json
from mathutils import Matrix
from pathlib import Path
D=Path(__file__).resolve().parents[1];q=json.load(open(D/'qa/aug23-circle-work-camera.json'));R=Matrix(q['world_to_camera']);rot=R.transposed()@Matrix.Diagonal((1,-1,-1))
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/FR03_{typ}.blend'));s=bpy.context.scene;c=bpy.data.cameras.new('AUG23_CIRCLE_CONDITION_NOT_CALIBRATED');o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o);o.location=q['camera_center'];o.rotation_euler=rot.to_euler();c.lens=q['fixed_f_pixels']*36/3840;c.sensor_width=36;c.sensor_fit='HORIZONTAL';s.camera=o;s.render.threads=2;s.cycles.samples=8;s.view_settings.exposure=-1.3;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/FR03_source_{typ}.blend'));s.render.filepath=str(D/f'renders/FR03_aug23_circlecondition_{typ}_960.png');bpy.ops.render.render(write_still=True)
