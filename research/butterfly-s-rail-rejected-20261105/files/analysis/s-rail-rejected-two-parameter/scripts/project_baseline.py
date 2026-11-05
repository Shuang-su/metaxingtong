import bpy,pathlib,json,hashlib
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');Q=pathlib.Path(__file__).resolve().parents[1]
f=P/'models/R04D_material.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene
out={'input':str(f),'input_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'unchanged_frozen_baseline':True,'objects':{}}
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('CENTRAL_'):
  centers=[sum((o.matrix_world@o.data.vertices[i].co for i in range(a,min(a+10,len(o.data.vertices)))),Vector())/10 for a in range(0,len(o.data.vertices),10)]
  rec={'world_centers':[list(x) for x in centers],'projections':{}}
  for camname in ['SOURCE02_conditional_front','SOURCE05_conditional_close','SOURCE05_alternate_tilt_diagnostic']:
   cam=bpy.data.objects[camname];points=[world_to_camera_view(s,cam,c) for c in centers]
   rec['projections'][camname]={'centers_pixel':[[p.x*1192,(1-p.y)*671] for p in points],'camera_matrix':[list(r) for r in cam.matrix_world],'lens':cam.data.lens}
  out['objects'][o.name]=rec
(Q/'baseline/central-projected-baseline.json').write_text(json.dumps(out,indent=2))
print('BASELINE_PROJECTED',len(out['objects']))
