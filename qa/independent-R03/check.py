import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils.kdtree import KDTree
P=Path('/workspace/scratch/fa58bfcf0425/butterfly-finite-stage-20261105');O=Path(__file__).parent
R={};states={}
def h(x):return hashlib.sha256(repr(x).encode()).hexdigest()
def state():
 s=bpy.context.scene;mes={};audit={}
 for o in s.objects:
  if o.type!='MESH':continue
  d=o.data;d.calc_loop_triangles();vs=[tuple(o.matrix_world@v.co)for v in d.vertices];ts=[tuple(t.vertices)for t in d.loop_triangles];bm=bmesh.new();bm.from_mesh(d)
  audit[o.name]={'vertices':len(vs),'triangles':len(ts),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_edges':sum(not e.link_faces for e in bm.edges),'degenerate_triangles':sum(t.area<1e-12 for t in d.loop_triangles),'signed_volume':bm.calc_volume(signed=True)};bm.free()
  mes[o.name]={'vertices':vs,'surface':h(sorted(tuple(sorted(vs[i]for i in t))for t in ts)),'uv':h([tuple(x.uv)for x in d.uv_layers.active.data])if d.uv_layers.active else None,'visibility':[o.hide_render,o.hide_viewport]}
 cams={o.name:{'matrix':[list(r)for r in o.matrix_world],'frame':[tuple(v.normalized())for v in o.data.view_frame(scene=s)]}for o in s.objects if o.type=='CAMERA'}
 return mes,cams,audit
for mode in ['material','white']:
 f=P/f'models/R03_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));a,c,audit=state();states[mode]=(a,c);g=P/f'models/R03_{mode}.glb';bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(g));s=bpy.context.scene;s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;b,cc,_=state()
 def nearest(v,w):
  k=KDTree(len(w))
  for i,p in enumerate(w):k.insert(p,i)
  k.balance();return max(k.find(p)[2]for p in v)
 R[mode]={'blend_sha':hashlib.sha256(f.read_bytes()).hexdigest(),'glb_sha':hashlib.sha256(g.read_bytes()).hexdigest(),'audit':audit,'counts':[len(a),len(b),len(c),len(cc)],'missing':list(a.keys()-b.keys()),'vertex_error':{n:max(nearest(a[n]['vertices'],b[n]['vertices']),nearest(b[n]['vertices'],a[n]['vertices']))for n in a.keys()&b.keys()},'camera_frame_error':{n:max(abs(c[n]['frame'][i][j]-cc[n]['frame'][i][j])for i in range(4)for j in range(3))for n in c.keys()&cc.keys()},'camera_matrix_error':{n:max(abs(c[n]['matrix'][i][j]-cc[n]['matrix'][i][j])for i in range(4)for j in range(4))for n in c.keys()&cc.keys()}}
 (O/'check.json').write_text(json.dumps(R,indent=2))
a,c=states['material'];b,d=states['white'];R['shared']={'mesh_names':a.keys()==b.keys(),'objects':{n:{k:a[n][k]==b[n][k]for k in ['surface','uv','visibility']}for n in a.keys()&b.keys()},'cameras':c==d};(O/'check.json').write_text(json.dumps(R,indent=2));print('DONE')
