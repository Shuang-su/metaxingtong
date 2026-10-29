import bpy,json,math,sys
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_camera_only_trial.blend'))
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.use_denoising=False
(R/'renders/camera_only_full').mkdir(parents=True,exist_ok=True)
geo=json.loads((R/'shared_geometry.json').read_text());rows=[]
for id in ['S01','S02','S03']:
 frame=2 if id=='S02' else 1;s.frame_set(frame);c=bpy.data.objects['SRC_'+id+('_open' if id=='S02' else '_closed')];s.camera=c;bpy.context.view_layer.update()
 checks=[]
 for name,expected in [('dash_top_corner','D01_dashboard_top'),('dash_bottom_corner','D01_dashboard_top'),('a_foot','A01_fixed_A_pillar')]:
  target=Vector(geo['states'][str(frame)][name]);direction=target-c.location;distance=direction.length;hit,loc,normal,face,o,mat=s.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,direction.normalized(),distance=distance+.001)
  actual=(loc-c.location).length if hit else None
  allowed=[expected,'D01_dashboard_top'] if name=='a_foot' else [expected]
  checks.append({'feature':name,'expected_objects':allowed,'first_hit_object':o.name if hit else None,'target_distance':distance,'first_hit_distance':actual,'surface_visible_within_0_005':bool(hit and o.name in allowed and abs(actual-distance)<.005),'interpretation':'A-foot is a nominal pillar/dashboard interface, so the dashboard surface at the same depth is valid. Other modeled proxy corners may be obscured; projection alone is insufficient.'})
 path=f'renders/camera_only_full/{id}_render_native.png';s.render.filepath=str(R/path)
 if '--visibility-only' not in sys.argv:bpy.ops.render.render(write_still=True)
 rows.append({'source':id,'frame':frame,'state':'open' if frame==2 else 'closed','camera':c.name,'dimensions':[1920,1080],'samples':32,'render':path,'visibility_checks':checks,'geometry_visibility':'Every baseline mesh retained; no per-camera hide flags or geometry changes'})
(R/'render_and_visibility.json').write_text(json.dumps(rows,indent=2)+'\n')
