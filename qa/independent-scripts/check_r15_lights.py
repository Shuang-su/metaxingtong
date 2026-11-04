import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/forest-diagnostic-replay-20261104');out={}
def nodes(tree):
 return {'nodes':[{ 'name':n.name,'type':n.bl_idname,'values':{x.name:(list(x.default_value) if hasattr(x.default_value,'__len__') and not isinstance(x.default_value,str) else x.default_value) for x in n.inputs if hasattr(x,'default_value') and isinstance(x.default_value,(int,float,str)) or hasattr(x,'default_value') and hasattr(x.default_value,'__len__') and not isinstance(x.default_value,bpy.types.ID)}} for n in tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in tree.links]} if tree else None
for rev in ['R14_anchor-diagnostic','R15_log-contact-diagnostic']:
 for mode in ['material','white']:
  bpy.ops.wm.open_mainfile(filepath=str(R/f'models/{rev}_{mode}.blend'));s=bpy.context.scene
  out[rev+'_'+mode]={'lights':{o.name:{'matrix':[list(x)for x in o.matrix_world],'type':o.data.type,'color':list(o.data.color),'energy':o.data.energy,'size':getattr(o.data,'size',None),'nodes':nodes(o.data.node_tree)}for o in s.objects if o.type=='LIGHT'},'world':nodes(s.world.node_tree),'camera':{o.name:{'matrix':[list(x)for x in o.matrix_world],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'sensor':[o.data.sensor_width,o.data.sensor_height,o.data.sensor_fit]}for o in s.objects if o.type=='CAMERA'}}
result={'data':out,'material_unchanged':out['R14_anchor-diagnostic_material']==out['R15_log-contact-diagnostic_material'],'white_unchanged':out['R14_anchor-diagnostic_white']==out['R15_log-contact-diagnostic_white']}
Path('/workspace/scratch/fa58bfcf0425/independent-forest-replay-qa-20261104/R15-light-world-camera-check.json').write_text(json.dumps(result,indent=2));print(result['material_unchanged'],result['white_unchanged'])
