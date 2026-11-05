import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path('/workspace/scratch/fa58bfcf0425');Q=Path(__file__).parent

def node(m):
 if not m or not m.use_nodes:return None
 return {'nodes':[(n.name,n.bl_idname,[(i.name, str(i.default_value[:]) if hasattr(i.default_value,'__len__') else str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes], 'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in m.node_tree.links]}
def snap():
 s=bpy.context.scene
 return {'meshes':{o.name:{'v':[tuple(o.matrix_world@v.co)for v in o.data.vertices],'p':[tuple(p.vertices)for p in o.data.polygons],'uv':[tuple(x.uv)for x in o.data.uv_layers.active.data]if o.data.uv_layers.active else None,'vis':[o.hide_render,o.hide_viewport],'materials':[node(m)for m in o.data.materials]}for o in s.objects if o.type=='MESH'},'cams':{o.name:[list(sum((tuple(r)for r in o.matrix_world),())),o.data.lens,o.data.sensor_fit]for o in s.objects if o.type=='CAMERA'},'lights':{o.name:[list(sum((tuple(r)for r in o.matrix_world),())),o.data.type,o.data.energy,list(o.data.color),o.data.size]for o in s.objects if o.type=='LIGHT'},'world':node(s.world)}
bpy.ops.wm.open_mainfile(filepath=str(P/'independent-seaside-wing-r04-qa-20261105/frozen/models/material.blend'));a=snap()
bpy.ops.wm.open_mainfile(filepath=str(P/'independent-seaside-wing-r05-qa-20261105/frozen/models/material.blend'));b=snap();R={'removed':list(a['meshes'].keys()-b['meshes'].keys()),'added':list(b['meshes'].keys()-a['meshes'].keys()),'common_exact':{n:a['meshes'][n]==b['meshes'][n]for n in a['meshes'].keys()&b['meshes'].keys()},'cameras_exact':a['cams']==b['cams'],'lights_exact':a['lights']==b['lights'],'world_exact':a['world']==b['world']}

(Q/'material-world-diff.json').write_text(json.dumps(R,indent=2));print('DONE')
