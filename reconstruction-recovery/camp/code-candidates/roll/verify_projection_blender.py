import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
out=Path(__file__).resolve().parent;r=Path('/workspace/shared/desert-camp-build-20261031/scenes/desert-tent-camp');bpy.ops.wm.open_mainfile(filepath=str(r/'models/R07_camp_materials.blend'));s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.pixel_aspect_x=s.render.pixel_aspect_y=1
P=json.load(open(r/'qa/heldout_r03/frozen_geometry_anchors.json'))['actual_model_points'];rows=[];compact=[]
for phase,file in [('three_points','audit_all_branches.json'),('three_points_plus_vertical','with_vertical_segment/audit_all_branches.json')]:
 j=json.load(open(out/file))
 for pr in j['profiles']:
  for k,b in enumerate(pr['branches']):
   if not (b['positive_depth'] and b['source_front_face_visible'] and b['source_left_face_visible']):continue
   bpy.ops.object.camera_add();cam=bpy.context.object;cam.name=f'DIAGNOSTIC_{phase}_{pr["focal_px"]}_{k}';M=Matrix(b['blender_camera_world_rotation_columns']).to_4x4();M.translation=Vector(b['camera_world_location']);cam.matrix_world=M;cam.data.lens=pr['focal_px']*36/1920;cam.data.sensor_width=36;cam.data.sensor_fit='HORIZONTAL';bpy.context.view_layer.update();R=Matrix(b['world_to_cv_rotation']);C=Vector(b['camera_world_location']);errs=[]
   for n in ['F1','F2','apex']:
    x=Vector(P[n]);q=R@(x-C);expected=[960+q.x/q.z*pr['focal_px'],540+q.y/q.z*pr['focal_px']];v=world_to_camera_view(s,cam,x);actual=[v.x*1920,(1-v.y)*1080];errs.append(math.dist(expected,actual))
   rows.append({'phase':phase,'focal':pr['focal_px'],'branch_index':k,'max_numpy_blender_pixel_difference':max(errs)})
   compact.append({'phase':phase,'focal_px':pr['focal_px'],'branch_index_in_full_log':k,'not_selected_by_heldout':True,'location':b['camera_world_location'],'matrix_world':[list(row) for row in M],'lens_mm_for_36mm_sensor':pr['focal_px']*36/1920,'sensor_fit':'HORIZONTAL','image_size':[1920,1080],'roll_degrees':b['roll_degrees'],'fit_point_residuals_px':b['fit_residual_px'],'heldout_checks':b['heldout_checks'],'vertical_training_check':b.get('vertical_segment_checks')})
(out/'blender_projection_verification.json').write_text(json.dumps(rows,indent=2));(out/'cameras_for_render.json').write_text(json.dumps({'purpose':'all found positive-depth front-left-view main branches, not chosen by heldout; both declared training protocols retained','cameras':compact},indent=2));print(rows)
