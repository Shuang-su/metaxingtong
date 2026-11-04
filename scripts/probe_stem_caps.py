import bpy,pathlib,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/R11_support-diagnostic_material.blend'));heads=[]
for ob in bpy.context.scene.objects:
 if not ob.name.startswith('SMALL_FLOWERS_patch_') or ob.name.endswith('_inferred_stems'):continue
 vv=[ob.matrix_world@v.co for v in ob.data.vertices]
 for i,start in enumerate(range(0,len(vv),30)):
  points=vv[start:start+30];c=sum(points,Vector())/30;faces=[tuple(v-start for v in f.vertices) for f in ob.data.polygons if all(start<=v<start+30 for v in f.vertices)];heads.append((ob.name,i,c,BVHTree.FromPolygons(points,faces)))
results=[]
for radius,offset in [(.009,.012),(.006,0),(.003,-.002),(.003,-.004),(.003,-.006)]:
 rows=[]
 for name,i,c,head in heads:
  vs=[(c.x+r*math.cos(j*math.tau/8),c.y+r*math.sin(j*math.tau/8),z) for r,z in [(.009,4.485),(radius,c.z+offset)] for j in range(8)];fs=[(j,(j+1)%8,(j+1)%8+8,j+8) for j in range(8)]+[tuple(reversed(range(8))),tuple(8+j for j in range(8))];bt=BVHTree.FromPolygons(vs,fs)
  # sample upper cap points for any actual head surface overhead; not full cap coverage proof
  probes=[Vector((c.x,c.y,c.z+offset+.00001))]+[Vector(v)+Vector((0,0,.00001)) for v in vs[8:]];uncovered=sum(head.ray_cast(p,Vector((0,0,1)),.1)[0] is None for p in probes)
  rows.append({'patch':name,'head':i,'head_intersection':bool(bt.overlap(head)),'cap_upward_uncovered_probes':uncovered})
 results.append({'top_radius':radius,'top_offset':offset,'head_intersections':sum(x['head_intersection'] for x in rows),'uncovered_cap_probes':sum(x['cap_upward_uncovered_probes'] for x in rows),'total_cap_probes':len(rows)*9,'rows':rows})
(R/'qa/stem-cap-probes.json').write_text(json.dumps({'scope':'same existing heads; structural geometry diagnostic only, nine cap probes not complete visibility/physical/source acceptance','trials':results},indent=2));print([(x['top_radius'],x['top_offset'],x['head_intersections'],x['uncovered_cap_probes']) for x in results])
