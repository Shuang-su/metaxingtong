import bpy,json,hashlib,math,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent.parent;src=P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
A=.74;W=11.4;D=3.;H=2.5;tau=.12
# Construct no mesh and do not evaluate any alternative a.
def surf(u,t):return np.array([W*u*(A+(1-A)*abs(t)),5.5+D*t,6+H*(1-abs(t))**2+.8*abs(u)**7*t*t])
def normal(u,t):
 assert t!=0
 du=np.array([W*(A+(1-A)*abs(t)),0,5.6*(1 if u>=0 else -1)*abs(u)**6*t*t])
 dt=np.array([W*u*(1-A)*(1 if t>0 else -1),D,-2*H*(1-abs(t))*(1 if t>0 else -1)+1.6*abs(u)**7*t]);n=np.cross(du,dt);return n/np.linalg.norm(n)
def tangents(c):
 seg=np.diff(c,axis=0);seg=seg/np.linalg.norm(seg,axis=1)[:,None];t=[seg[0]]
 for j in range(1,len(c)-1):
  v=seg[j-1]+seg[j];t.append(v/np.linalg.norm(v))
 return np.array(t+[seg[-1]])
def rot(a,b):
 cross=np.cross(a,b);co=float(np.dot(a,b));ss=float(np.dot(cross,cross))
 if ss<1e-24:return np.eye(3)
 K=np.array([[0,-cross[2],cross[1]],[cross[2],0,-cross[0]],[-cross[1],cross[0],0]]);return np.eye(3)+K+K@K*((1-co)/ss)
rows=[]
for o in s.objects:
 if not o.name.startswith('ROOF_MAIN') or o.name in ['ROOF_MAIN closed shell','ROOF_MAIN gold front eave','ROOF_MAIN gold back eave inferred']:continue
 if o.name.startswith('ROOF_MAIN rib '):
  i=int(o.name.rsplit(' ',1)[1]);u=-1+2*i/44;c=np.array([surf(u,-1+2*j/48)+[0,0,.06] for j in range(49)]);radius=.055
 elif o.name=='ROOF_MAIN gold ridge':c=np.array([surf(-1+2*i/64,0)+[0,0,.12] for i in range(65)]);radius=.085
 elif o.name.startswith('ROOF_MAIN swept gable'):
  # Exact object x sign establishes left/right without assuming Blender numeric suffix ordering.
  u=-1 if sum(v.co.x for v in o.data.vertices)<0 else 1;c=np.array([surf(u,-1+2*j/48)+[0,0,.1] for j in range(49)]);radius=.085
 else:raise RuntimeError('unknown tube '+o.name)
 v=np.array([list(o.matrix_world@p.co) for p in o.data.vertices]);dist=np.linalg.norm(v[:,None,:]-c[None,:,:],axis=2);assignment=dist.argmin(axis=1);T=tangents(c);rings=[];allrel=[];allabs=[];valid=True
 edges={tuple(sorted(e.vertices)) for e in o.data.edges}
 for j,center in enumerate(c):
  ids=np.where(assignment==j)[0];rv=v[ids];q=rv-center;nn=len(ids)
  if nn<3:valid=False;rings.append({'station':j,'count':nn,'valid':False});continue
  mean=rv.mean(axis=0);U,sv,Vh=np.linalg.svd(rv-mean,full_matrices=False);n=Vh[-1]
  if np.dot(n,T[j])<0:n=-n
  axes=Vh[:2];angles=np.arctan2((rv-mean)@axes[1],(rv-mean)@axes[0]);order=ids[np.argsort(angles)];cycle_present=sum(tuple(sorted((int(order[k]),int(order[(k+1)%nn])))) in edges for k in range(nn))
  radii=np.linalg.norm(q,axis=1);Q=rot(n,T[j]);aligned=center+q@Q.T;relative=center+q # a==a0, relative tangent rotation is I by definition.
  pair0=np.linalg.norm(rv[:,None]-rv[None,:],axis=2);pair1=np.linalg.norm(aligned[:,None]-aligned[None,:],axis=2)
  raderr=float(np.max(np.abs(radii-radius)));planerr=float(np.max(np.abs((rv-mean)@n)));ce=float(np.linalg.norm(mean-center));identity=float(np.max(np.linalg.norm(relative-rv,axis=1)));align=float(np.max(np.linalg.norm(aligned-rv,axis=1)));allrel.append(identity);allabs.append(align)
  rings.append({'station':j,'actual_vertex_ids':ids.tolist(),'count':nn,'centerline':center.tolist(),'actual_mean_center_error':ce,'nominal_radius':radius,'radius_minmax':[float(radii.min()),float(radii.max())],'max_radius_error':raderr,'plane_residual':planerr,'ring_cycle_edges_present':cycle_present,'ring_cycle_edges_expected':nn,'actual_ring_normal':n.tolist(),'authored_unit_bisector_tangent':T[j].tolist(),'angle_degrees':float(math.degrees(math.acos(np.clip(np.dot(n,T[j]),-1,1)))),'relative_identity_max_vertex_error':identity,'absolute_tangent_alignment_max_vertex_shift':align,'absolute_rotation_pairwise_distance_error':float(np.abs(pair1-pair0).max())})
  if nn!=8 or cycle_present!=nn or raderr>1e-5 or planerr>1e-5 or ce>1e-5:valid=False
 sorted_dist=np.sort(dist,axis=1)
 rows.append({'object':o.name,'vertices':len(v),'centerline_stations':len(c),'ring_assignment':'unique nearest authored centerline station, validated by mean/radius/planarity/cyclic mesh edges; not assumed vertex chunks','smallest_nearest_station_distance_margin':float((sorted_dist[:,1]-sorted_dist[:,0]).min()),'all_eight_point_rings_valid_under_1e_5':valid,'max_relative_identity_error':max(allrel),'max_absolute_alignment_shift':max(allabs),'rings':rings})
# New theoretical fold-band definition only: no topology created.
eps=2/32;fold=[];shell=bpy.data.objects['ROOF_MAIN closed shell'];N=len(shell.data.vertices)//2
for i in [0,8,16,24,32,40,48,56,64]:
 u=-1+2*i/64;left=surf(u,-eps)-tau*normal(u,-eps);right=surf(u,eps)-tau*normal(u,eps);mid=(left+right)/2;ix=16*65+i;oldtop=np.array(shell.matrix_world@shell.data.vertices[ix].co);oldbottom=np.array(shell.matrix_world@shell.data.vertices[ix+N].co)
 fold.append({'u':u,'epsilon_original_first_row':eps,'left_normal_offset_boundary':left.tolist(),'right_normal_offset_boundary':right.tolist(),'proposed_ruled_inner_seam_midpoint':mid.tolist(),'original_saved_top_ridge':oldtop.tolist(),'original_saved_bottom_ridge':oldbottom.tolist(),'new_inner_minus_saved_bottom':(mid-oldbottom).tolist(),'original_ridge_vertical_distance':float(oldtop[2]-oldbottom[2]),'proposed_ridge_vertical_distance':float(surf(u,0)[2]-mid[2]),'note':'ruled inner band only a precisely stated hypothetical seam; not claimed normal-distance thickness, no model generated'})
result={'input':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'a':A,'not_a_parameter_scan':True,'no_mesh_or_render_generated':True,'tube_count':len(rows),'rings_total':sum(len(r['rings']) for r in rows),'two_eave_tubes':'excluded and read-only; intended exact originals, no transformed versions created','tube_checks':rows,'fold_band_hypothesis':{'epsilon':eps,'outside_band':'analytic top S and inward normal offset S-.12*N separately on t<=-epsilon and t>=epsilon','inside_band':'retain original outer top S including crease; connect two inward-offset boundary rows by ruled strip with corresponding u; explicit side closures would still need topology/intersection tests','guarantees':'offset vector norm .12 only in smooth patches; seam is deliberately NOT claimed globally equal normal thickness','not_adopted':True,'baseline_rows':fold}}
(P/'results/baseline-rings-and-fold.json').write_text(json.dumps(result,indent=2));print('tubes',len(rows),'rings',result['rings_total'],'all valid',all(r['all_eight_point_rings_valid_under_1e_5'] for r in rows));print('max absolute alignment shift',max(r['max_absolute_alignment_shift'] for r in rows));print('mid seam',fold[4])
