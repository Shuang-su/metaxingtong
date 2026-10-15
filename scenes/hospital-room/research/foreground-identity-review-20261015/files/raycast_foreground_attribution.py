"""Read-only named mesh attribution at source-image coordinates.
This does not assert that the modeled object is the correct source object.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;scene=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();P=json.load(open(R/'source_review_query_points.json'))
rows=[]
for k,d in P.items():
 cam=bpy.data.objects[d['camera']];rot=cam.matrix_world.to_3x3().normalized();f=1920*cam.data.lens/cam.data.sensor_width;origin=cam.matrix_world.translation
 for xy,note in zip(d['points'],d['source_note']):
  local=Vector(((xy[0]+.5-960)/f,(540-xy[1]-.5)/f,-1));direction=(rot@local).normalized();ok,loc,norm,face,obj,mat=scene.ray_cast(dep,origin,direction);rows.append({'frame':k,'source_xy':xy,'source_observation':note,'source_identity_status':'requires source visual-review interpretation; these queries alone cannot confirm source identity','camera':cam.name,'current_model_first_hit':obj.name if ok else None,'hit_world':list(loc) if ok else None,'face':face if ok else None,'not_a_metric_residual':True})
report={'status':'MODEL_ATTRIBUTION_ONLY_NO_GEOMETRY_EDIT','input_model':bpy.data.filepath,'input_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'native_source_coordinate_system':[1920,1080],'new_viewports_not_raycast':'5476/5663/6063 have no validated camera and are viewport observations, no native pixel residual','rays':rows,'warning':'Do not transfer Bed mesh names into source annotations. Existing model labels are hypotheses; foreground source identities are separate.'};(R/'foreground_model_first_hits.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print([(x['frame'],x['source_xy'],x['current_model_first_hit']) for x in rows])
