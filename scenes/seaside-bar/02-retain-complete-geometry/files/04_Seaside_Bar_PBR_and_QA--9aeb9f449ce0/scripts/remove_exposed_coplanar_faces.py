import bpy,json
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom';report={}
for typ in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');S=bpy.context.scene;bpy.context.view_layer.update();rows=[]
 def apply(o):
  bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o=bpy.data.objects['左侧矩形开口_下墙'];o.location.x=(-4.38-3.435)/2;o.dimensions.x=(-3.435)-(-4.38);apply(o);rows.append({'object':o.name,'x_bounds':[-4.38,-3.435],'fix':'去除与外柱和主下墙的外露共面叠面，保持边界连接'})
 for o in list(bpy.data.objects):
  if o.name.startswith('Right_cream_apron_leg'):
   rows.append({'object':o.name,'fix':'删除与完整柜侧板重复的旧腿'});bpy.data.objects.remove(o,do_unlink=True)
 for o in bpy.data.objects:
  if o.name.startswith('右操作柜_全高侧板'):
   old=max((o.matrix_world@Vector(p)).z for p in o.bound_box);delta=1.14-old;o.dimensions.z+=delta;bpy.context.view_layer.update();o.location.z+=delta/2;apply(o);rows.append({'object':o.name,'top':1.14,'fix':'完整柜侧板接入台面，替代旧腿支撑'})
 o=bpy.data.objects.get('Raised_bottle_display')
 if o:rows.append({'object':o.name,'fix':'删除与阶梯0重复的顶面；保留三阶实体与两支腿'});bpy.data.objects.remove(o,do_unlink=True)
 o=bpy.data.objects['短侧墙_左侧墙角'];o.location.y=(-.475+.91)/2;o.dimensions.y=.91-(-.475);apply(o);rows.append({'object':o.name,'y_bounds':[-.475,.91],'fix':'裁到外柱前面，消除外露x侧面重叠'})
 report[typ]=rows;S['coplanar_cleanup']='左下墙与柱/主下墙裁边；右柜去重复腿并接台面；瓶架去重复面；左返墙裁至柱前面。'
 bpy.ops.wm.save_as_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/seaside_bar_complete_'+typ+'.glb',export_format='GLB',use_selection=True,export_yup=True)
json.dump(report,open(R+'/qa/coplanar_face_cleanup.json','w'),ensure_ascii=False,indent=2)
for typ in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');S=bpy.context.scene
 names=[o.name for o in bpy.data.objects if o.type=='CAMERA' and (typ=='textured' or o.name.startswith(('源图','01_','05_')))]
 for name in names:
  S.camera=bpy.data.objects[name];S.render.resolution_x=1180 if name.startswith('源图') else 1000;S.render.resolution_y=663 if name.startswith('源图') else 750;S.cycles.samples=48 if name=='01_前方全貌' else 24;S.render.filepath=R+'/renders/'+name+('_材质.png' if typ=='textured' else '_白模.png');bpy.ops.render.render(write_still=True)
