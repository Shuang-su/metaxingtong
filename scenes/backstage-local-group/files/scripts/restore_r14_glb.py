"""Fresh-scene import and explicit sidecar restoration; no automatic save/render."""
import bpy,json,pathlib
from mathutils import Matrix
P=pathlib.Path(__file__).resolve().parents[1]
def restore(mode='material'):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(P/'models'/f'R14_{mode}.glb'))
 s=bpy.context.scene;cams=json.loads((P/'qa'/f'R14_{mode}_camera_restore.json').read_text());env=json.loads((P/'qa'/f'R14_{mode}_environment_restore.json').read_text())
 s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=cams['resolution'];s.render.pixel_aspect_x,s.render.pixel_aspect_y=cams['pixel_aspect']
 for name,v in cams['cameras'].items():
  o=bpy.data.objects.get(name)
  if o is None:o=bpy.data.objects.new(name,bpy.data.cameras.new(name));s.collection.objects.link(o)
  assert o.type=='CAMERA';o.matrix_world=Matrix(v['matrix_world'])
  for k,x in v.items():
   if k!='matrix_world':setattr(o.data,k,x)
 s.camera=bpy.data.objects.get(cams['active_camera'])
 wd=env['world'];w=bpy.data.worlds.new(wd['name']);s.world=w;w.use_nodes=True;w.node_tree.nodes.clear()
 for x in wd['nodes']:
  n=w.node_tree.nodes.new(x['bl_idname']);n.name=x['name'];n.location=x['location']
  for key,value in x['inputs'].items():
   socket=n.inputs.get(key)
   if socket is None:
    if n.bl_idname=='ShaderNodeBackground' and key=='Weight' and value==0.0:
     print('Explicit compatibility exception: absent hidden Background Weight socket, source value zero; Color and Strength restored.')
     continue
    raise KeyError('Required world socket missing: '+n.name+'/'+key)
   socket.default_value=value
 for l in wd['links']:w.node_tree.links.new(w.node_tree.nodes[l['from_node']].outputs[l['from_socket']],w.node_tree.nodes[l['to_node']].inputs[l['to_socket']])
 w.color=wd['color'];w.use_nodes=wd['use_nodes']
 for name,x in env['lights'].items():
  o=bpy.data.objects.get(name)
  if o is None:o=bpy.data.objects.new(name,bpy.data.lights.new(name,x['type']));s.collection.objects.link(o)
  assert o.type=='LIGHT';o.matrix_world=Matrix(x['matrix_world'])
  for k in ['type','energy','color','shape','size','size_y']:
   if x[k] is not None and hasattr(o.data,k):setattr(o.data,k,x[k])
 for k,v in env['view_settings'].items():setattr(s.view_settings,k,v)
 bpy.context.view_layer.update();return s
if __name__=='__main__':
 import sys
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];restore(args[0] if args else 'material');print('R14 GLB restored in memory, no save.')
