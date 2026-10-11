import bpy,os,json,re
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom';reports={}
def bounds(o):return [o.matrix_world@Vector(p) for p in o.bound_box]
def lo(objs):return min(v.z for o in objs for v in bounds(o))
def hi(objs):return max(v.z for o in objs for v in bounds(o))
for typ in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');S=bpy.context.scene;bpy.context.view_layer.update();report=[]
 def group(prefix):return [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefix)]
 def seat(prefix,z):
  objs=group(prefix)
  if not objs:return
  old=lo(objs);dz=z-old
  for o in objs:o.location.z+=dz
  bpy.context.view_layer.update();report.append({'assembly':prefix,'previous_min_z':old,'support_top_z':z,'translation_z':dz,'new_min_z':lo(objs),'residual_units':abs(lo(objs)-z)})
 top=hi([bpy.data.objects['Foreground_wood_top']]);prep=hi([bpy.data.objects['Right_prep_counter_top']])
 for p in ['Foreground_red_martini','Foreground_small_pink','Foreground_coral_martini','Foreground_yellow_martini','Citrus_can_','Round_serving_tray']:seat(p,top)
 # Fallen assembly's children keep their exact parent-relative transforms.
 e=bpy.data.objects.get('Fallen_can_assembly');objs=[o for o in bpy.data.objects if o.parent==e and o.type=='MESH'];old=lo(objs);e.location.z+=top-old;bpy.context.view_layer.update();report.append({'assembly':'Fallen_can_assembly','residual_units':abs(lo(objs)-top)})
 for i in range(5):seat('Prep_tumbler_%02d'%i,prep)
 seat('Right_prep_pink_',prep)
 for stem in ['Upright_book_left_','Upright_book_right_','Far_right_volume_']:
  for i in range(8):seat(stem+'%02d'%i,prep) if stem!='Far_right_volume_' else seat(stem+str(i),prep)
 seat('Leaning_book',prep)
 z=prep
 for i in range(4):
  objs=group('Horizontal_stack_pages_'+str(i))+group('Horizontal_stack_cover_'+str(i));old=lo(objs);delta=z-old
  for o in objs:o.location.z+=delta
  bpy.context.view_layer.update();report.append({'assembly':'Horizontal_stack_'+str(i),'residual_units':abs(lo(objs)-z)});z=hi(objs)
 # Plinth plus glass move as one supported assembly.
 pl=bpy.data.objects['右薄荷杯_台面补块'];delta=prep-lo([pl]);pl.location.z+=delta
 for o in group('Right_back_mint_martini'):o.location.z+=delta
 sill=hi([bpy.data.objects['Window_sill']]);foot=bpy.data.objects['Lamp_dark_foot'];delta=sill-lo([foot]);foot.location.z+=delta;bpy.data.objects['Cylindrical_amber_table_lamp'].location.z+=delta
 shelf=bpy.data.objects['瓶架_阶梯实体_0'];shelf.location.y=0;shelf.dimensions.y=.35
 bpy.context.view_layer.update()
 # Solid mounting shoes overlap both jamb and lower strut/mount cylinder.
 m=bpy.data.materials.get('Brushed_metal') if typ=='textured' else bpy.data.materials.get('中性白模');C=bpy.data.collections['09_推断_地面柜体墙角']
 for name,x in [('左撑杆_实体安装座',-2.64),('右撑杆_实体安装座',3.62)]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,.90,3.27));o=bpy.context.object;o.name=name;o.dimensions=(.18,.13,.16);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
  for c in list(o.users_collection):c.objects.unlink(o)
  C.objects.link(o);o['evidence']='源图支持撑杆；安装座实体厚度推断'
 S['support_revision']='统一补撑杆安装座并将杯盘、书与灯座接触落台。'
 bpy.context.view_layer.update();reports[typ]=report
 bpy.ops.wm.save_as_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/seaside_bar_complete_'+typ+'.glb',export_format='GLB',use_selection=True,export_yup=True)
 names=[o.name for o in bpy.data.objects if o.type=='CAMERA' and (typ=='textured' or o.name.startswith(('源图','01_','05_')))]
 for name in names:
  S.camera=bpy.data.objects[name];S.render.resolution_x=1180 if name.startswith('源图') else 1000;S.render.resolution_y=663 if name.startswith('源图') else 750;S.cycles.samples=48 if name=='01_前方全貌' else 24;S.render.filepath=R+'/renders/'+name+('_材质.png' if typ=='textured' else '_白模.png');bpy.ops.render.render(write_still=True)
json.dump(reports,open(R+'/qa/assembly_contact_corrections.json','w'),ensure_ascii=False,indent=2)
