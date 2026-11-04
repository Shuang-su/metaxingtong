import bpy,pathlib,json
from mathutils.bvhtree import BVHTree
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/R12_support-diagnostic_material.blend'));ob=bpy.data.objects['ISLAND_turf_blades_procedural'];bed=bpy.data.objects['ISLAND_moss_bedding_inferred'];vs=[ob.matrix_world@v.co for v in ob.data.vertices];bt=BVHTree.FromPolygons([bed.matrix_world@v.co for v in bed.data.vertices],[p.vertices[:] for p in bed.data.polygons]);groups=[[] for _ in range(len(vs)//6)]
for f in ob.data.polygons:
 group=f.vertices[0]//6
 if any(i//6!=group for i in f.vertices):raise RuntimeError('unexpected leaf group')
 groups[group].append(tuple(i-group*6 for i in f.vertices))
rows=[]
for i in range(len(groups)):
 leaf=vs[i*6:i*6+6];low=min(range(6),key=lambda k:leaf[k].z);base=leaf[low];tree=BVHTree.FromPolygons(leaf,groups[i]);hit,norm,index,dist=bt.ray_cast(base+Vector((0,0,.001)),Vector((0,0,-1)),2)
 rows.append({'leaf':i,'base_vertex':i*6+low,'original_world_base':list(base),'surface_intersects_bed':bool(tree.overlap(bt)),'bed_below':hit is not None,'bed_z':hit.z if hit is not None else None,'vertical_gap':base.z-hit.z if hit is not None else None,'actual_faces':len(groups[i])})
(R/'qa/grass-base-check.json').write_text(json.dumps({'model':'models/R12_support-diagnostic_material.blend','scope':'actual individual six-vertex grass meshes and actual bed surfaces, representative downward basal ray; not source root observation or full environmental contact','leaves':rows},indent=2));print('leaves',len(rows),'intersect',sum(r['surface_intersects_bed'] for r in rows),'clear_gap',sum(r['bed_below'] and r['vertical_gap']>.0001 and not r['surface_intersects_bed'] for r in rows),'no_bed',sum(not r['bed_below'] for r in rows))
