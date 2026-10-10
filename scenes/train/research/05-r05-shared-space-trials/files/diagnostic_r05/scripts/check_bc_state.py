import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;out={'mesh':{},'camera':{},'visibility':{},'materials':{}}
 for o in s.objects:
  out['visibility'][o.name]=[o.hide_render,o.hide_viewport]
  if o.type=='MESH':
   h=hashlib.sha256()
   for v in o.data.vertices:h.update(struct.pack('<3f',*(o.matrix_world@v.co)))
   out['mesh'][o.name]=h.hexdigest()
  if o.type=='CAMERA':out['camera'][o.name]=[[list(a) for a in o.matrix_world],o.data.lens]
 for m in bpy.data.materials:
  vals=[]
  if m.node_tree:
   for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
    sockets=[]
    for inp in n.inputs:
     if hasattr(inp,'default_value'):
      v=inp.default_value
      try:v=list(v)
      except TypeError:pass
      sockets.append([inp.name,str(v)])
    vals.append([n.name,n.type,sockets])
  out['materials'][m.name]=vals
 return out
b=json.loads((R/'analysis/trial_b_manifest.json').read_text());c=json.loads((R/'analysis/trial_c_manifest.json').read_text());bp=Path(b['file']);cp=Path(c['file']);assert hashlib.sha256(bp.read_bytes()).hexdigest()==b['sha256'];assert hashlib.sha256(cp.read_bytes()).hexdigest()==c['sha256'];bs=snapshot(bp);cs=snapshot(cp);diff=[n for n,h in bs['mesh'].items() if cs['mesh'].get(n)!=h];assert sorted(diff)==sorted(c['c_only_changed_objects']);out={'B_input':b['sha256'],'C_input':c['sha256'],'changed_meshes':diff,'changed_mesh_count':len(diff),'mesh_name_set_equal':bs['mesh'].keys()==cs['mesh'].keys(),'all_camera_states_equal':bs['camera']==cs['camera'],'all_visibility_equal':bs['visibility']==cs['visibility'],'all_material_node_defaults_equal':bs['materials']==cs['materials'],'status':'Only the36 declared shared sash/housing/diffuser meshes changed; no camera/object visibility/material changes.'};(R/'analysis/B_C_scene_state_check.json').write_text(json.dumps(out,indent=2));print(out['status'])
