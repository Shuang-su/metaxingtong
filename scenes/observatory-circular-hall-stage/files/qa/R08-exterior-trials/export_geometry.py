import bpy,pathlib,json,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425');model=P/'observatory-candidate-20261104/models/R07_material.blend';bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;cam=bpy.data.objects['SOURCE_15_exterior'];objects={}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 if o.name.startswith(('WALL_','COLUMN_','DOOR_00_','DOOR_08_')) or o.name in ['ROOF_drum','ROOF_gold_cornice','ROOF_hollow_dome','ROOF_centre_spire','TERRACE_portal_00']:
  objects[o.name]={'vertices':[list(o.matrix_world@v.co)for v in o.data.vertices],'faces':[list(f.vertices)for f in o.data.polygons]}
x={'model_path':str(model),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'camera':{'matrix_world':[list(row)for row in cam.matrix_world],'lens':cam.data.lens,'sensor_width':cam.data.sensor_width,'sensor_height':cam.data.sensor_height,'sensor_fit':cam.data.sensor_fit,'shift_x':cam.data.shift_x,'shift_y':cam.data.shift_y,'resolution':[s.render.resolution_x,s.render.resolution_y],'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y]},'objects':objects,'scope':'read-only exact R07 world geometry for conditional source15 camera diagnosis, not geometry acceptance'}
(P/'observatory-exterior-fit-20261105/geometry.json').write_text(json.dumps(x,indent=2))
