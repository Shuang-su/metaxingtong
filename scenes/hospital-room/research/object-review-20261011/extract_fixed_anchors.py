import bpy,json
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit');s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
cams={'F':bpy.data.objects['MATCH_F_Turning_Right'],'G':bpy.data.objects['MATCH_G_Sofa_And_Bed'],'H':bpy.data.objects['MATCH_H']};out=[]
for o in s.objects:
 if not(o.name.startswith('Window • calibrated vertical mullion') or o.name=='TV • rectangular black frame' or o.name.startswith('Curtain rail • forward overhead beam') or o.name=='Bed • observed endboard, consistent width'):continue
 corners=[o.matrix_world@Vector(c) for c in o.bound_box];pts={'bbox_'+str(i):p for i,p in enumerate(corners)};pts['origin']=o.matrix_world.translation
 rec={'object':o.name,'world_dimensions':list(o.dimensions),'points':[]}
 for label,p in pts.items():
  pr={}
  for key,cam in cams.items():
   v=world_to_camera_view(s,cam,p);pr[key]={'pixel_xy':[round(v.x*1920,2),round((1-v.y)*1080,2)],'camera_depth':round(v.z,5),'inside_image':v.z>0 and 0<=v.x<=1 and 0<=v.y<=1}
  rec['points'].append({'label':label,'world_xyz':list(p),'projections':pr})
 out.append(rec)
(r/'fixed_anchor_model_projection.json').write_text(json.dumps({'baseline_model':'hospital_complete_materials.blend','projection_resolution':[1920,1080],'status':'Existing-model projections only, NOT observed source labels or solved calibration','objects':out},indent=2))
