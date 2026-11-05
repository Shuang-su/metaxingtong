import bpy,json,hashlib,math,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parent
j=json.load(open(R/'cyber-roof-parametric-method-study-20261105/results/baseline-rings-and-fold.json'))
src=R/'cyber-roof-stage-20261105/models/roof-r05.blend';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha==j['sha256'];bpy.ops.wm.open_mainfile(filepath=str(src))
rows=[]
for rec in j['tube_checks']:
 o=bpy.data.objects[rec['object']];v=np.array([list(o.matrix_world@q.co)for q in o.data.vertices]);cs=np.array([a['centerline']for a in rec['rings']]);a=np.linalg.norm(v[:,None]-cs[None,:],axis=2).argmin(axis=1);badids=0;rad=0;plane=0;cent=0;ds=0;ang=0
 for i,r in enumerate(rec['rings']):
  ids=np.flatnonzero(a==i);badids+=int(set(ids)!=set(r['actual_vertex_ids']));vv=v[ids];c=vv.mean(0);_,_,vh=np.linalg.svd(vv-c,full_matrices=False);n=vh[-1];T=np.array(r['authored_unit_bisector_tangent']);n*=1 if n@T>=0 else -1
  rad=max(rad,float(np.max(abs(np.linalg.norm(vv-cs[i],axis=1)-r['nominal_radius']))));plane=max(plane,float(np.max(abs((vv-c)@n))));cent=max(cent,float(np.linalg.norm(c-cs[i])));angle=math.atan2(np.linalg.norm(np.cross(n,T)),n@T);ang=max(ang,math.degrees(angle))
  axis=np.cross(n,T);ss=np.linalg.norm(axis)
  if ss>1e-12:
   k=axis/ss;q=vv-cs[i];rot=q*math.cos(angle)+np.cross(k,q)*math.sin(angle)+np.outer(q@k,k)*(1-math.cos(angle));ds=max(ds,float(np.linalg.norm(rot-q,axis=1).max()))
 pairs=[abs(int(a[e.vertices[0]])-int(a[e.vertices[1]]))for e in o.data.edges];o.data.calc_loop_triangles();same=[int(a[t.vertices[0]])for t in o.data.loop_triangles if len(set(int(a[z])for z in t.vertices))==1]
 rows.append({'object':o.name,'ring_count':len(cs),'assignment_mismatch':badids,'max_radius_error':rad,'max_plane_error':plane,'max_center_error':cent,'normal_tangent_angle_deg':ang,'independent_rodrigues_alignment_shift':ds,'max_edge_station_span':max(pairs),'same_station_triangle_count':len(same),'same_station_triangle_nonendpoint_count':sum(x not in [0,len(cs)-1]for x in same),'all_vertices_covered':sum(len(x['actual_vertex_ids'])for x in rec['rings'])==len(v)})
# Recompute analytic centre ruled-strip seam at epsilon only; no geometric candidate.
e=.0625; z=6+2.5*(1-e)**2; nz=3/math.sqrt(9+(5*(1-e))**2);mid=z-.12*nz
out={'input_sha':sha,'tube_count':len(rows),'ring_count':sum(x['ring_count']for x in rows),'rows':rows,'centre_fold':{'mid_z':mid,'outer_z':8.5,'vertical_difference':8.5-mid,'reported_mid_z':j['fold_band_hypothesis']['baseline_rows'][4]['proposed_ruled_inner_seam_midpoint'][2]},'input_unchanged':sha==hashlib.sha256(src.read_bytes()).hexdigest(),'scope':'actual all48 tube meshes; independent assignment and SVD/Rodrigues; cap/local edge station adjacency. No candidate, no scan, no full self intersection.'}
(P/'baseline-check.json').write_text(json.dumps(out,indent=2));print('DONE',len(rows),out['ring_count'],max(x['independent_rodrigues_alignment_shift']for x in rows));print(out['centre_fold'])
