import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
r=Path(__file__).resolve().parents[1];p=r/'models/R07_camp_materials.blend';sha=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.use_denoising=False;s.cycles.samples=8;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50;s.render.use_border=False;s.render.use_crop_to_border=False
cams=json.load(open(r/'qa/roll_condition/cameras_for_render.json'))['cameras']
for c in cams:
 n=f"H02_{c['phase']}_f{c['focal_px']}";bpy.ops.object.camera_add();o=bpy.context.object;o.name=n;o.matrix_world=Matrix(c['matrix_world']);o.data.lens=c['lens_mm_for_36mm_sensor'];o.data.sensor_width=36;o.data.sensor_fit='HORIZONTAL';s.camera=o;s.render.filepath=str(r/f'qa/roll_condition/{n}_render960.png');bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/R07_roll_condition_diagnostic.blend'));(r/'qa/roll_condition/original_production_byte_check.json').write_text(json.dumps({'original_model_sha_before':sha,'original_model_sha_after':hashlib.sha256(p.read_bytes()).hexdigest(),'equal':sha==hashlib.sha256(p.read_bytes()).hexdigest(),'modified':'new cameras only in separate diagnostic BLEND','lighting_and_geometry':'R07 unchanged'},indent=2));print('ROLL_RENDER_DONE')
