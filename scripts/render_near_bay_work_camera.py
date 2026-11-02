import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parents[1];q=json.load(open(D/'qa/near-bay-work-camera.json'));R=Matrix(q['rotation_world_to_opencv']);flip=Matrix(((1,0,0),(0,-1,0),(0,0,-1)));worldrot=R.transposed()@flip
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/NOV2_CP01_{typ}.blend'));s=bpy.context.scene;bpy.ops.object.camera_add();o=bpy.context.object;o.name='NOV2_NEAR_BAY_CONDITIONAL_NOT_CALIBRATED';o.location=q['camera_location'];o.rotation_euler=worldrot.to_euler();o.data.type='PERSP';o.data.sensor_width=36;o.data.sensor_fit='HORIZONTAL';o.data.lens=q['f_pixels_work_assumption']*36/3840;s.camera=o;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.threads=2;s.cycles.samples=16
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/NOV2_CP02_workcamera_{typ}.blend'));s.render.filepath=str(D/f'renders/NOV2_CP02_near_bay_{typ}.png');bpy.ops.render.render(write_still=True)
