import bpy,json,pathlib,hashlib,numpy as np
from mathutils import Euler,Vector,Matrix
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/cyber-roof-stage-20261105');Q=pathlib.Path(__file__).parent

def sig(m):
 if not m:return None
 return {'nodes':sorted((n.bl_idname,tuple((i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value)for i in n.inputs if hasattr(i,'default_value')))for n in m.node_tree.nodes),'links':sorted((l.from_node.bl_idname,l.from_socket.name,l.to_node.bl_idname,l.to_socket.name)for l in m.node_tree.links)}
states={}
for stage in ['r04','r05']:
 for mode in ['','-white']:
  bpy.ops.wm.open_mainfile(filepath=str(P/f'models/roof-{stage}{mode}.blend'));s=bpy.context.scene
  states[stage+mode]={'mats':{o.name:[sig(m)for m in o.data.materials]for o in s.objects if o.type=='MESH'},'world':sig(s.world),'cam':{o.name:[list(r)for r in o.matrix_world]for o in s.objects if o.type=='CAMERA'}}

a=states['r04'];b=states['r05'];out={'material_nodes_same':a['mats']==b['mats'],'white_nodes_same':states['r04-white']['mats']==states['r05-white']['mats'],'World_same':a['world']==b['world'],'old_ten_cameras_same':all(a['cam'][n]==b['cam'][n]for n in a['cam']),'new_camera_names':list(b['cam'].keys()-a['cam'].keys())}
(Q/'reuse.json').write_text(json.dumps(out,indent=2));print('DONE')
