import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/'stage-03-contact-qa';Q=D/'qa'
bpy.ops.wm.open_mainfile(filepath=str(D/'campus-courtyard_material.blend'));s=bpy.context.scene
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
g=json.loads((Q/'material_geometry.json').read_text());geometry={k:v['geometry_sha256'] for k,v in sorted(g.items())}
def value(v):
    if isinstance(v,(str,int,float,bool)):return v
    try:return list(v)
    except:return str(v)
materials={}
for m in sorted(bpy.data.materials,key=lambda m:m.name):
 nodes=[]
 if m.use_nodes:
  for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
   node={'name':n.name,'type':n.type,'inputs':{p.name:value(p.default_value) for p in n.inputs if hasattr(p,'default_value')}}
   if n.type=='TEX_IMAGE' and n.image:node['image']={'name':n.image.name,'size':list(n.image.size),'packed':bool(n.image.packed_file)}
   nodes.append(node)
 materials[m.name]={'diffuse_color':list(m.diffuse_color),'nodes':nodes,'links':sorted([f'{l.from_node.name}:{l.from_socket.name}->{l.to_node.name}:{l.to_socket.name}' for l in m.node_tree.links]) if m.use_nodes else []}
assignment={o.name:{'slots':[m.name if m else None for m in o.data.materials],'indices_sha256':sha([p.material_index for p in o.data.polygons])} for o in s.objects if o.type=='MESH'}
lighting={'world_background_color':list(s.world.node_tree.nodes['Background'].inputs[0].default_value),'world_strength':s.world.node_tree.nodes['Background'].inputs[1].default_value,'lights':{o.name:{'type':o.data.type,'matrix':[list(r) for r in o.matrix_world],'energy':o.data.energy,'color':list(o.data.color),'angle':getattr(o.data,'angle',None)} for o in s.objects if o.type=='LIGHT'},'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma}
visibility={o.name:[o.hide_render,o.hide_viewport] for o in s.objects}
cameras={o.name:{'matrix':[list(r) for r in o.matrix_world],'lens_mm':o.data.lens,'sensor_width_mm':o.data.sensor_width,'sensor_fit':o.data.sensor_fit,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y} for o in s.objects if o.type=='CAMERA' and o.name.startswith('SRC')}
source=json.loads((R/'source/acquisition.json').read_text())
result={'status':'frozen four-source candidate; later independent reverse frame NOT received or used','geometry_sha256':sha(geometry),'material_nodes_sha256':sha(materials),'material_assignments_sha256':sha(assignment),'lighting_sha256':sha(lighting),'visibility_sha256':sha(visibility),'source_cameras_sha256':sha(cameras),'mesh_geometry_hashes':geometry,'material_nodes':materials,'material_assignments':assignment,'lighting':lighting,'visibility':visibility,'source_cameras':cameras,'source_inputs':{f['id']:f['sha256'] for f in source['frames']},'invariants':['same world geometry/material/light/visibility across all four source views','no camera-dependent object hide or shape changes','no source-image texture projection or image warp','arbitrary model units; character excluded as a scale reference','window/facade and track geometry unchanged in this stage','original source cameras retained; camera-only fit trials rejected','new reverse frame must first get only a new camera; held-out relation baseline before any geometry update']}
(Q/'frozen_invariants.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k.endswith('sha256')},indent=2))
