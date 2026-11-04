import bpy,pathlib,json,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R08_{mode}.blend'));case=bpy.data.objects['COSMETIC_case_body'];top=max((case.matrix_world@v.co).z for v in case.data.vertices);changes=[]
 for name in sorted(n for n in bpy.data.objects.keys() if n.startswith('CASE_handle_leg_')):
  o=bpy.data.objects[name];M=o.matrix_world.copy();I=M.inverted();low=min((M@v.co).z for v in o.data.vertices);records=[]
  for v in o.data.vertices:
   w=M@v.co
   if abs(w.z-low)<1e-6:
    old=list(v.co);w.z=top-.001;v.co=I@w;records.append({'index':v.index,'old_local':old,'new_local':list(v.co)})
  o.data.update();changes.append({'object':name,'root_before':low,'case_top':top,'changes':records})
 a=bpy.data.objects[changes[0]['object']].matrix_world.translation;d=bpy.data.cameras.new('DIAG_case_handle_mount');d.lens=65;d.clip_start=.0005;o=bpy.data.objects.new('DIAG_case_handle_mount',d);bpy.context.collection.objects.link(o);o.location=(a.x-.055,a.y-.13,top+.038);o.rotation_euler=(Vector((a.x,a.y,top+.008))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R09_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R09_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'changes':changes,'scope':'two existing proxy handle root caps extended only; not measured hardware, not welded or load-bearing proof; case/table gap and other tabletop collisions remain','model_sha256':hashlib.sha256((P/'models'/f'R09_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R09-handle-applied.json').write_text(json.dumps(audit,indent=2))
