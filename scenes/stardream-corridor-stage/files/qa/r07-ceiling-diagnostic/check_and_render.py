import bpy,pathlib,json,hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-ceiling-qa-20261105');f=P/'models/R06_white.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene;s.camera=bpy.data.objects['CHECK_05'];s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100
r={'model_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'rails':{}}
for o in s.objects:
 if 'rail' not in o.name.lower():continue
 v=[o.matrix_world@x.co for x in o.data.vertices];r['rails'][o.name]={'bounds':[[min(x[i] for x in v),max(x[i] for x in v)] for i in range(3)],'faces':[[list(o.matrix_world@o.data.vertices[i].co) for i in p.vertices] for p in o.data.polygons]}
r['intersections']=[]
for n,a in r['rails'].items():
 if 'crossrail' not in n:continue
 b=r['rails']['CEILING_center_rail'];lo=[max(a['bounds'][i][0],b['bounds'][i][0]) for i in range(3)];hi=[min(a['bounds'][i][1],b['bounds'][i][1]) for i in range(3)];pt=Vector([(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]]);ndc=world_to_camera_view(s,s.camera,pt);r['intersections'].append({'cross':n,'overlap_lo':lo,'overlap_hi':hi,'bottom_pixel':[ndc.x*1192,(1-ndc.y)*671],'bottom_planes_exact_equal':a['bounds'][2][0]==b['bounds'][2][0]})
(Q/'geometry.json').write_text(json.dumps(r,indent=2))
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=1;s.render.image_settings.file_format='PNG';s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=560/1192;s.render.border_max_x=630/1192;s.render.border_min_y=1-280/671;s.render.border_max_y=1-220/671
for name,shift in [('baseline',0),('center_down_001',-.001)]:
 bpy.data.objects['CEILING_center_rail'].location.z+=shift;bpy.context.view_layer.update();s.render.filepath=str(Q/(name+'.png'));bpy.ops.render.render(write_still=True)
print('DONE')
