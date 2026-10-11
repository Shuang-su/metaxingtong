import bpy,json,hashlib
R='/workspace/scratch/fa58bfcf0425/dark_cell_v1';d={}
for kind in ['blend','glb']:
 for typ in ['textured','white']:
  p=R+'/models/dark_cell_'+typ+'.'+kind
  if kind=='blend':bpy.ops.wm.open_mainfile(filepath=p)
  else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=p)
  bpy.context.view_layer.update();ts=[]
  for o in bpy.context.scene.objects:
   if o.type!='MESH':continue
   o.data.calc_loop_triangles()
   ts.extend(tuple(sorted(tuple(o.matrix_world@o.data.vertices[i].co) for i in t.vertices)) for t in o.data.loop_triangles)
  d[kind+'_'+typ]=hashlib.sha256(json.dumps(sorted(ts)).encode()).hexdigest()
d['blend_twins_identical']=d['blend_textured']==d['blend_white'];d['glb_twins_identical']=d['glb_textured']==d['glb_white'];json.dump(d,open(R+'/qa/independent/twin_geometry.json','w'),indent=2)
