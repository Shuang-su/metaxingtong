import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/roof-r03.blend'));s=bpy.context.scene;c=s.camera;o=bpy.data.objects['STAGE_INNER annulus']
manual={'source':'11.webp 1192x671 non-native time unknown','points':{'inner_left_extreme':{'xy':[282,406],'uncertainty_px':[12,15]},'inner_right_extreme':{'xy':[905,408],'uncertainty_px':[12,15]},'inner_front_lower':{'xy':[596,488],'uncertainty_px':[12,10]},'inner_back_center':{'xy':None,'reason':'DJ and audience occlusion; do not fabricate correspondence'},'outer_front_led_center':{'xy':None,'reason':'bottom boundary clips center; not a measured complete circle'},'outer_front_led_left_visible':{'xy':[90,588],'uncertainty_px':[12,15],'use_fit':False,'reason':'visible local strip, angular correspondence unknown'}}}
(P/'qa/source11-manual-points.json').write_text(json.dumps(manual,indent=2))
rows=[]
for z in [8,9,10,11,12,13,14,15]:
 c.location.z=z;c.rotation_euler=(Vector((0,2.4,3.8))-c.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 pts=[world_to_camera_view(s,c,o.matrix_world@v.co) for v in o.data.vertices];pts=[(p.x*1192,(1-p.y)*671) for p in pts]
 ex={'inner_left_extreme':min(pts,key=lambda p:p[0]),'inner_right_extreme':max(pts,key=lambda p:p[0]),'inner_front_lower':max(pts,key=lambda p:p[1])}
 res={k:[ex[k][i]-manual['points'][k]['xy'][i] for i in [0,1]] for k in ex};rms=(sum(v*v for r in res.values() for v in r)/6)**.5
 rows.append({'camera_z':z,'projected_extrema':ex,'residual_xy':res,'rms_px':rms})
(P/'qa/camera-height-only-test.json').write_text(json.dumps({'scope':'one parameter only camera z, same target/lens/geometry; numerical projection, no render or accepted change','rows':rows,'decision':'Not applied: all tested settings leave large residuals and source10 common geometry correspondence remains uncalibrated. No joint camera/geometry multi-parameter fit asserted.'},indent=2))
