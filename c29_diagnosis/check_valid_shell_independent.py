from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];v=np.array(json.load(open(R/'c29/MATERIAL_actual_curtain_vertices.json')));o=np.array(json.load(open(R/'c29_diagnosis/c28_curtain_mesh_readonly.json'))['verts_local']);results=[]
def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
for row in range(65):
 a=v[row*225:(row+1)*225,:2];b=v[14625+row*225:14625+(row+1)*225,:2];p=np.r_[a,b[::-1]];e=np.roll(p,-1,axis=0)-p
 A=p[:,None,:];B=p[None,:,:];U=e[:,None,:];V=e[None,:,:];den=cross(U,V);nonparallel=abs(den)>1e-13;t=np.divide(cross(B-A,V),den,out=np.zeros_like(den),where=nonparallel);u=np.divide(cross(B-A,U),den,out=np.zeros_like(den),where=nonparallel)
 idx=np.arange(len(p));gap=abs(idx[:,None]-idx[None,:]);mask=(gap>1)&(gap<len(p)-1);hit=nonparallel&mask&(t>=-1e-9)&(t<=1+1e-9)&(u>=-1e-9)&(u<=1+1e-9)
 # Check distances from every endpoint to every nonadjacent segment, including collinear contacts.
 t0=((A-B)*V).sum(-1)/(V*V).sum(-1);nearest=B+np.clip(t0,0,1)[...,None]*V;dist=np.linalg.norm(A-nearest,axis=-1);dist[~mask]=np.inf
 results.append({'row':row,'nonadjacent_closed_polygon_intersections':int(hit.sum()//2),'min_nonadjacent_vertex_segment_distance_local':float(dist.min())})
out={'method':'closed 450-edge cross section including both end caps; nonadjacent inclusive segment intersections plus endpoint-to-segment contact distance, independent of producer script','rows':results,'minimum_clearance_local':min(r['min_nonadjacent_vertex_segment_distance_local'] for r in results),'all_intersection_counts_zero':all(r['nonadjacent_closed_polygon_intersections']==0 for r in results),'normal_thickness_preserved':False,'back_front_same_index_distance_range_local':[float(np.linalg.norm(v[14625:14850,:2]-v[:225,:2],axis=1).min()),float(np.linalg.norm(v[14625:14850,:2]-v[:225,:2],axis=1).max())]}
(R/'c29_diagnosis/valid_shell_independent_review.json').write_text(json.dumps(out,indent=2));print({k:x for k,x in out.items() if k!='rows'})
