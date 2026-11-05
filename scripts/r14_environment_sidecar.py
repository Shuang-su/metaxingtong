import bpy,json,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
def val(v):
 if isinstance(v,(str,int,float,bool)):return v
 try:return list(v)
 except:return str(v)
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R14_{mode}.blend'));s=bpy.context.scene;w=s.world
 data={'world':{'name':w.name,'use_nodes':w.use_nodes,'color':list(w.color),'nodes':[{'name':n.name,'bl_idname':n.bl_idname,'inputs':{p.name:val(p.default_value) for p in n.inputs if hasattr(p,'default_value')},'location':list(n.location)} for n in w.node_tree.nodes],'links':[{'from_node':l.from_node.name,'from_socket':l.from_socket.name,'to_node':l.to_node.name,'to_socket':l.to_socket.name}for l in w.node_tree.links]},'lights':{o.name:{'matrix_world':[list(r)for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shape':getattr(o.data,'shape',None),'size':getattr(o.data,'size',None),'size_y':getattr(o.data,'size_y',None)}for o in s.objects if o.type=='LIGHT'},'view_settings':{k:val(getattr(s.view_settings,k)) for k in ['view_transform','look','exposure','gamma']},'render_resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage]};(P/'qa'/f'R14_{mode}_environment_restore.json').write_text(json.dumps(data,indent=2))
