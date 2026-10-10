import bpy,json,hashlib,math
from mathutils import Vector
ROOT='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery'
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/KTV_Complete_Open_Stage.blend');sc=bpy.context.scene;sc.render.resolution_x=1188;sc.render.resolution_y=668
from bpy_extras.object_utils import world_to_camera_view
anchors=[('lamp shade center',(-2.55,2.05,2.18),(215,164)),('left seat center',(-.81,-.075,.365),(441,513)),('right seat center',(.93,-.075,.365),(769,513)),('left silver star',(-1.36,.1,2.43),(349,139)),('right silver star',(2.88,.5,2.73),(1114,77))]
r=[]
for n,p,xy in anchors:
 v=world_to_camera_view(sc,bpy.data.objects['MATCH_A_01h15m29s'],Vector(p));q=(v.x*1188,(1-v.y)*668);r.append({'anchor':n,'source_pixel':xy,'projected_pixel':q,'residual_px':math.dist(q,xy)})
json.dump({'reference':'frame_4529_crop.png','size':[1188,668],'hand_clicked_approximate_points':True,'anchors':r,'rms_px':math.sqrt(sum(x['residual_px']**2 for x in r)/len(r)),'caution':'Sparse anchors do not establish full-image correspondence. No image warping or per-camera geometry changes.'},open(ROOT+'/qa/anchor_residuals.json','w'),indent=2)
def gather():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or any(c.name=='09_Optional_Moving_Balloon_Dog' for c in o.users_collection):continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];o.data.calc_loop_triangles();out[o.name]={'triangles':len(o.data.loop_triangles),'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'raw_points':[tuple(p) for p in pts],'coordinate_set':set(tuple(round(x,5) for x in p) for p in pts)}
 return out
before=gather();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=ROOT+'/models/KTV_Complete_Open_Stage.glb');after=gather();diff=[]
for n,a in before.items():
 b=after.get(n)
 if not b:diff.append({'missing':n});continue
 if a['triangles']!=b['triangles'] or a['coordinate_set']!=b['coordinate_set']:
  from mathutils.kdtree import KDTree
  kd=KDTree(len(b['raw_points']))
  for i,p in enumerate(b['raw_points']):kd.insert(Vector(p),i)
  kd.balance();d1=max(kd.find(Vector(p))[2] for p in a['raw_points'])
  kd=KDTree(len(a['raw_points']))
  for i,p in enumerate(a['raw_points']):kd.insert(Vector(p),i)
  kd.balance();d2=max(kd.find(Vector(p))[2] for p in b['raw_points'])
  diff.append({'object':n,'max_bidirectional_distance':max(d1,d2),'triangles_before':a['triangles'],'triangles_after':b['triangles'],'coordinate_set_equal_5dp':a['coordinate_set']==b['coordinate_set']})
json.dump({'actual_import':True,'mesh_count_before':len(before),'mesh_count_after':len(after),'triangle_count_before':sum(x['triangles'] for x in before.values()),'triangle_count_after':sum(x['triangles'] for x in after.values()),'differences':diff,'note':'Vertex splits for UV/normals do not change unique world coordinate sets; 5-decimal quantization may flag tiny floating point roundoff.'},open(ROOT+'/qa/glb_roundtrip.json','w'),indent=2)
