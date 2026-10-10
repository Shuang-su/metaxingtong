import bpy,os
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom'
for typ in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend');S=bpy.context.scene
 o=bpy.data.objects.get('Wall_below_window')
 if o:bpy.data.objects.remove(o,do_unlink=True)
 o=bpy.data.objects['海侧墙_下部补齐'];o.location.z=.5525;o.dimensions.z=2.005;bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o=bpy.data.objects.get('Lower_window_apron')
 if o:o.location.y=.825
 bpy.ops.wm.save_as_mainfile(filepath=R+'/models/seaside_bar_complete_'+typ+'.blend')
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=R+'/models/seaside_bar_complete_'+typ+'.glb',export_format='GLB',use_selection=True,export_yup=True)
 names=[o.name for o in bpy.data.objects if o.type=='CAMERA' and (typ=='textured' or o.name.startswith(('源图','01_','05_')))]
 for name in names:
  S.camera=bpy.data.objects[name];S.render.resolution_x=1180 if name.startswith('源图') else 1000;S.render.resolution_y=663 if name.startswith('源图') else 750;S.render.filepath=R+'/renders/'+name+('_材质.png' if typ=='textured' else '_白模.png');bpy.ops.render.render(write_still=True)
