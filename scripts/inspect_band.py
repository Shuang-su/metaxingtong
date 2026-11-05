import bpy,json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent.parent
sources={'R05':P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend','a055':P.parent/'cyber-roof-paired-shell-study-20261105/export/roof-paired-a055.blend'};out={}
for label,path in sources.items():
 bpy.ops.wm.open_mainfile(filepath=str(path));rows=[]
 for o in bpy.context.scene.objects:
  if not o.name.startswith('STAGE_'):continue
  m=o.data;vs=[list(o.matrix_world@v.co) for v in m.vertices];rs=[math.hypot(v[0],v[1]) for v in vs];mats=[]
  for mat in m.materials:
   nodes=[]
   for n in mat.node_tree.nodes:
    ins={}
    for i in n.inputs:
     if hasattr(i,'default_value'):
      v=i.default_value
      try:v=list(v)
      except TypeError:pass
      if isinstance(v,(str,float,int,bool,list)):ins[i.name]=v
    nodes.append({'name':n.name,'type':n.type,'inputs':ins})
   mats.append({'name':mat.name,'nodes':nodes,'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in mat.node_tree.links]})
  faces=[]
  for f in m.polygons:
   zz=[vs[i][2] for i in f.vertices];rr=[rs[i] for i in f.vertices];faces.append({'index':f.index,'vertices':list(f.vertices),'z_minmax':[min(zz),max(zz)],'r_minmax':[min(rr),max(rr)],'material_index':f.material_index})
  projection={}
  if 'LED front' in o.name:
   from bpy_extras.object_utils import world_to_camera_view
   from mathutils import Vector
   for cam in ['SOURCE11 conditional camera','SOURCE10 auxiliary different state']:
    pp=[world_to_camera_view(bpy.context.scene,bpy.data.objects[cam],Vector(v)) for v in vs if v[1]<0]
    projection[cam]={'front_half_vertex_pixel_bounds':[[min(p.x for p in pp)*1192,max(p.x for p in pp)*1192],[(1-max(p.y for p in pp))*671,(1-min(p.y for p in pp))*671]],'vertices_in_frame':sum(0<=p.x<=1 and 0<=p.y<=1 and p.z>0 for p in pp),'front_half_vertices':len(pp)}
  geo={'vertices':vs,'faces':[list(f.vertices) for f in m.polygons],'matrix':[list(r) for r in o.matrix_world]}
  rows.append({'name':o.name,'vertices':len(vs),'faces':len(m.polygons),'radius_minmax':[min(rs),max(rs)],'z_minmax':[min(v[2] for v in vs),max(v[2] for v in vs)],'uv_layers':[{'name':u.name,'loops':len(u.data),'range':[[min(x.uv[k] for x in u.data),max(x.uv[k] for x in u.data)] for k in [0,1]]} for u in m.uv_layers],'projection':projection,'geometry_sha256':hashlib.sha256(json.dumps(geo,sort_keys=True).encode()).hexdigest(),'materials':mats,'face_groups':faces})
 out[label]={'input':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':rows}
a={r['name']:r for r in out['R05']['objects']};b={r['name']:r for r in out['a055']['objects']};out['stage_objects_exact_equal']=a==b
(P/'results/band-inventory.json').write_text(json.dumps(out,indent=2));print('same stage objects',out['stage_objects_exact_equal'])
for r in a.values():print(r['name'],r['radius_minmax'],r['z_minmax'],'uv',r['uv_layers'],'mat',[m['name'] for m in r['materials']])
