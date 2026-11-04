import bpy,pathlib,json,sys,math,hashlib,datetime
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parent;P=R.parents[1];sys.path.insert(0,str(R));from triangle_distance import triangle_triangle2

def surf(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@p.co for p in m.vertices];idx=[tuple(t.vertices) for t in m.loop_triangles]
 return dict(name=o.name,v=v,indices=idx,tris=[tuple(tuple(v[j]) for j in t) for t in idx],tree=BVHTree.FromPolygons(v,idx,all_triangles=True))
def collisions(a,b,same=False):
 pairs=a['tree'].overlap(b['tree']);ret=[];skipped=0
 for i,j in pairs:
  if same:
   if i>=j:continue
   if set(a['indices'][i])&set(a['indices'][j]):skipped+=1;continue
  if triangle_triangle2(a['tris'][i],b['tris'][j])<=1e-18:ret.append([i,j])
 return dict(candidate_pairs=len(pairs),skipped_shared_vertex_pairs=skipped,intersecting_pairs=ret)
records=[];centers={}
for label,path in [('before',P/'inputs/leaf-only-r06-nonexact-diagnostic-replay.blend'),('after',P/'models/leaf-only-contact-candidate-v2.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));ss=[surf(o) for o in bpy.context.scene.objects if o.name.startswith(('LEAF_002','LEAF_003'))];cs={};selfs=[];between=[]
 for a in ss:
  sides=9 if a['name'].startswith('LEAF_002') else 6;cs[a['name']]=[sum(a['v'][i:i+sides],Vector())/sides for i in range(0,len(a['v']),sides)]
  c=collisions(a,a,True);selfs.append(dict(name=a['name'],**c));print(label,a['name'],'nonincident-self',len(c['intersecting_pairs']),flush=True)
 for i,a in enumerate(ss):
  if not a['name'].startswith('LEAF_003'):continue
  for b in ss[i+1:]:
   if not b['name'].startswith('LEAF_003'):continue
   between.append(dict(a=a['name'],b=b['name'],**collisions(a,b)))
 centers[label]=cs;records.append(dict(label=label,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),nonincident_self=selfs,branch_pair_tests=between))
slopes=[]
for name,before in centers['before'].items():
 after=centers['after'][name];oldv=[b-a for a,b in zip(before,before[1:])];newv=[b-a for a,b in zip(after,after[1:])]
 oldbend=[math.degrees(a.angle(b)) for a,b in zip(oldv,oldv[1:])];newbend=[math.degrees(a.angle(b)) for a,b in zip(newv,newv[1:])]
 slopes.append(dict(name=name,max_segment_direction_change_degrees=max(math.degrees(a.angle(b)) for a,b in zip(oldv,newv)),max_bend_before_degrees=max(oldbend),max_bend_after_degrees=max(newbend),max_bend_change_degrees=max(abs(a-b) for a,b in zip(oldbend,newbend)),segment_length_ratio_range=[min(b.length/a.length for a,b in zip(oldv,newv)),max(b.length/a.length for a,b in zip(oldv,newv))]))
changes=[]
for before,after in zip(records[0]['nonincident_self'],records[1]['nonincident_self']):
 assert before['name']==after['name'];old={tuple(t) for t in before['intersecting_pairs']};new={tuple(t) for t in after['intersecting_pairs']};changes.append(dict(name=after['name'],before=len(old),after=len(new),added=sorted(new-old),removed=sorted(old-new)))
bc=[]
for before,after in zip(records[0]['branch_pair_tests'],records[1]['branch_pair_tests']):
 assert (before['a'],before['b'])==(after['a'],after['b']);old={tuple(t) for t in before['intersecting_pairs']};new={tuple(t) for t in after['intersecting_pairs']};bc.append(dict(a=after['a'],b=after['b'],before=len(old),after=len(new),added=sorted(new-old),removed=sorted(old-new)))
out=dict(created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Nonincident triangle self-intersections for 19 tubes and intersections for 153 distinct branch pairs. Shared-vertex self-pairs are excluded; adjacent-fold intersections remain untested. Central-branch overlap is intentionally outside this check and was checked as junction contact in VD2. Float32 BVH candidates and float64 feature distance <=1e-9 tolerance, not exact arithmetic.',records=records,centerline_slope_changes=slopes,self_pair_changes=changes,branch_pair_changes=bc,model_modified=False,source_accepted=False)
(R/'tube-regression-results.json').write_text(json.dumps(out,indent=2)+'\n')
print('Added nonincident self pairs',sum(len(r['added']) for r in changes),'added branch pair intersections',sum(len(r['added']) for r in bc),'max direction change',max(r['max_segment_direction_change_degrees'] for r in slopes),flush=True)
