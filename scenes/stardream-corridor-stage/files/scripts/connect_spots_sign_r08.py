import bpy,pathlib,json
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];records=[]
def bound(o,axis,high):return (max if high else min)((o.matrix_world@v.co)[axis] for v in o.data.vertices)
def extend(o,axis,target):
 M=o.matrix_world.copy();I=M.inverted();old=bound(o,axis,True);ids=[]
 for v in o.data.vertices:
  w=M@v.co
  if abs(w[axis]-old)<1e-6:w[axis]=target;v.co=I@w;ids.append(v.index)
 return {'object':o.name,'axis':axis,'original_cap':old,'target':target,'vertex_ids':ids,'changed_vertex_count':len(ids),'other_vertices_unchanged_intent':True}
cameras=[{'name':'DIAG_spot_mount','position':[1.95,-4.55,3.43],'target':[1.8,-4.8,3.465],'lens':65},{'name':'DIAG_sign_profile','position':[.7,5.88,2.67],'target':[0,5.95,2.64],'lens':60}]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R07_{mode}.blend'));rs=[]
 for side in [-1,1]:
  roofbottom=bound(bpy.data.objects[f'SOFFIT_{side}'],2,False)
  for j in range(5):
   rim=bpy.data.objects[f'SPOT_rim_{side}_{j}'];diff=bpy.data.objects[f'SPOT_diffuser_{side}_{j}'];rs.append(extend(rim,2,roofbottom+.001));rs.append(extend(diff,2,bound(rim,2,False)+.001))
 wallfront=bound(bpy.data.objects['WALL_end_1_lintel'],1,False);sign=bpy.data.objects['ONAIR_sign_back'];rs.append(extend(sign,1,wallfront+.005));rs.append(extend(bpy.data.objects['ONAIR_text'],1,bound(sign,1,False)+.001))
 for a in cameras:
  d=bpy.data.cameras.new(a['name']);d.lens=a['lens'];d.clip_start=.001;d.clip_end=100;o=bpy.data.objects.new(a['name'],d);bpy.context.collection.objects.link(o);o.location=a['position'];o.rotation_euler=(Vector(a['target'])-o.location).to_track_quat('-Z','Y').to_euler();o['scope']='Synthetic installation diagnostic, not source matching; same existing lights/world'
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R08_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R08_{mode}.glb'),export_format='GLB',export_cameras=True);records.append({'mode':mode,'changes':rs,'scope':'only installation/back caps extended; source construction inferred, not measured'})
(P/'qa/R08-cap-changes.json').write_text(json.dumps(records,indent=2));(P/'qa/R08-diagnostic-cameras.json').write_text(json.dumps(cameras,indent=2))
