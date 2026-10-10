import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/01_bedroom_material.blend'));bpy.context.view_layer.update();obs=list(bpy.data.collections['08_Plant_inferred_hidden'].objects);coords=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
bounds=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)];inside=bounds[0][0]>-3.52 and bounds[0][1]<3.92 and bounds[1][0]>-5.6 and bounds[1][1]<.03 and bounds[2][1]<3.30
r={'plant_world_bounds_m':bounds,'interior_wall_limits_m':{'x':[-3.52,3.92],'y':[-5.6,.03],'ceiling_z':3.3},'plant_inside_inferred_room':inside,'adjustment':'Complete plant translated 0.65 m forward; right inferred wall moved outward 0.4 m, envelope width updated to 7.6 m. Bed, cabinet and cameras unchanged.'};(R/'analysis/boundary_check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r));assert inside
