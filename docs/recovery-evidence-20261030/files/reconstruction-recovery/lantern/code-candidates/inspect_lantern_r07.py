import bpy,json
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
p=Path('/workspace/shared/lantern-petal-stage-build-20261031/scenes/lantern-petal-stage');bpy.ops.wm.open_mainfile(filepath=str(p/'models/R06b_column_trial_material.blend'));s=bpy.context.scene
out={}
for n in ['LANTERN_round_L0','LANTERN_round_R0','LANTERN_string0_10','LANTERN_string0_9']:
 o=bpy.data.objects[n];v=[o.matrix_world@x.co for x in o.data.vertices]; q=[world_to_camera_view(s,bpy.data.objects['SOURCE1'],x) for x in v];out[n]={'bounds':[[min(x[i] for x in v) for i in range(3)],[max(x[i] for x in v) for i in range(3)]],'pixels':[[min(x.x for x in q)*1920,(1-max(x.y for x in q))*1080],[max(x.x for x in q)*1920,(1-min(x.y for x in q))*1080]]}
print(json.dumps(out));(p/'qa/R07_lantern/before_bounds.json').write_text(json.dumps(out,indent=2))
