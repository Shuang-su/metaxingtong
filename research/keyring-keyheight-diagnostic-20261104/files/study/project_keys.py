import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).parent;R=Path('/workspace/scratch/fa58bfcf0425/keyring-hall-candidate-20261104/versions/R06/models/keyring-material.blend');bpy.ops.wm.open_mainfile(filepath=str(R));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();out={}
for source in [17,20,21]:
 cam=s.objects[f'source{source}-conditional'];rows=[]
 for o in s.objects:
  if not o.name.startswith(('white-key-','black-key-')):continue
  vs=[o.matrix_world@v.co for v in o.data.vertices];p=[world_to_camera_view(s,cam,v) for v in vs];pix=[(q.x*1192,(1-q.y)*671,q.z) for q in p];xs=[x[0] for x in pix];ys=[x[1] for x in pix]
  # Projected geometry box, explicitly not source identity or visible mask.
  rows.append({'name':o.name,'bbox_xyxy':[min(xs),min(ys),max(xs),max(ys)],'all_positive_depth':all(q[2]>0 for q in pix),'center_x':sum(xs)/len(xs)})
 out[str(source)]=rows
(O/'fixed-camera-key-projections.json').write_text(json.dumps(out,indent=2))
