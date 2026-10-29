import json,argparse
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--directory',default=str(Path(__file__).parent));ap.add_argument('--candidate',default='C25');a=ap.parse_args();D=Path(a.directory);old=json.load(open(D/'C23_silhouette_report.json'));new=json.load(open(D/(a.candidate+'_silhouette_report.json')));geo=json.load(open(D/(a.candidate+'_geometry_report.json')))
rows=[]
for category in ['panel_branches','support_branches','return_object_diagnostics']:
 baseline={b['id']:b for b in old[category]}
 for b in new[category]:
  o=baseline[b['id']];assert o['source_annotation']==b['source_annotation']
  pts=[]
  for p,q in zip(o['points'],b['points']):
   assert p['source_xy']==q['source_xy']
   if category=='panel_branches':
    x=p['visible_correct_branch'];y=q['visible_correct_branch'];ox=x['distance_px']if x else None;ny=y['distance_px']if y else None
   else:ox=p['absolute_x_error_px']if p['selected_boundary']and p['selected_boundary']['fullscene_visible']else None;ny=q['absolute_x_error_px']if q['selected_boundary']and q['selected_boundary']['fullscene_visible']else None
   pts.append({'source_xy':p['source_xy'],'C23_visible_error_px':ox,a.candidate+'_visible_error_px':ny,'delta_px':None if ox is None or ny is None else ny-ox})
  rows.append({'category':category,'id':b['id'],'target':b['target'],'tolerance_px':b['tolerance_px'],'C23':o['visible_metrics'],a.candidate:b['visible_metrics'],'points':pts})
R={'status':'REJECTED_GEOMETRY_AND_SOURCE'if any(not g.get('closed_oriented_manifold_numerical_pass')or not g.get('self_intersection',{}).get('pass',True)for n,g in geo['geometry'].items()if n in geo['allowed_changed_objects'])else'GEOMETRY_NUMERICAL_PASS_SOURCE_UNACCEPTED','baseline_sha256':old['sha256_before'],'candidate_sha256':new['sha256_before'],'fixed_source_sha256':old['source_sha256'],'source_hash_equal':old['source_sha256']==new['source_sha256'],'full_state_invariance_pass':geo['invariance']['pass'],'rows':rows,'limitations':['No pixel-error threshold is relaxed. Missing/invisible original points remain failures; RMS with missing points must not be presented as an aggregate acceptance score.','G and 665 are previous training/regression views, not independent holdouts.','New semantic groups are declared construction evidence, constrained by actual H silhouette orientation; they are not independent source observations.','No person/foreground occluder is synthesized, and source cuts are never extended. Full-scene visibility treats opaque evaluated mesh geometry, not alpha/transmission.','Numerical BVH + double-precision triangle tests are not exact rational certification. Adjoining triangles sharing a mesh vertex are excluded from nonadjacent intersection checks.','Contact intersections demonstrate overlap between separate objects, not mechanical joining or physically plausible hidden completion.','White-copy invariance and native render appearance are separate parent checks.']}
(D/(a.candidate+'_comparison.json')).write_text(json.dumps(R,ensure_ascii=False,indent=2))
lines=['# Independent C23 → '+a.candidate+' review','',R['status'],'','## Geometry and shared scene','',f"Shared-scene invariance: {'PASS'if R['full_state_invariance_pass']else'FAIL'}; permitted mesh objects: "+', '.join(geo['allowed_changed_objects'])+'.','']
for n,g in geo['geometry'].items():
 if n in geo['allowed_changed_objects']:
  si=g.get('self_intersection',{});lines.append(f"- {n}: {g['vertices']} vertices, {g['triangles']} triangles; {g.get('nonmanifold_vertex_count','not checked')} nonmanifold vertices; {g['nonmanifold_edge_count']} nonmanifold edges; orientation edge defects {g['inconsistent_oriented_edge_count']}; signed volume {g['signed_volume']:.9g}; nonadjacent numerical intersections {si.get('confirmed_numerical_triangle_intersections','not run')}.")
lines+=['','## Fixed-source errors','', 'All values below are full-scene geometrically visible errors in native pixels. Panel rows use Euclidean distance on the named physical branch; support rows use directed x-at-observed-y. Return rows are kept per object, with no best-object union.','', '| Branch / object | Tolerance | C23 RMS / max (scored/total) | Candidate RMS / max (scored/total) | Candidate within tolerance |','|---|---:|---:|---:|---:|']
def fmt(m):return 'missing'if m['rms_px']is None else f"{m['rms_px']:.3f} / {m['max_px']:.3f} ({m['scored_count']}/{m['record_count']})"
for r in rows:
 n=r[a.candidate];lines.append('| '+r['id']+(' / panel-only diagnostic'if r['category']=='return_object_diagnostics'else'')+' | '+str(r['tolerance_px'])+' | '+fmt(r['C23'])+' | '+fmt(n)+' | '+str(n['within_tolerance_count'])+'/'+str(n['record_count'])+' |')
lines+=['','## Boundaries of this evidence','']+['- '+v for v in R['limitations']]+['','The JSON artifacts retain each original source point, tolerance, exact target, directed branch, numerical error, ray first hits, and input hashes. No model or camera was saved by verification.']
(D/(a.candidate+'_INDEPENDENT_REVIEW.md')).write_text('\n'.join(lines)+'\n');print(R['status'])
