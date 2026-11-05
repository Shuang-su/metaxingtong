import bpy,json,hashlib
from pathlib import Path
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=Path(__file__).parent
exec((O.parent/'independent-backstage-pearl-r14-qa-20261105/restore.py').read_text().split('def snap():')[1].split("out={'script_sha'")[0].join(['def snap():','']))
def h(x):return hashlib.sha256(repr(x).encode()).hexdigest()
def extra():
 s=bpy.context.scene
 def val(p):
  v=p.default_value;return list(v) if hasattr(v,'__len__') else v
 def nodes(m):return {'nodes':[(n.name,n.bl_idname,[(p.name,val(p))for p in n.inputs if hasattr(p,'default_value')],getattr(getattr(n,'image',None),'name',None))for n in m.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in m.node_tree.links]}
 return {'mesh':{o.name:h(([list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons],[list(row)for row in o.matrix_world],[[list(x.uv)for x in u.data]for u in o.data.uv_layers],[m.name for m in o.data.materials],o.hide_render,o.hide_viewport))for o in s.objects if o.type=='MESH'},'materials':{m.name:nodes(m) for m in bpy.data.materials if m.use_nodes},'render':{'samples':s.cycles.samples,'denoise':s.cycles.use_denoising,'engine':s.render.engine,'film':s.render.film_transparent,'percentage':s.render.resolution_percentage,'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y]}}
out={}
for mode in ['material','white']:
 rows=[]
 for v in ['R04','R04D']:
  bpy.ops.wm.open_mainfile(filepath=str(P/f'models/{v}_{mode}.blend'));rows.append({'state':snap(),'extra':extra()})
 a,b=rows;out[mode]={'mesh_exact':a['extra']['mesh']==b['extra']['mesh'],'material_nodes_exact':a['extra']['materials']==b['extra']['materials'],'render_exact':a['extra']['render']==b['extra']['render'],'world_exact':a['state']['world']==b['state']['world'],'lights_exact':a['state']['lights']==b['state']['lights'],'old_source_cameras_exact':{n:a['state']['cameras'][n]==b['state']['cameras'][n] for n in a['state']['cameras']if n.startswith('SOURCE')},'changed_camera_names':[n for n in a['state']['cameras']if a['state']['cameras'][n]!=b['state']['cameras'][n]],'rows':rows}
(O/'diff.json').write_text(json.dumps(out,indent=2));print('DONE')
