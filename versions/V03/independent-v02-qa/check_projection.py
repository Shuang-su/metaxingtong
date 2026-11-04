import bpy,json,pathlib,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/dreamfold-phone-study-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-dreamfold-phone-v02-qa-20261104');bpy.ops.wm.open_mainfile(filepath=str(P/'versions/V02/models/phone-material.blend'));s=bpy.context.scene;o=bpy.data.objects['P01_front_shell_thickness_INFERRED'];fit=json.load(open(P/'versions/V02/qa/camera-fit.json')) if (P/'versions/V02/qa/camera-fit.json').exists() else json.load(open(P/'qa/camera-fit.json'));out=[]
for j,v in enumerate([(-.5,.6,.025),(.5,.6,.025),(.5,-.6,.025),(-.5,-.6,.025)]):
 w=o.matrix_world@Vector(v);p=world_to_camera_view(s,s.camera,w);xy=[1080*p.x,603*(1-p.y)];out.append({'actual_projected':xy,'depth':p.z,'recorded_projected':fit['projected'][j],'record_error':math.dist(xy,fit['projected'][j]),'source_residual':math.dist(xy,fit['source_landmarks'][j])})
(Q/'projection.json').write_text(json.dumps({'corners':out,'coordinate_RMSE':fit['rms_pixels'],'euclidean_point_RMS':math.sqrt(sum(x['source_residual']**2for x in out)/4)},indent=2));print(out)
