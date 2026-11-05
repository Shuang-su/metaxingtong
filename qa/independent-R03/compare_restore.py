import bpy,json
from pathlib import Path
O=Path(__file__).parent;P=O.parent/"butterfly-finite-stage-20261105"
def snap():
 s=bpy.context.scene;w=s.world
 return {'world':{'color':list(w.color),'use_nodes':w.use_nodes,'nodes':[(n.name,n.bl_idname,[(p.name,list(p.default_value) if hasattr(p.default_value,'__len__') else p.default_value) for p in n.inputs if hasattr(p,'default_value')]) for n in w.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in w.node_tree.links]},'lights':{o.name:{'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shape':o.data.shape,'size':o.data.size,'size_y':o.data.size_y} for o in s.objects if o.type=='LIGHT'},'cameras':{o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens,'frame':[list(v.normalized()) for v in o.data.view_frame(scene=s)],'sensor_fit':o.data.sensor_fit,'clip':[o.data.clip_start,o.data.clip_end]} for o in s.objects if o.type=='CAMERA'},'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'active':s.camera.name if s.camera else None,'view':{k:getattr(s.view_settings,k) for k in ['view_transform','look','exposure','gamma']},'meshes':sum(o.type=='MESH' for o in s.objects)}

out={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'models/R03_{mode}.blend'));a=snap()
 bpy.ops.wm.open_mainfile(filepath=str(O/f'restored/R03_{mode}_restored.blend'));b=snap();out[mode]={'old':a,'restored':b}
(O/'restore-comparison-raw.json').write_text(json.dumps(out,indent=2))
