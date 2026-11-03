import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path('/workspace/shared/metaxingtong-production-20261103');out=Path('/workspace/shared/novelty-review-20261103/qa')
p=D/'models/R07_material.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
rows=[]
for r in json.load(open(D/'qa/R05-camera-fit.json')):
 c=bpy.data.objects[r['camera']]
 ar=[]; invalid=[]
 for a in r['anchors']:
  if a['id']=='bar_left_upper_front':
   invalid.append({'id':a['id'],'status':'invalidated by R06 bar topology change (still invalid in R07); no replacement landmark or refit'});continue
  v=world_to_camera_view(s,c,Vector(a['world_hypothesis']));pix=[v.x*1920,(1-v.y)*1080];delta=[pix[i]-a['fitted_projection'][i] for i in range(2)]
  ar.append({'id':a['id'],'blender_projection_px':pix,'stored_projection_px':a['fitted_projection'],'difference_px':delta,'in_front':v.z>0,'manual_source_pixel':a['manual_source_pixel'],'source_error_px':sum((pix[i]-a['manual_source_pixel'][i])**2 for i in range(2))**.5})
 rows.append({'camera':r['camera'],'lens_mm':c.data.lens,'sensor_fit':c.data.sensor_fit,'sensor_width_mm':c.data.sensor_width,'shift':[c.data.shift_x,c.data.shift_y],'anchors':ar,'invalidated_anchors':invalid,'mean_error_px':sum(a['source_error_px'] for a in ar)/len(ar),'max_error_px':max(a['source_error_px'] for a in ar)})
res={'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cameras':rows,'max_projection_delta_px':max(abs(d) for r in rows for a in r['anchors'] for d in a['difference_px'])};(out/'R07-projection-independent.json').write_text(json.dumps(res,indent=2));print(res['max_projection_delta_px'])
