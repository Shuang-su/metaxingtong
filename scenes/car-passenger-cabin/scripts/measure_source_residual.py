"""One manually identified visible landmark only; not camera calibration or global fit."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_passenger_cabin_material.blend'))
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
rows=[]
for id,cam,frame,xy in [('S01','SRC_S01_closed',1,(216,751)),('S02','SRC_S02_open',2,(245,806)),('S03','SRC_S03_closed',1,(365,688))]:
 s.frame_set(frame);co=world_to_camera_view(s,bpy.data.objects[cam],Vector((.80,.626,.77)))
 pred=[co.x*1920,(1-co.y)*1080];err=math.dist(pred,xy)
 rows.append({'source':id,'landmark':'D03 circular vent center, visible unique instance','manual_source_xy_pixels':xy,'source_pick_uncertainty_pixels':15,'projected_model_xy_pixels':pred,'euclidean_residual_pixels':err,'interpretation':'Manual source center and projected model center are approximate; residual > source-pick tolerance, alignment NOT passed'})
(R/'qa/source-landmark-residuals.json').write_text(json.dumps({'note':'Only one visible landmark in each view; NOT calibration, scale recovery, independent camera baseline, or overall fit score. S04 excluded as context.','rows':rows},indent=2)+'\n')
print(rows)
