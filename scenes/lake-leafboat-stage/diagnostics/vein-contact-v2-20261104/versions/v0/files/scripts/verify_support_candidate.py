import bpy,pathlib,json,sys,math,hashlib,datetime,struct
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(pathlib.Path(__file__).parent));from triangle_distance import triangle_triangle2,tests
R=pathlib.Path(__file__).resolve().parents[1]
def surface(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];ii=[tuple(t.vertices) for t in m.loop_triangles]
 return dict(v=v,ii=ii,tris=[tuple(tuple(v[j]) for j in t) for t in ii],tree=BVHTree.FromPolygons(v,ii,all_triangles=True),triangles=list(m.loop_triangles))
def separation(o,selected,target):
 vv=[o.matrix_world@v.co for v in o.data.vertices];dist=[];tree=target['tree']
 for t in selected:
  pp=[vv[j] for j in t.vertices];c=sum(pp,Vector())/3;r=max((p-c).length for p in pp);upper=min(tree.find_nearest(p)[3] for p in pp)
  cc={x[2] for x in tree.find_nearest_range(c,r+upper+1e-5)};assert cc
  a=tuple(tuple(p) for p in pp);best=min((triangle_triangle2(a,target['tris'][j]),j) for j in cc)
  d=math.sqrt(best[0]);assert d<=upper+1e-5;dist.append(dict(triangle=t.index,minimum_distance=d,target_triangle=best[1]))
 return dict(triangles=len(dist),minimum_distance=min(x['minimum_distance'] for x in dist),intersection_triangles=sum(x['minimum_distance']<1e-9 for x in dist),details=dist)
def intersections(o,target):
 own=surface(o);pairs=own['tree'].overlap(target['tree']);hits=[]
 for i,j in pairs:
  if triangle_triangle2(own['tris'][i],target['tris'][j])<=1e-18:
   a,b,c=[Vector(p) for p in target['tris'][j]];normal=(b-a).cross(c-a).normalized()
   hits.append(dict(tube_triangle=i,shell_triangle=j,shell_normal_z=normal.z))
 return hits
results=[]
for label,model in [('baseline',R/'inputs/leaf-only-r06-nonexact-diagnostic-replay.blend'),('candidate',R/'models/leaf-only-contact-candidate-v2.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;shell=surface(s.objects['LEAF_001_ThinConcaveShell']);mid=surface(s.objects['LEAF_002_CentralMidrib']);rows=[]
 for o in s.objects:
  if not o.name.startswith(('LEAF_002','LEAF_003')):continue
  m=o.data;m.calc_loop_triangles();sides=9 if o.name.startswith('LEAF_002') else 6;nr=len(m.vertices)//sides;nf=(nr-1)*sides
  selected=[t for t in m.loop_triangles if ((t.polygon_index<2*sides or t.polygon_index==nf) if sides==9 else ((nr-3)*sides<=t.polygon_index<nf or t.polygon_index==nf+1))]
  terminal=separation(o,selected,shell)
  junction=None
  if sides==6:junction=separation(o,[t for t in m.loop_triangles if t.polygon_index<sides or t.polygon_index==nf],mid)
  collision=intersections(o,shell)
  rows.append(dict(name=o.name,selected_terminal_shell_distance=terminal,branch_start_to_midrib=junction,all_tube_shell_triangle_intersections=collision))
  print(label,o.name,'terminal',terminal['minimum_distance'],'junction',junction['minimum_distance'] if junction else None,'intersections',len(collision),flush=True)
 results.append(dict(label=label,model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),rows=rows))
report=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),unit_tests=tests(),scope='Selected terminal all-triangle distance and branch-start all-triangle distance; complete tube-shell intersections via BVH candidate overlap and feature tests. No source images or production original.',rows=results,source_accepted=False)
old={r['name']:r for r in results[0]['rows']};checks=[]
for row in results[1]['rows']:
 b=old[row['name']];newlower=[x for x in row['all_tube_shell_triangle_intersections'] if x['shell_normal_z']<-.01];oldlower=[x for x in b['all_tube_shell_triangle_intersections'] if x['shell_normal_z']<-.01]
 checks.append(dict(name=row['name'],terminal_contact=row['selected_terminal_shell_distance']['minimum_distance']<1e-9,
  junction_retained=(row['branch_start_to_midrib']['minimum_distance']<=b['branch_start_to_midrib']['minimum_distance']+1e-9) if row['branch_start_to_midrib'] else None,
  negative_z_shell_normal_intersections_before=len(oldlower),negative_z_shell_normal_intersections_after=len(newlower),
  new_negative_z_pairs=sorted(set((x['tube_triangle'],x['shell_triangle']) for x in newlower)-set((x['tube_triangle'],x['shell_triangle']) for x in oldlower))))
report['checks']=checks
(R/'qa/support-candidate-continuous-checks.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(x['terminal_contact'] for x in checks)
assert all(x['junction_retained'] for x in checks if x['junction_retained'] is not None)
assert all(not x['new_negative_z_pairs'] for x in checks),'Investigate newly introduced lower-oriented shell crossings; keep failed report.'
print('Terminal contacts and junctions pass; no newly introduced negative-Z shell-face intersection pairs.',flush=True)
