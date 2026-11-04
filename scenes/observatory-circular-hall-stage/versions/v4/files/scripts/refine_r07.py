import bpy,json,pathlib,math,hashlib
P=pathlib.Path(__file__).resolve().parents[1];D=json.load(open(P/'qa/R07-band-trial.json'));audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R06_{mode}.blend'));o=bpy.data.objects['FLOOR_four_point_inlay'];changes=[]
 # R06 polygon order after -45-degree rotation starts +X then CCW; rings offset8 and24 are inner bottom/top.
 for base in [8,24]:
  for i,xy in enumerate(D['inner_xy']):
   v=o.data.vertices[base+i];old=list(v.co);v.co.x=xy[0];v.co.y=xy[1];changes.append({'index':base+i,'old':old,'new':list(v.co)})
 o['R07_evidence']='Parallel-edge inset hypothesis using seven approximate inner tips. Outer loop/cameras unchanged. Not accepted source match; preserve R06.';o.data.update();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R07_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R07_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'changed_vertices':changes,'model_sha256':hashlib.sha256((P/'models'/f'R07_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R07-applied.json').write_text(json.dumps(audit,indent=2))
