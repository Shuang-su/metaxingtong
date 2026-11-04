import bpy,pathlib,json,re
from mathutils.bvhtree import BVHTree
from mathutils import Vector
OUT=pathlib.Path(__file__).resolve().parent;model='/workspace/scratch/fa58bfcf0425/forest-diagnostic-replay-20261104/models/R13_root-diagnostic_material.blend';bpy.ops.wm.open_mainfile(filepath=model);s=bpy.context.scene
cache={}
def tree(o):
 if o.name not in cache:cache[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
 return cache[o.name]
def bounds(o):
 v=[o.matrix_world@Vector(c) for c in o.bound_box];return [(min(x[i] for x in v),max(x[i] for x in v)) for i in range(3)]
bb={o.name:bounds(o) for o in s.objects if o.type=='MESH'};out=[]
for name in ['TREE_main_buttress_02','LOG_left_fallen','TREE_background_03']:
 ob=bpy.data.objects[name];hits=[]
 for other in s.objects:
  if other.type!='MESH' or other==ob:continue
  if any(bb[name][i][1]<bb[other.name][i][0] or bb[other.name][i][1]<bb[name][i][0] for i in range(3)):continue
  pairs=tree(ob).overlap(tree(other))
  if pairs:hits.append({'object':other.name,'surface_intersection_pairs':len(pairs)})
 out.append({'object':name,'actual_overlaps':hits})
ob=bpy.data.objects['TREE_background_03'];terrain=bpy.data.objects['TERRAIN_finite_working_domain'];rows=[]
for i in range(12):
 v=ob.matrix_world@ob.data.vertices[i].co;loc,no,index,d=tree(terrain).ray_cast(Vector((v.x,v.y,100)),Vector((0,0,-1)),200);rows.append({'index':i,'world':list(v),'terrain_z':loc.z if loc is not None else None,'vertical_gap':v.z-loc.z if loc is not None else None})
(OUT/'support-relations.json').write_text(json.dumps({'scope':'actual mesh surface overlap against all AABB-overlapping current scene meshes; foliage overlap is not a physically meaningful load path; first12 tree vertices bound to original tube recipe','relations':out,'tree03_base_ring':rows},indent=2));print([(x['object'],[(y['object'],y['surface_intersection_pairs']) for y in x['actual_overlaps']]) for x in out]);print('tree ring gaps',[r['vertical_gap'] for r in rows])
