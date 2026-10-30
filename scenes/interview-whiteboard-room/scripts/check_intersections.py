"""Surface-triangle intersection checks for furniture; preserve all pairs.
Within one assembled object many contacts intentionally overlap; cross-object collisions flagged.
"""
import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa/r05'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/r05/interview-room-material.blend'))
dep=bpy.context.evaluated_depsgraph_get();items=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.get('stable_id','').startswith(('BOARD','TABLE','CHAIR')):continue
 ev=o.evaluated_get(dep);me=ev.to_mesh();verts=[o.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons]
 tree=BVHTree.FromPolygons(verts,faces,epsilon=1e-7);lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 items.append((o.name,o['stable_id'],lo,hi,tree));ev.to_mesh_clear()
cross=[];assembly=[]
for i,a in enumerate(items):
 for b in items[i+1:]:
  if any(a[3][k]<b[2][k]-1e-7 or b[3][k]<a[2][k]-1e-7 for k in range(3)):continue
  overlaps=a[4].overlap(b[4])
  if overlaps:
   row={'a':a[1],'b':b[1],'triangle_pair_intersections':len(overlaps)}
   (assembly if a[1].split('-')[0]==b[1].split('-')[0] else cross).append(row)
r={'cross_furniture_intersections':cross,'same_assembly_contacts':assembly,
 'cross_furniture_pass':not cross,'limits':'Triangle surface intersection test; containment and all internal construction details not proven. Same assembly contacts require design review, not automatically errors.'}
(QA/'furniture-intersections.json').write_text(json.dumps(r,indent=2));print(json.dumps({'cross':cross,'assembly_contact_count':len(assembly)},indent=2))
