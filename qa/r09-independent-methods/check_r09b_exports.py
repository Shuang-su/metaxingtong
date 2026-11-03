import bpy,bmesh,json,hashlib,sys,math
from pathlib import Path
from mathutils.kdtree import KDTree
D=Path('/workspace/scratch/fa58bfcf0425/cityroom-refinement-20261103/models');O=Path('/workspace/scratch/fa58bfcf0425/cityroom-independent-refinement-qa-20261103')
def snapshot(p):
 if p.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(p))
 else:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
 result={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  world=[tuple(o.matrix_world@v.co) for v in o.data.vertices]
  faces=[tuple(f.vertices) for f in o.data.polygons]
  data=json.dumps([world,faces],separators=(',',':')).encode()
  bm=bmesh.new();bm.from_mesh(o.data)
  result[o.name]={'world':world,'shape_hash':hashlib.sha256(data).hexdigest(),'vertices':len(world),'faces':len(faces),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'boundary':sum(e.is_boundary for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'materials':[m.name if m else None for m in o.data.materials]};bm.free()
 cams={o.name:{'location':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens} for o in bpy.context.scene.objects if o.type=='CAMERA'}
 return result,cams
allr={};payload={}
for name in ['R09b_material.blend','R09b_white.blend','R09b_material.glb','R09b_white.glb']:
 p=D/name;allr[name]=snapshot(p);payload[name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mesh_count':len(allr[name][0]),'cameras':allr[name][1],'objects':{n:{k:v for k,v in r.items() if k!='world'} for n,r in allr[name][0].items()}}
a=allr['R09b_material.blend'][0];b=allr['R09b_white.blend'][0]
comparisons={'material_white_same_names':set(a)==set(b),'material_white_different_geometry':[n for n in a if n not in b or a[n]['shape_hash']!=b[n]['shape_hash']],'camera_equal':allr['R09b_material.blend'][1]==allr['R09b_white.blend'][1]}
for suffix in ['material','white']:
 a=allr[f'R09b_{suffix}.blend'][0];b=allr[f'R09b_{suffix}.glb'][0];rs=[]
 for n in a:
  if n not in b:rs.append({'name':n,'missing':True});continue
  def dist(A,B):
   k=KDTree(len(A))
   for i,v in enumerate(A):k.insert(v,i)
   k.balance();return max((k.find(v)[2] for v in B),default=0)
  d=max(dist(a[n]['world'],b[n]['world']),dist(b[n]['world'],a[n]['world']))
  rs.append({'name':n,'max_bidirectional_vertex_distance':d,'blend_vertices':a[n]['vertices'],'glb_vertices':b[n]['vertices'],'glb_degenerate_faces':b[n]['degenerate']})
 comparisons[suffix+'_glb']={'missing':sorted(set(a)-set(b)),'extra':sorted(set(b)-set(a)),'max_distance':max((r.get('max_bidirectional_vertex_distance',0) for r in rs),default=0),'objects':rs}
(O/'R09b-independent-model-check.json').write_text(json.dumps({'files':payload,'comparisons':comparisons,'limits':'Read-only coordinate/topology export check, not source fidelity or full intersection proof.'},indent=2))
print(json.dumps({k:v for k,v in comparisons.items() if not k.endswith('_glb')}));print([(k,v['max_distance'],v['missing'],v['extra']) for k,v in comparisons.items() if k.endswith('_glb')])
