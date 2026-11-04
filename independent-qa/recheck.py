import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).parent;R=Path('/workspace/scratch/fa58bfcf0425/keyring-keyheight-diagnostic-20261104');out={}
def mesh(o):return {'matrix':[list(x) for x in o.matrix_world],'verts':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'materials':[m.name for m in o.data.materials],'hide':[o.hide_render,o.hide_viewport]}
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def extra_state():
 def val(v):
  if isinstance(v,(str,int,float,bool)):return v
  try:return list(v)
  except:return str(v)
 def tree(t):
  if t is None:return None
  return {'nodes':{n.name:{'type':n.bl_idname,'inputs':[(v.name,val(v.default_value)) for v in n.inputs if hasattr(v,'default_value')]} for n in t.nodes},'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in t.links]}
 return {'materials':{m.name:tree(m.node_tree) for m in bpy.data.materials},'world':tree(bpy.context.scene.world.node_tree),'lights':{o.name:{'matrix':[list(r) for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'shape':o.data.shape,'size':o.data.size} for o in bpy.context.scene.objects if o.type=='LIGHT'},'uv':{o.name:[[list(d.uv) for d in l.data] for l in o.data.uv_layers] for o in bpy.context.scene.objects if o.type=='MESH'}}
for name,ratio in [('baseline',1.),('height060',.60),('height082',.82)]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/r06-material-frozen.blend'));s=bpy.context.scene;orig={o.name:mesh(o) for o in s.objects if o.type=='MESH'};cam0={o.name:(tuple(tuple(r) for r in o.matrix_world),o.data.lens,o.data.shift_x,o.data.shift_y) for o in s.objects if o.type=='CAMERA'};bottom=[];extra_before=extra_state()
 for o in s.objects:
  if o.name.startswith(('white-key-','black-key-')):
   z0=min(v.co.z for v in o.data.vertices);keep={v.index:o.matrix_world@v.co.copy() for v in o.data.vertices if abs(v.co.z-z0)<1e-7}
   for v in o.data.vertices:v.co.z=z0+(v.co.z-z0)*ratio
   bottom +=[(o.matrix_world@o.data.vertices[i].co-p).length for i,p in keep.items()]
 bpy.context.view_layer.update();new={o.name:mesh(o) for o in s.objects if o.type=='MESH'};d=json.loads((R/f'results/{name}/state.json').read_text());diffs=[]
 for src,rows in d['projected_geometry_boxes'].items():
  c=s.objects[f'source{src}-conditional']
  for row in rows:
   o=s.objects[row['id']];ps=[world_to_camera_view(s,c,o.matrix_world@v.co) for v in o.data.vertices];b=[min(p.x*1192 for p in ps),min((1-p.y)*671 for p in ps),max(p.x*1192 for p in ps),max((1-p.y)*671 for p in ps)];diffs +=[abs(x-y) for x,y in zip(b,row['bbox_xyxy'])]
 dg=bpy.context.evaluated_depsgraph_get();bv={}
 for o in s.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();bv[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True);e.to_mesh_clear()
 keynames=[n for n in bv if n.startswith(('white-key-','black-key-'))];contacts=[]
 for i,a in enumerate(keynames):
  for b in keynames[i+1:]+['key-pink-ring','stage-outer-floor']:
   pairs=bv[a].overlap(bv[b]);
   if pairs:contacts.append({'a':a,'b':b,'surface_triangle_pairs':len(pairs)})
 out[name]={'ratio':ratio,'materials_world_lights_uv_exact':extra_before==extra_state(),'before_digest_matches':digest(orig)==d['before_mesh_state_sha256'],'after_digest_matches':digest(new)==d['after_mesh_state_sha256'],'nonkey_unchanged_count':sum(orig[n]==new[n] for n in orig if not n.startswith(('white-key-','black-key-'))),'camera_exact':cam0=={o.name:(tuple(tuple(r) for r in o.matrix_world),o.data.lens,o.data.shift_x,o.data.shift_y) for o in s.objects if o.type=='CAMERA'},'bottom_point_count':len(bottom),'max_bottom_displacement':max(bottom),'all_192_box_projection_max_abs_error':max(diffs),'contact_edges':contacts}
 (O/'recheck.json').write_text(json.dumps(out,indent=2))
