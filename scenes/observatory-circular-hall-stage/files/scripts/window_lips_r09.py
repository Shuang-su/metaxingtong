import bpy,json,pathlib,hashlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parents[1];audit={};front={1,2,3,13,14,15}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R08_{mode}.blend'));records=[]
 for o in sorted(list(bpy.data.objects),key=lambda x:x.name):
  if not o.name.startswith('WINDOW_'):continue
  k=int(o.name.split('_')[1]);wall=bpy.data.objects[f'WALL_{k:02d}_perforated'];n=Vector((wall.location.x,wall.location.y,0)).normalized();wv=[wall.matrix_world@v.co for v in wall.data.vertices];fv=[o.matrix_world@v.co for v in o.data.vertices];wlo=min(n.dot(v) for v in wv);whi=max(n.dot(v) for v in wv);flo=min(n.dot(v) for v in fv);fhi=max(n.dot(v) for v in fv);r={'object':o.name,'wall':wall.name,'normal':list(n),'old_wall_range':[wlo,whi],'old_frame_range':[flo,fhi],'old_inner_plane_gap':wlo-fhi}
  if k in front:
   outer=o.copy();outer.data=o.data;bpy.context.collection.objects.link(outer);outer.name=f'EXTERIOR_WINDOW_{k:02d}_conditional_lip';d=whi-.005-flo;outer.matrix_world.translation+=n*d;outer['R09_scope']='Conditional finite border proxy for six front windows in source15. Not proven metal/thickness/double-frame technology; glass and ornate tracery unknown. Rear eight exterior lips intentionally not invented.';r.update(new_outer=outer.name,outer_translation=list(n*d),shared_mesh_data_with_inner=True)
  d=wlo+.005-fhi;o.matrix_world.translation+=n*d;o['R09_scope']='Existing inner lip mounted to finite wall with shallow .005 overlap; profile unchanged, technical gap repair not source calibration.';r['inner_translation']=list(n*d);records.append(r)
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R09_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R09_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'windows':records,'source_scope':'Keep16-bay hypothesis unchanged; six new front-side border proxies only. All existing cameras/light/materials unchanged. Source matching FAILED.','model_sha256':hashlib.sha256((P/'models'/f'R09_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R09-window-applied.json').write_text(json.dumps(audit,indent=2))
