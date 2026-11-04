import bpy,json
from pathlib import Path
O=Path(__file__).parent
def extra_state():
 def val(v):
  if isinstance(v,(str,int,float,bool)):return v
  try:return list(v)
  except:return str(v)
 def tree(t):
  if t is None:return None
  return {'nodes':{n.name:{'type':n.bl_idname,'inputs':[(v.name,val(v.default_value)) for v in n.inputs if hasattr(v,'default_value')]} for n in t.nodes},'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in t.links]}
 return {'materials':{m.name:tree(m.node_tree) for m in bpy.data.materials},'world':tree(bpy.context.scene.world.node_tree),'lights':{o.name:{'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shape':o.data.shape,'size':o.data.size} for o in bpy.context.scene.objects if o.type=='LIGHT'},'uv':{o.name:[[list(d.uv) for d in l.data] for l in o.data.uv_layers] for o in bpy.context.scene.objects if o.type=='MESH'}}

bpy.ops.wm.open_mainfile(filepath=str(O.parent/'keyring-hall-candidate-20261104/versions/R06/models/keyring-material.blend'));a=extra_state();used={m.name for o in bpy.context.scene.objects if o.type=='MESH' for m in o.data.materials if m}
bpy.ops.wm.open_mainfile(filepath=str(O.parent/'keyring-underbridge-r07-20261104/models/r07-material.blend'));b=extra_state()
out={'original_material_nodes_exact':all(b['materials'].get(n)==x for n,x in a['materials'].items()),'world_exact':a['world']==b['world'],'lights_exact':a['lights']==b['lights'],'original_uv_exact':all(b['uv'].get(n)==x for n,x in a['uv'].items())}
out['used_material_nodes_exact']=all(a['materials'][n]==b['materials'].get(n) for n in used)
out['original_used_material_names']=sorted(used)
out['changed_materials']={n:{'old':x,'new':b['materials'].get(n)} for n,x in a['materials'].items() if b['materials'].get(n)!=x}
(O/'extra-state.json').write_text(json.dumps(out,indent=2));print(out)
