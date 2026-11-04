import bpy,json,pathlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104/models');Q=P.parents[1]/'independent-observatory-qa-20261104'
def val(v):
 if isinstance(v,(str,int,float,bool)):return v
 try:return list(v)
 except:return str(v)
R={}
for mode in ['material','white']:
 for v in ['R06','R07']:
  bpy.ops.wm.open_mainfile(filepath=str(P/f'{v}_{mode}.blend'));w=bpy.context.scene.world;n=w.node_tree;R[v+'_'+mode]={'world':w.name,'color':list(w.color),'use_nodes':w.use_nodes,'nodes':{x.name:{'type':x.bl_idname,'inputs':{s.name:val(s.default_value) for s in x.inputs if hasattr(s,'default_value')}} for x in n.nodes},'links':[(x.from_node.name,x.from_socket.name,x.to_node.name,x.to_socket.name) for x in n.links]}
R['same_per_variant']={m:R['R06_'+m]==R['R07_'+m] for m in ['material','white']};(Q/'R07-world-check.json').write_text(json.dumps(R,indent=2));print(R['same_per_variant'])
