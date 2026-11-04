import bpy,json,pathlib,hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');O=pathlib.Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R09_material.blend'));s=bpy.context.scene;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;c=bpy.data.objects['SOURCE_15_exterior'];s.camera=c
src=json.load(open(P/'qa/R09-following-portal-source-diagnostic/annotations.json'))['images'][0]
frame=c.data.view_frame(scene=s);xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
origin=c.matrix_world.translation;R=c.matrix_world.to_3x3();out={'scope':'Diagnostic only. Fixed existing FAILED camera. One-view backprojection onto assumed front planes; no depth measurement or inferred opposite correspondence. No model saved.','model_sha256':hashlib.sha256((P/'models/R09_material.blend').read_bytes()).hexdigest(),'source_sha256':src['sha256'],'camera':c.name,'planes':{},'existing_door_bounds':{}}
for yy in [-6.36,-6.16,-5.96]:
 traces=[]
 for f in src['features']:
  if f['pixels_xy'] is None:continue
  points=[]
  for x,y in f['pixels_xy']:
   d=R@Vector((xmin+(x/1192)*(xmax-xmin),ymax-(y/671)*(ymax-ymin),-1));t=(yy-origin.y)/d.y;v=origin+t*d;q=world_to_camera_view(s,c,v);points.append({'pixel':[x,y],'world':list(v),'positive_ray':t>0,'roundtrip_error_px':[(q.x*1192-x),((1-q.y)*671-y)]})
  traces.append({'feature':f['id'],'semantic':f['semantic'],'points':points})
 out['planes'][str(yy)]=traces
for n in ['DOOR_00_gold_arch','DOOR_00_upper','DOOR_00_jamb_-1','DOOR_00_jamb_1']:
 o=bpy.data.objects[n];v=[o.matrix_world@x.co for x in o.data.vertices];pix=[world_to_camera_view(s,c,x) for x in v];out['existing_door_bounds'][n]={'world_min':[min(x[i] for x in v) for i in range(3)],'world_max':[max(x[i] for x in v) for i in range(3)],'pixel_bounds':[min(q.x*1192 for q in pix),min((1-q.y)*671 for q in pix),max(q.x*1192 for q in pix),max((1-q.y)*671 for q in pix)]}
(O/'result.json').write_text(json.dumps(out,indent=2));print(out['existing_door_bounds'])
