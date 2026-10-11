import bpy,json,math
from mathutils import Vector,Quaternion
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/camera_calibration_b');obs=json.loads((r/'observations.json').read_text())['observations'];fit=json.loads((r/'fit_results.json').read_text());names={'F':'MATCH_F_Turning_Right','G':'MATCH_G_Sofa_And_Bed','H':'MATCH_H'};out={}
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
for tag in 'FGH':
 out[tag]={};cam=bpy.data.objects[names[tag]]
 for mode in ['original']+(['pose6','pose_focal7'] if tag in 'FG' else []):
  x=fit[tag]['original'] if mode=='original' else fit[tag]['candidates'][mode]['parameters'];v=Vector(x[:3]);m=Quaternion(v.normalized(),v.length).to_matrix().to_4x4();m.translation=Vector(x[3:6]);cam.matrix_world=m;cam.data.lens=math.exp(x[6]);cam.data.shift_x=-x[7]/1920;cam.data.shift_y=x[8]/1920;bpy.context.view_layer.update()
  data={}
  for a in obs[tag]:
   points=[a['xyz']] if a['kind']=='point' else a['xyz'];qs=[]
   for p in points:
    q=world_to_camera_view(s,cam,Vector(p));qs.append([q.x*1920,(1-q.y)*1080,q.z])
   data[a['id']]=qs
  furniture={}
  for n in ['Sofa • reclined back cushion 1','Sofa • reclined back cushion 2','Chair • narrow curved wraparound back','Bed • observed endboard, consistent width']:
   o=bpy.data.objects[n];ps=[]
   for vv in o.data.vertices:
    q=world_to_camera_view(s,cam,o.matrix_world@vv.co)
    if q.z>0:ps.append([q.x*1920,(1-q.y)*1080,q.z])
   if not ps: furniture[n]={"behind_camera":True};continue
   furniture[n]={'projected_bounds_unclipped':[min(a[0] for a in ps),min(a[1] for a in ps),max(a[0] for a in ps),max(a[1] for a in ps)],'depth_range':[min(a[2] for a in ps),max(a[2] for a in ps)]}
  out[tag][mode]={'anchors':data,'furniture':furniture}
(r/'blender_projection_verification.json').write_text(json.dumps(out,indent=2))
