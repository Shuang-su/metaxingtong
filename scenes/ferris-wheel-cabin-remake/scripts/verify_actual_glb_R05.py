import bpy,bmesh,json,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
R=Path(__file__).resolve().parents[1];results=[]
for mode in ['material','white']:
 bpy.ops.wm.read_factory_settings(use_empty=True);p=R/f'models/ferris_remake_R05_{mode}.glb';bpy.ops.import_scene.gltf(filepath=str(p));obs=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  m=o.data;world=[o.matrix_world@v.co for v in m.vertices];volume=0.;directed=Counter();face_normals=0
  # glTF exporter splits normal/material seams: geometric-position identity for edge winding audit.
  keys=[tuple(round(c,6) for c in v) for v in world]
  for poly in m.polygons:
   ids=list(poly.vertices)
   for i in range(1,len(ids)-1):
    a,b,c=[world[j] for j in [ids[0],ids[i],ids[i+1]]];volume+=a.dot(b.cross(c))/6
   for a,b in zip(ids,ids[1:]+ids[:1]):directed[(keys[a],keys[b])]+=1
  undirected=Counter()
  for (a,b),n in directed.items():undirected[tuple(sorted((a,b)))]+=n
  obs.append({'object':o.name,'signed_world_volume':volume,'seam_weld_1e-6_boundary_edges':sum(n==1 for n in undirected.values()),'seam_weld_non2face_edges':sum(n!=2 for n in undirected.values()),'same_direction_edges':sum(n>1 for n in directed.values()),'materials':[ma.name for ma in m.materials]})
 results.append({'mode':mode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mesh_count':len(obs),'nonpositive_volume':sum(o['signed_world_volume']<=0 for o in obs),'objects':obs,'limits':'Position-weld quantization1e-6 for normal-seam duplicate vertices; not proof of full assembly manifold or source truth'})
(R/'qa/fresh-GLB-oriented-solids-R05.json').write_text(json.dumps(results,indent=2));print([(r['mode'],r['mesh_count'],r['nonpositive_volume']) for r in results])
