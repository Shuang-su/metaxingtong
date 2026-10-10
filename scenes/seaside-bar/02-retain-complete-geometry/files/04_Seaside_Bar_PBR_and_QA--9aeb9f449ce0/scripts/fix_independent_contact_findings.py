import bpy,json
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom';result={}
for typ in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');S=bpy.context.scene;bpy.context.view_layer.update();rows=[]
 def top(o):return max((o.matrix_world@Vector(v)).z for v in o.bound_box)
 def extend(o,target):
  old=top(o);dz=target-old;o.dimensions.z+=dz;bpy.context.view_layer.update();o.location.z+=dz/2;bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);rows.append({'object':o.name,'old_top':old,'new_top':top(o),'intent':'延伸至与对应台面0.005单位相交，保留底面'})
 for o in list(bpy.data.objects):
  if o.name=='服务吧台_前立面' or o.name.startswith('服务吧台_支撑肋'):extend(o,.530)
 for n in ['Left_front_apron','Right_front_apron']:extend(bpy.data.objects[n],1.140)
 o=bpy.data.objects['Upright_book_right_00_pageblock'];o.dimensions.x+=.0024;bpy.context.view_layer.update();o.dimensions.y+=.0024;bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);rows.append({'object':o.name,'intent':'页芯x/y各增0.0024单位，与书脊/封面连接'})
 result[typ]=rows;S['independent_QA_corrections']='前台支撑和左右裙板延至台面内0.005；孤立页芯微扩至书脊/封面连接。'
 bpy.ops.wm.save_as_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/seaside_bar_complete_'+typ+'.glb',export_format='GLB',use_selection=True,export_yup=True)
 names=[o.name for o in bpy.data.objects if o.type=='CAMERA' and (typ=='textured' or o.name.startswith(('源图','01_','05_')))]
 for name in names:
  S.camera=bpy.data.objects[name];S.render.resolution_x=1180 if name.startswith('源图') else 1000;S.render.resolution_y=663 if name.startswith('源图') else 750;S.cycles.samples=48 if name=='01_前方全貌' else 24;S.render.filepath=R+'/renders/'+name+('_材质.png' if typ=='textured' else '_白模.png');bpy.ops.render.render(write_still=True)
json.dump(result,open(R+'/qa/independent_contact_fixes.json','w'),ensure_ascii=False,indent=2)
