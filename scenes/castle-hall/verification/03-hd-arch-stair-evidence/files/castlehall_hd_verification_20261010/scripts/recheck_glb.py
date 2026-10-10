import bpy,json,hashlib
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'castle_hall_fullroom/models'
def inventory():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();vs=np.array([list(o.matrix_world@v.co) for v in o.data.vertices]);vs=np.unique(np.round(vs,5),axis=0)
  out[o.name]={'triangles':len(o.data.loop_triangles),'unique_positions':len(vs),'position_sha_1e5':hashlib.sha256(vs.astype('<f8').tobytes()).hexdigest(),'uv':len(o.data.uv_layers)>0}
 return out
bpy.ops.wm.open_mainfile(filepath=str(P/'Xingtong_Castle_Hall_FullRoom.blend'));a=inventory()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/'Xingtong_Castle_Hall_FullRoom.glb'));b=inventory()
res={'blend_sha':hashlib.sha256((P/'Xingtong_Castle_Hall_FullRoom.blend').read_bytes()).hexdigest(),'glb_sha':hashlib.sha256((P/'Xingtong_Castle_Hall_FullRoom.glb').read_bytes()).hexdigest(),'blend_meshes':len(a),'glb_meshes':len(b),'same_names':set(a)==set(b),'blend_triangles':sum(v['triangles'] for v in a.values()),'glb_triangles':sum(v['triangles'] for v in b.values()),'all_glb_meshes_uv':all(v['uv'] for v in b.values()),'quantized_vertex_hash_differences':[k for k in a.keys()&b.keys() if a[k]['position_sha_1e5']!=b[k]['position_sha_1e5']],'method':'Blender roundtrip, world vertices unique and rounded to 1e-5 model units; technical parity only, not source acceptance.'}
res['pass']=res['same_names'] and res['blend_triangles']==res['glb_triangles'] and res['all_glb_meshes_uv'] and not res['quantized_vertex_hash_differences']
(R/'qa/current_glb_reimport_check.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
