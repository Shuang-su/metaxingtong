import bpy,pathlib,json,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R12_{mode}.blend'));table=bpy.data.objects['TABLE_top'];top=max((table.matrix_world@v.co).z for v in table.data.vertices);changes=[]
 for i in range(3,9):
  body=bpy.data.objects[f'COSMETIC_bottle_proxy_{i}'];bottom=min((body.matrix_world@v.co).z for v in body.data.vertices);dz=top-.0003-bottom
  for n in [f'COSMETIC_bottle_proxy_{i}',f'COSMETIC_cap_proxy_{i}']:
   o=bpy.data.objects[n];before=list(o.location);o.location.z+=dz;changes.append({'object':n,'old_location':before,'new_location':list(o.location),'dz':dz})
 c=bpy.data.objects['COSMETIC_bottle_proxy_8'].matrix_world.translation;d=bpy.data.cameras.new('DIAG_relocated_bottle8_mount');d.lens=70;d.clip_start=.0005;o=bpy.data.objects.new('DIAG_relocated_bottle8_mount',d);bpy.context.collection.objects.link(o);o.location=(c.x,c.y-.15,top+.028);o.rotation_euler=(Vector((c.x,c.y,top+.004))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R13_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R13_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'changes':changes,'table_top':top,'scope':'After R12 safe XY relocation, six existing left bottles3..8 plus caps lowered as rigid pairs to shallow .0003 table overlap; no source calibration. Other tabletop gaps/collisions remain.','model_sha256':hashlib.sha256((P/'models'/f'R13_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R13-seating-applied.json').write_text(json.dumps(audit,indent=2))
