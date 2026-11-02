import bpy,json
from pathlib import Path
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/arcade_remake_R03_material.blend'));s=bpy.context.scene;out={}
for o in s.objects:
 if o.type=='MESH' and any(o.name.endswith(x)for x in ['_display','_screen_frame','_lower_face','_plinth','_pad_base','_pad_top','_coin_gold','_shelf']):
  vs=[list(o.matrix_world@v.co)for v in o.data.vertices];out[o.name]={'vertices_world':vs,'faces':[list(p.vertices)for p in o.data.polygons],'bounds':[[min(v[j]for v in vs)for j in range(3)],[max(v[j]for v in vs)for j in range(3)]]}
(D/'qa/camera_diagnostic_meshes.json').write_text(json.dumps(out))
(D/'qa/camera_diagnostic_initial_cameras.json').write_text(json.dumps({o.name:{'matrix':[list(v)for v in o.matrix_world],'lens':o.data.lens,'sensor_width':o.data.sensor_width}for o in s.objects if o.type=='CAMERA'},indent=2))
