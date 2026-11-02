import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
root=Path('/workspace/scratch/fa58bfcf0425');out=Path(__file__).resolve().parent;model=root/'camp-remake-20261102/models/C02_repaired_materials.blend';before=hashlib.sha256(model.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.pixel_aspect_x=s.render.pixel_aspect_y=1
P=json.load(open(root/'camp-remake-20261102/qa/C02_actual_points.json'));j=json.load(open(out/'cameras_for_render.json'));obs={'F1':[186,700],'F2':[283,697],'apex':[143,193]};checks=[]
def original_cams():return {n:{'matrix':[list(row) for row in bpy.data.objects[n].matrix_world],'lens':bpy.data.objects[n].data.lens} for n in ['SOURCE_CONDITIONAL_1','SOURCE_CONDITIONAL_2']}
original=original_cams()
for row in j['cameras']:
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.name=f'READONLY_DIAGNOSTIC_{row["focal_px"]}';cam.matrix_world=Matrix(row['matrix_world']);cam.data.lens=row['lens_mm'];cam.data.sensor_width=row['sensor_width_mm'];cam.data.sensor_fit=row['sensor_fit'];bpy.context.view_layer.update();errs=[]
 for n in ['F1','F2','apex']:
  v=world_to_camera_view(s,cam,Vector(P[n]));xy=[v.x*1920,(1-v.y)*1080];errs.append({'point':n,'Blender_projected':xy,'difference_from_three_fit_pixels':math.dist(xy,obs[n])})
 checks.append({'focal_px':row['focal_px'],'checks':errs,'max_blender_pixel_difference':max(e['difference_from_three_fit_pixels'] for e in errs)})
res={'new_computation_not_old_recovery':True,'C02_file_sha256':before,'file_unchanged':before==hashlib.sha256(model.read_bytes()).hexdigest(),'source1_2_camera_parameters_unchanged_in_runtime':original==original_cams(),'matrix_checks':checks,'scope':'one-thread read-only Blender load, temporary unsaved camera objects for numerical projection; no renders or production saves'};(out/'blender_matrix_verification.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
