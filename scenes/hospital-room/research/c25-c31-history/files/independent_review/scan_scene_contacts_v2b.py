import bpy,numpy as np,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent;R=O.parent;sys.path.insert(0,str(O));from triangle_narrow_phase import tri_intersect
P='Chair • narrow curved wraparound back';L='Chair • slim back support';TARGETS=[P,L]
paths={'C23':R/'inputs/hospital_C23_source_shaped_supports_CONDITIONAL.blend','C25_v2b':R/'v2b/hospital_C25_structural_volume_CONDITIONAL.blend'}
DIRECTIONS=[Vector(x).normalized()for x in [(1,.371,.137),(.239,1,.461),(.177,.293,1)]]
def inside(tree,p):
 # A three-direction parity agreement is only a bounded numerical containment test.
 near=tree.find_nearest(Vector(p));
 if near[3] is None:return None
 if near[3]<=1e-6:return None
 votes=[]
 for di in DIRECTIONS:
  origin=Vector(p)+di*1e-6;n=0
  for _ in range(256):
   loc,no,ix,dist=tree.ray_cast(origin,di,1000)
   if ix is None:break
   n+=1;origin=loc+di*1e-6
  else:return None
  votes.append(n%2)
 return bool(votes[0])if len(set(votes))==1 else None
results={}
for label,path in paths.items():
 before=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();MD={}
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=np.array([list(x.co)for x in me.vertices]);m=np.array(ev.matrix_world);v=v@m[:3,:3].T+m[:3,3];f=np.array([list(x.vertices)for x in me.loop_triangles],int);ev.to_mesh_clear()
  if len(v)and len(f):MD[ob.name]={'v':v,'f':f,'lo':v.min(0),'hi':v.max(0),'tree':None,'hide_render':ob.hide_render}
 def tree(n):
  d=MD[n]
  if d['tree']is None:d['tree']=BVHTree.FromPolygons(d['v'].tolist(),d['f'].tolist(),all_triangles=True,epsilon=0)
  return d['tree']
 rows=[]
 for tar in TARGETS:
  A=MD[tar]
  for name,B in MD.items():
   if name.startswith('Chair'):continue
   gap=float(np.linalg.norm(np.maximum(np.maximum(A['lo']-B['hi'],B['lo']-A['hi']),0)))
   row={'target':tar,'other':name,'other_hide_render':B['hide_render'],'aabb_gap':gap,'collision':False}
   if gap>0:row['method']='AABB separation';rows.append(row);continue
   at=tree(tar);bt=tree(name);pairs=at.overlap(bt);hits=[]
   for i,j in pairs[:200000]:
    if tri_intersect(A['v'][A['f'][i]],B['v'][B['f'][j]]):hits.append([i,j])
   samples=[]
   for src,dst,lab in [(A,bt,'target_inside_other'),(B,at,'other_inside_target')]:
    ids=np.unique(np.linspace(0,len(src['v'])-1,min(256,len(src['v']))).astype(int));vals=[inside(dst,src['v'][i])for i in ids];samples.append({'direction':lab,'sample_count':len(ids),'inside_count':sum(v is True for v in vals),'outside_count':sum(v is False for v in vals),'ambiguous_or_surface_count':sum(v is None for v in vals),'inside_first10_vertex_ids':[int(ids[j])for j,v in enumerate(vals)if v is True][:10]})
   best=(float('inf'),None)
   for src,dst,lab in [(A,bt,'target_to_other'),(B,at,'other_to_target')]:
    ids=np.unique(np.linspace(0,len(src['v'])-1,min(5000,len(src['v']))).astype(int))
    for i in ids:
     pt,no,fi,dist=dst.find_nearest(Vector(src['v'][i]))
     if dist is not None and dist<best[0]:best=(float(dist),{'direction':lab,'source_vertex':int(i),'source_xyz':src['v'][i].tolist(),'destination_xyz':list(pt)})
   row.update({'method':'BVH candidates + independent triangle narrow phase, 3-direction parity sample containment, sampled nearest distances','bvh_candidate_pairs':len(pairs),'tested_triangle_pairs':min(len(pairs),200000),'complete_triangle_test':len(pairs)<=200000,'confirmed_triangle_intersection_count':len(hits),'first20_intersection_pairs':hits[:20],'containment_probes':samples,'minimum_sampled_vertex_surface_gap':best[0],'nearest_witness':best[1],'collision':bool(hits or any(q['inside_count']for q in samples))});rows.append(row);print(label,tar,name,row['collision'],len(hits),best[0],flush=True)
 results[label]={'sha256_before':before,'sha256_after':hashlib.sha256(path.read_bytes()).hexdigest(),'mesh_count':len(MD),'scanned_pair_count':len(rows),'rows':rows}
old={(r['target'],r['other']):r for r in results['C23']['rows']};new=results['C25_v2b']['rows'];out={'scope':'All non-chair mesh objects in the full saved scene, including render-hidden geometry; exactly the rebuilt panel and left frame are scanned. Chair-local contacts were tested separately.','method_limitations':'AABB separation and numerical surface intersection checks; containment uses at most 256 vertex samples in each direction and three agreed ray parities. No exact rational or exhaustive containment certificate. Minimum distance is a sampled vertex-to-surface upper bound.','results':results,'new_collision_pairs':[[r['target'],r['other']]for r in new if r['collision']and not old.get((r['target'],r['other']),{}).get('collision',False)],'inherited_collision_pairs':[[r['target'],r['other']]for r in new if r['collision']and old.get((r['target'],r['other']),{}).get('collision',False)],'all_inputs_unchanged':all(q['sha256_before']==q['sha256_after']for q in results.values())};(O/'C25_v2b_fullscene_contacts.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('NEW',out['new_collision_pairs'],'INHERITED',out['inherited_collision_pairs'],flush=True)
