import bpy,json,pathlib,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=pathlib.Path(__file__).resolve().parent
p=D.parent/'forest-diagnostic-replay-20261104/models/R14_anchor-diagnostic_material.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[x.vertices[:] for x in o.data.polygons])
t=bpy.data.objects['TERRAIN_finite_working_domain']; bt=tree(t); trunk=tree(bpy.data.objects['TREE_main_trunk']); rows=[]
for name in ['TREE_main_buttress_02','LOG_left_fallen']:
 o=bpy.data.objects[name];vs=[o.matrix_world@v.co for v in o.data.vertices]; r=[]
 for i,v in enumerate(vs):
  a=bt.ray_cast(Vector((v.x,v.y,100)),Vector((0,0,-1)),200)[0]; b=bt.ray_cast(Vector((v.x,v.y,-100)),Vector((0,0,1)),200)[0]
  near=trunk.find_nearest(v)
  r.append({'index':i,'world':list(v),'terrain_top':None if a is None else a.z,'terrain_bottom':None if b is None else b.z,'above_top':None if a is None else v.z-a.z,'inside_vertical_terrain_interval':a is not None and b is not None and b.z<=v.z<=a.z,'distance_to_main_trunk_surface':near[3]})
 rows.append({'object':name,'vertices':r,'terrain_surface_pairs':len(tree(o).overlap(bt)),'main_trunk_surface_pairs':len(tree(o).overlap(trunk))})
out={'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'Every existing world vertex, bidirectional vertical rays to finite terrain, nearest main trunk surface; no mutation','limits':['Vertex tests do not classify entire volume or all support footprint','Nearest vertex to surface minimum is not exact mesh-mesh distance','Terrain and object positions remain inferred, not source geometry'],'objects':rows};(D/'remaining-support-check.json').write_text(json.dumps(out,indent=2));
for r in rows:
 print(r['object'],len(r['vertices']),'inside',sum(v['inside_vertical_terrain_interval'] for v in r['vertices']),'min_gap',min(v['above_top'] for v in r['vertices'] if v['above_top'] is not None),'nearest_trunk_vertex',min(v['distance_to_main_trunk_surface'] for v in r['vertices']))
