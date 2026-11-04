import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def capture():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  vs=[tuple(o.matrix_world@v.co) for v in o.data.vertices];out[o.name]={'vertices':len(vs),'polygons':len(o.data.polygons),'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'mesh_hash':hashlib.sha256(str(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()}
 return out
bpy.ops.wm.open_mainfile(filepath=str(R/'models/phone-material.blend'));a=capture();objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bvh={o.name:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in objs};pairs=[]
for i,o in enumerate(objs):
 for p in objs[i+1:]:
  n=len(bvh[o.name].overlap(bvh[p.name]));
  if n:pairs.append({'objects':[o.name,p.name],'triangle_overlap_pairs':n})
bpy.ops.wm.open_mainfile(filepath=str(R/'models/phone-white.blend'));w=capture();same={k:a[k]['mesh_hash']==w[k]['mesh_hash'] and a[k]['bounds']==w[k]['bounds'] for k in a}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'models/phone-material.glb'));g=capture()
errs={k:max(abs(a[k]['bounds'][j][i]-g[k]['bounds'][j][i]) for j in range(2) for i in range(3)) for k in a if k in g}
json.dump({'blend_material':a,'blend_white':w,'shared_geometry_exact':same,'glb_reimport':g,'glb_bbox_error_model_units':errs,'source_vs_glb_object_count':[len(a),len(g)],'surface_intersection_candidates':pairs,'contact_limit':'BVH triangle intersections are proxy attachment checks only, not watertight assembly or structural proof; intentional layered finish/rim intersections retained. No ground/contact inferred from obscured source.'},open(R/'qa/reimport-and-contact.json','w'),indent=2)
