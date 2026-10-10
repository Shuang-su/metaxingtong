import bpy, json, hashlib, os, sys
from mathutils import Vector
from mathutils.kdtree import KDTree
R='/workspace/scratch/fa58bfcf0425'
OUT=R+'/ktv_fixed_visibility_20261010'
paths={'legacy':R+'/ktv_fullroom/source/restored/models/Xingtong_KTV_Textured.blend','current':R+'/ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.blend','current_white':R+'/ktv_fullroom/delivery/models/KTV_Complete_Open_Stage_White.blend'}
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def snapshot():
 sc=bpy.context.scene
 geo=[]; meshes=[]
 for o in sorted(sc.objects,key=lambda o:o.name):
  if o.type!='MESH':continue
  geo.append({'name':o.name,'matrix':[list(row) for row in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons]})
  meshes.append({'name':o.name,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_get':o.hide_get(),'visible_camera':o.visible_camera,'collections':[c.name for c in o.users_collection]})
 coll=[{'name':c.name,'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in sorted(bpy.data.collections,key=lambda c:c.name)]
 def lc(c):return {'name':c.name,'exclude':c.exclude,'hide_viewport':c.hide_viewport,'holdout':c.holdout,'indirect_only':c.indirect_only,'children':[lc(x) for x in c.children]}
 vis={'meshes':meshes,'collections':coll,'view_layers':{v.name:lc(v.layer_collection) for v in sc.view_layers}}
 return {'geometry_sha256':digest(geo),'visibility_sha256':digest(vis),'visibility':vis,'mesh_count':len(meshes)}
res={}
for key,path in paths.items():
 bpy.ops.wm.open_mainfile(filepath=path);sc=bpy.context.scene
 initial=snapshot();cams={}
 for cam in sorted([o for o in sc.objects if o.type=='CAMERA'],key=lambda o:o.name):
  sc.camera=cam;bpy.context.view_layer.update();p=snapshot()
  cams[cam.name]={'matrix_world':[list(row) for row in cam.matrix_world],'lens_mm':cam.data.lens,'sensor_width':cam.data.sensor_width,'sensor_fit':cam.data.sensor_fit,'shift_x':cam.data.shift_x,'shift_y':cam.data.shift_y,'type':cam.data.type,'geometry_sha256':p['geometry_sha256'],'visibility_sha256':p['visibility_sha256']}
 res[key]={'file':path,'sha256':hashlib.sha256(open(path,'rb').read()).hexdigest(),'initial':initial,'cameras':cams,'all_camera_geometry_equal':len(set(x['geometry_sha256'] for x in cams.values()))==1,'all_camera_visibility_equal':len(set(x['visibility_sha256'] for x in cams.values()))==1,'scene_animation':bool(sc.animation_data),'objects_with_animation':[o.name for o in sc.objects if o.animation_data],'collections_with_animation':[c.name for c in bpy.data.collections if getattr(c,'animation_data',None)],'render_handlers':[str(h) for h in bpy.app.handlers.render_pre],'frame':sc.frame_current,'render':{'engine':sc.render.engine,'resolution_x':sc.render.resolution_x,'resolution_y':sc.render.resolution_y,'percentage':sc.render.resolution_percentage,'samples':sc.cycles.samples}}
json.dump(res,open(OUT+'/audit/blender_visibility_audit.json','w'),indent=2)
print('VISIBILITY_AUDIT',json.dumps({k:{'meshes':v['initial']['mesh_count'],'all_camera_visibility_equal':v['all_camera_visibility_equal'],'all_camera_geometry_equal':v['all_camera_geometry_equal'],'geom':v['initial']['geometry_sha256'],'vis':v['initial']['visibility_sha256']} for k,v in res.items()}))

def gather():
 d={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or any(c.name=='09_Optional_Moving_Balloon_Dog' for c in o.users_collection):continue
  o.data.calc_loop_triangles();d[o.name]={'points':[tuple(o.matrix_world@v.co) for v in o.data.vertices],'triangles':len(o.data.loop_triangles),'uv':bool(o.data.uv_layers)}
 return d
def dist(a,b):
 kd=KDTree(len(b))
 for i,p in enumerate(b):kd.insert(Vector(p),i)
 kd.balance();return max(kd.find(Vector(p))[2] for p in a)
bpy.ops.wm.open_mainfile(filepath=paths['current']);a=gather()
glb=R+'/ktv_fullroom/delivery/models/KTV_Complete_Open_Stage.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=glb);b=gather()
compare={'file':glb,'sha256':hashlib.sha256(open(glb,'rb').read()).hexdigest(),'actual_import':True,'count_before':len(a),'count_after':len(b),'missing':sorted(set(a)-set(b)),'extra':sorted(set(b)-set(a)),'triangle_mismatch':[],'vertex_distance_max':0,'vertex_distance_over_1e-5':[],'uv_missing':[],'uv_missing_before':[n for n,v in a.items() if not v['uv']],'triangles_before':sum(x['triangles'] for x in a.values()),'triangles_after':sum(x['triangles'] for x in b.values())}
for n,v in a.items():
 if n not in b:continue
 w=b[n]
 if v['triangles']!=w['triangles']:compare['triangle_mismatch'].append(n)
 m=max(dist(v['points'],w['points']),dist(w['points'],v['points']))
 compare['vertex_distance_max']=max(compare['vertex_distance_max'],m)
 if m>1e-5:compare['vertex_distance_over_1e-5'].append([n,m])
 if not w['uv']:compare['uv_missing'].append(n)
json.dump(compare,open(OUT+'/qa/current_actual_glb_roundtrip.json','w'),indent=2);print('ACTUAL_GLB',json.dumps(compare))
