import bpy,json
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1';d={}
for typ in ['blend','glb']:
 if typ=='blend':bpy.ops.wm.open_mainfile(filepath=R+'/models/dark_cell_textured.blend')
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=R+'/models/dark_cell_textured.glb')
 bpy.context.view_layer.update();d[typ]={}
 for name in [o.name for o in bpy.context.scene.objects if o.type=='MESH']:
  o=bpy.data.objects[name];o.data.calc_loop_triangles();d[typ][name]=[[list(o.matrix_world@o.data.vertices[i].co) for i in t.vertices] for t in o.data.loop_triangles]
json.dump(d,open(R+'/qa/independent/surface_examples.json','w'))
