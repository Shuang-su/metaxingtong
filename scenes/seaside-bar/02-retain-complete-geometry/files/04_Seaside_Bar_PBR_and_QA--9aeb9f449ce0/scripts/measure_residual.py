import bpy,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom';bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_textured.blend');S=bpy.context.scene;S.render.resolution_x=1180;S.render.resolution_y=663;S.render.resolution_percentage=100
# Hand-marked structural anchors on exact unchanged source, not on props changed across the cut.
pairs={'B':[('窗框外上角左',(-2.82,.775,4.58),(212,34)),('窗框外上角右',(3.81,.775,4.58),(1105,34)),('窗台上沿左',(-2.64,.80,1.705),(240,419)),('窗台上沿右',(3.63,.80,1.705),(1069,419))], 'A':[('左竖框_仅水平坐标',(-2.64,.91,2.80),(112,264)),('右竖框_仅水平坐标',(3.63,.91,2.80),(1133,264)),('窗台上沿中点',(.495,.80,1.705),(622,437))]}
out={'method':'人工读取的少量结构锚点；A竖框只计算水平距离，A窗台及B四角计算二维距离。相机经人工构图调整，非独立标定精度；未计算道具/背景误差。','image_size':[1180,663]}
for f,pts in pairs.items():
 cam=bpy.data.objects['源图_'+f+'_透视近似'];rows=[]
 for n,w,s in pts:
  p=world_to_camera_view(S,cam,Vector(w));xy=(p.x*1180,(1-p.y)*663);rows.append({'name':n,'source_pixel':s,'model_pixel':xy,'residual_px':abs(s[0]-xy[0]) if '仅水平' in n else math.dist(s,xy),'axis':'x_only' if '仅水平' in n else 'xy'})
 out[f]={'anchors':rows,'rms_px':math.sqrt(sum(r['residual_px']**2 for r in rows)/len(rows))}
json.dump(out,open(R+'/qa/source_structural_residuals.json','w'),ensure_ascii=False,indent=2)
