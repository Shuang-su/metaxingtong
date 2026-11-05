import bpy,pathlib,json,math,hashlib
P=pathlib.Path(__file__).resolve().parents[1];audit={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R05_{mode}.blend'));changed=[]
 for side in [-1,1]:
  o=bpy.data.objects[f'MANNEQUIN_red_bifurcated_lower_proxy_{side}'];L=len(o.data.vertices);old=[]
  for j in range(24):
   v=o.data.vertices[L-24+j];old.append(list(v.co));t=2*math.pi*j/24;v.co.x=3.85+side*.09+.075*math.cos(t);v.co.y=2.78+.06*math.sin(t)
  o.data.update();o['R06_scope']='Only top24 garment vertices XY narrowed into upper-clothing proxy; lower silhouette/Z/topology unchanged. Technical cap concealment, not source pattern proof.';changed.append({'object':o.name,'indices':list(range(L-24,L)),'old':old,'new':[list(v.co) for v in o.data.vertices[L-24:L]]})
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'models'/f'R06_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R06_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);audit[mode]={'changes':changed,'model_sha256':hashlib.sha256((P/'models'/f'R06_{mode}.blend').read_bytes()).hexdigest()}
(P/'qa/R06-mannequin-applied.json').write_text(json.dumps(audit,indent=2))
