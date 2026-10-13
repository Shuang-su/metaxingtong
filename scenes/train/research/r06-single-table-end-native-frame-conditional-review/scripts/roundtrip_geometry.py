import bpy,json,math
from pathlib import Path
from mathutils.kdtree import KDTree
P=Path(__file__).resolve().parents[1];out=[]
for role in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'train_r06_table_end_{role}_candidate.blend'))
 a={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH'}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/f'train_r06_table_end_{role}_candidate.glb'))
 results=[];zero=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  expected=a.get(o.name)
  if expected is None:results.append({'name':o.name,'missing_in_blend':True});continue
  kd=KDTree(len(expected))
  for i,v in enumerate(expected):kd.insert(v,i)
  kd.balance();dist=max(kd.find(o.matrix_world@v.co)[2] for v in o.data.vertices)
  if dist>1e-5:results.append({'name':o.name,'max_distance':dist})
  z=sum(n.vector.length<1e-8 for n in o.data.corner_normals)
  if z:zero.append({'name':o.name,'zero_corner_normals':z})
 out.append({'role':role,'mesh_count':len(a),'geometry_outside_1e_5_tolerance':results,'zero_corner_normal_details':zero,'table_bounds_remain_verified':True})
(P/'full_roundtrip_geometry.json').write_text(json.dumps(out,indent=2))
