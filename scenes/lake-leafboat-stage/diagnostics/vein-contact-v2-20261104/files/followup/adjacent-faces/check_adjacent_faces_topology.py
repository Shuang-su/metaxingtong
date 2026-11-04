import bpy,pathlib,json,sys,math,hashlib
from itertools import combinations
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parent;P=R.parents[1];sys.path.insert(0,str(R));from adjacent_triangle_overlap import off_shared_extent,tests
result=[];normals={};eps=1e-6
for label,path in [('before',P/'inputs/leaf-only-r06-nonexact-diagnostic-replay.blend'),('after',P/'models/leaf-only-contact-candidate-v2.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));rows=[];ns={};minz=100
 for o in bpy.context.scene.objects:
  if not o.name.startswith(('LEAF_002','LEAF_003')):continue
  m=o.data;m.calc_loop_triangles();v=[o.matrix_world@q.co for q in m.vertices];ii=[tuple(t.vertices) for t in m.loop_triangles];tri=[tuple(tuple(v[j]) for j in t) for t in ii];tree=BVHTree.FromPolygons(v,ii,all_triangles=True)
  ns[o.name]=[(v[t[1]]-v[t[0]]).cross(v[t[2]]-v[t[0]]).normalized() for t in ii];minz=min(minz,min(p.z for p in v));n=0;flags=[];worst=None;mx=-1;counts={}
  incident=defaultdict(set)
  for ti,ids in enumerate(ii):
   for vid in ids:incident[vid].add(ti)
  pairs=set()
  for ids in incident.values():pairs.update(combinations(sorted(ids),2))
  for i,j in sorted(pairs):
   shared=set(ii[i])&set(ii[j])
   if not shared:continue
   assert len(shared)<3
   extent,mode,hitpoints=off_shared_extent(tri[i],tri[j],[tuple(v[k]) for k in sorted(shared)]);n+=1;counts[mode]=counts.get(mode,0)+1
   if extent>mx:mx=extent;worst=dict(triangle_a=i,triangle_b=j,shared_vertices=sorted(shared),extent=extent,mode=mode,hitpoints=hitpoints)
   if extent>eps:flags.append(dict(triangle_a=i,triangle_b=j,shared_vertices=sorted(shared),extent=extent,mode=mode))
  rows.append(dict(name=o.name,candidate_shared_vertex_pairs_tested=n,methods=counts,max_off_shared_extent=mx,worst_pair=worst,flagged_pairs=flags));print(label,o.name,'tested',n,'maxextent',mx,'flags',len(flags),flush=True)
 normals[label]=ns;result.append(dict(label=label,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rows=rows,vein_vertex_minimum_world_z=minz,analytic_wave_upper_bound_float32_margin=.02700001,positive_vertical_clearance_to_analytic_bound=minz-.02700001))
changes=[]
for name,aa in normals['before'].items():
 bb=normals['after'][name];assert len(aa)==len(bb);dots=[max(-1,min(1,a.dot(b))) for a,b in zip(aa,bb)];changes.append(dict(name=name,triangles=len(dots),minimum_old_new_unit_normal_dot=min(dots),maximum_normal_change_degrees=math.degrees(math.acos(min(dots))),nonpositive_dot_count=sum(d<=0 for d in dots)))
out=dict(scope='19 tube meshes only. All shared-vertex triangle pairs directly enumerated from topology and tested for intersection outside their shared vertex/edge. Float64 feature intersections and coplanar clipping, extent tolerance1e-6; not exact arithmetic or source fit. Old/new normal dot is a diagnostic, not a global injectivity proof. Analytic wave bound uses the archived .018*sin + .009*sin formula with a conservative float32 margin, not current lake geometry measurement or hydrodynamics.',unit_tests=tests(),rows=result,normal_changes=changes,model_modified=False,source_accepted=False)
(R/'adjacent-face-topology-results.json').write_text(json.dumps(out,indent=2)+'\n');print('total flags',sum(len(x['flagged_pairs']) for r in result for x in r['rows']),'max normal angle',max(x['maximum_normal_change_degrees'] for x in changes),'clearance',result[1]['positive_vertical_clearance_to_analytic_bound'],flush=True)
