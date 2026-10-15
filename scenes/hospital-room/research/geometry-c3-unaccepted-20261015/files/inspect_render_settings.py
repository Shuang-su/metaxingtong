import bpy,json
s=bpy.context.scene
print('DENOISE',s.cycles.use_denoising,s.cycles.denoiser,s.render.use_compositing,s.use_nodes)
if s.node_tree:
 for n in s.node_tree.nodes:print('NODE',n.name,n.type)
 for l in s.node_tree.links:print('LINK',l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)
for l in s.view_layers:print('LAYER',l.name,l.cycles.use_denoising)
for n in bpy.data.images:print('IMAGE',n.name,n.source,'packed',bool(n.packed_file),'path',n.filepath)
