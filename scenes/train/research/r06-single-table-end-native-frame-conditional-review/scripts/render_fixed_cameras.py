"""Render inherited cameras with shared geometry, lighting and materials unchanged.
Usage: blender -b INPUT.blend -P render_fixed_cameras.py -- OUTPUT_DIR [inspect]
Source-camera outputs are conditional because new native frames are not recalibrated.
"""
import bpy,sys,json,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]);out.mkdir(parents=True,exist_ok=True);inspect='inspect' in args[1:];s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8 if inspect else 24;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2 if inspect else 4;s.render.resolution_x=960 if inspect else 1920;s.render.resolution_y=540 if inspect else 1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
names=[next(o.name for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith(f'INSPECT_{i:02d}_')) for i in range(1,9)] if inspect else ['R05_HD_A','R05_HD_B','R05_HD_D','R05_J_LOCAL_UNRESOLVED_BAY']
for name in names:
 s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 (out/(name+'.json')).write_text(json.dumps({'camera':name,'matrix':[list(x) for x in s.camera.matrix_world],'lens':s.camera.data.lens,'visibility_changes':False,'geometry_changes':False,'material_changes':False,'light_changes':False,'sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()},indent=2))
