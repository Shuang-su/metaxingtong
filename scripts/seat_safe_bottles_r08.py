import bpy,pathlib,json,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];safe=[0,1,2,9,10,11,13,14,15,16];audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R07_{mode}.blend'));table=bpy.data.objects['TABLE_top'];top=max((table.matrix_world@v.co).z for v in table.data.vertices);changes=[]
 for i in safe:
  body=bpy.data.objects[f'COSMETIC_bottle_proxy_{i}'];cap=bpy.data.objects[f'COSMETIC_cap_proxy_{i}'];bottom=min((body.matrix_world@v.co).z for v in body.data.vertices);dz=top-.0003-bottom
  for o in [body,cap]:o.location.z+=dz
  changes.append({'index':i,'old_body_bottom':bottom,'table_top':top,'translation_z':dz,'scope':'body+cap only, XY unchanged; shallow intersection .0003 working units not measured physical contact or source geometry'})
 body=bpy.data.objects['COSMETIC_bottle_proxy_0'];c=body.matrix_world.translation;d=bpy.data.cameras.new('DIAG_bottle_mount');d.lens=70;d.clip_start=.0005;o=bpy.data.objects.new('DIAG_bottle_mount',d);bpy.context.collection.objects.link(o);o.location=(c.x,c.y-.18,top+.024);o.rotation_euler=(Vector((c.x,c.y,top+.007))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R08_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R08_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'changes':changes,'remaining_unmodified_indices':[3,4,5,6,7,8,12],'model_sha256':hashlib.sha256((P/'models'/f'R08_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R08-bottle-applied.json').write_text(json.dumps(audit,indent=2))
