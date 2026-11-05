import bpy,numpy as np,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent.parent
src=P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
A=.55;N=2145
objs={o.name:o for o in s.objects if o.type=='MESH'}
old={n:np.array([list(o.matrix_world@v.co) for v in o.data.vertices]) for n,o in objs.items()};new={n:v.copy() for n,v in old.items()}
def C(u,t,a):return np.array([11.4*u*(a+(1-a)*abs(t)),5.5+3*t,6+2.5*(1-abs(t))**2+.8*abs(u)**7*t*t])
def tangent(c):
 seg=np.diff(c,axis=0);seg/=np.linalg.norm(seg,axis=1)[:,None];mid=seg[:-1]+seg[1:];mid/=np.linalg.norm(mid,axis=1)[:,None];return np.vstack([seg[0],mid,seg[-1]])
def R(a,b):
 c=np.cross(a,b);co=np.clip(np.dot(a,b),-1,1);ss=np.dot(c,c)
 if ss<1e-24:
  if co<0:raise ValueError('antiparallel tangent rejected')
  return np.eye(3)
 K=np.array([[0,-c[2],c[1]],[c[2],0,-c[0]],[-c[1],c[0],0]]);return np.eye(3)+K+K@K*((1-co)/ss)
shell='ROOF_MAIN closed shell'
for j in range(33):
 for i in range(65):
  ix=j*65+i;u=-1+2*i/64;t=-1+2*j/32;delta=C(u,t,A)-C(u,t,.74);new[shell][ix]+=delta;new[shell][ix+N]+=delta
ringbase=json.loads((P/'sources/previous-ring-baseline.json').read_text());ringmetrics=[]
for row in ringbase['tube_checks']:
 n=row['object'];c0=np.array([r['centerline'] for r in row['rings']]);c1=c0.copy()
 if ' rib ' in n:
  u=-1+2*int(n.rsplit(' ',1)[1])/44;params=[(u,-1+2*j/48) for j in range(49)]
 elif n.endswith('gold ridge'):params=[(-1+2*i/64,0) for i in range(65)]
 else:
  u=-1 if old[n][:,0].mean()<0 else 1;params=[(u,-1+2*j/48) for j in range(49)]
 for j,(u,t) in enumerate(params):c1[j]+=C(u,t,A)-C(u,t,.74)
 T0=tangent(c0);T1=tangent(c1);err=[];radius=[];det=[]
 for j,ring in enumerate(row['rings']):
  ids=ring['actual_vertex_ids'];q=old[n][ids]-c0[j];rot=R(T0[j],T1[j]);new[n][ids]=c1[j]+q@rot.T;delta=new[n][ids]-c1[j]
  err.append(float(np.abs(np.linalg.norm(q[:,None]-q[None,:],axis=2)-np.linalg.norm(delta[:,None]-delta[None,:],axis=2)).max()));radius.append(float(np.abs(np.linalg.norm(q,axis=1)-np.linalg.norm(delta,axis=1)).max()));det.append(float(np.linalg.det(rot)))
 ringmetrics.append({'object':n,'max_pair_distance_error':max(err),'max_radius_error':max(radius),'rotation_det_minmax':[min(det),max(det)]})
tri={};tree={};bounds={}
for n,o in objs.items():
 o.data.calc_loop_triangles();tri[n]=np.array([list(t.vertices) for t in o.data.loop_triangles],dtype=int)
 for state,vs in [('old',old[n]),('new',new[n])]:
  tree[state,n]=BVHTree.FromPolygons(vs.tolist(),tri[n].tolist(),all_triangles=True,epsilon=0);bounds[state,n]=(vs.min(0),vs.max(0))
def intersectbox(a,b):return np.all(a[0]<=b[1]) and np.all(b[0]<=a[1])
def count(state,a,b):return len(tree[state,a].overlap(tree[state,b]))
main=[n for n in objs if n.startswith('ROOF_MAIN')];metrics=[]
for n in main:
 tt=tri[n];v=new[n];p=v[tt];cr=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);op=old[n][tt];ocr=np.cross(op[:,1]-op[:,0],op[:,2]-op[:,0]);selfcounts={}
 for state in ['old','new']:
  pairs=tree[state,n].overlap(tree[state,n]);w=[(a,b) for a,b in pairs if a<b and not(set(tt[a])&set(tt[b]))];selfcounts[state]={'nonshared_triangle_pairs':len(w),'examples':w[:12]}
 metrics.append({'object':n,'max_vertex_displacement':float(np.linalg.norm(v-old[n],axis=1).max()),'degenerate_triangles_area2_below_1e_12':int((np.linalg.norm(cr,axis=1)<1e-12).sum()),'signed_volume':float(np.sum(np.einsum('ij,ij->i',p[:,0],np.cross(p[:,1],p[:,2])))/6),'triangle_normal_dot_old_min':float(np.min(np.einsum('ij,ij->i',cr,ocr)/(np.linalg.norm(cr,axis=1)*np.linalg.norm(ocr,axis=1)))),'self_bvh':selfcounts})
contacts=[]
for ai,a in enumerate(main):
 for b in objs:
  if b==a or (b in main and main.index(b)<ai):continue
  if not any(intersectbox(bounds[state,a],bounds[state,b]) for state in ['old','new']):continue
  co=count('old',a,b);cn=count('new',a,b)
  if co or cn:contacts.append({'a':a,'b':b,'old_triangle_pairs':co,'new_triangle_pairs':cn,'new_relationship':co==0 and cn>0})
# Actual discrete outer vertex normals, independently area weighted for angle/projection diagnostics.
toptri=tri[shell][np.max(tri[shell],axis=1)<N]
def normals(v):
 p=v[toptri];face=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);out=np.zeros((N,3))
 for k in range(3):np.add.at(out,toptri[:,k],face)
 return out/np.linalg.norm(out,axis=1)[:,None]
d0=old[shell][N:]-old[shell][:N];d1=new[shell][N:]-new[shell][:N];nv0=normals(old[shell]);nv1=normals(new[shell]);L=np.linalg.norm(d1,axis=1);angles0=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',-d0,nv0)/L,-1,1)));angles1=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',-d1,nv1)/L,-1,1)))
res={'a_single':A,'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'no_candidate_saved_or_rendered':True,'paired_vector_max_error':float(np.abs(d1-d0).max()),'paired_length_max_error':float(np.abs(np.linalg.norm(d1,axis=1)-np.linalg.norm(d0,axis=1)).max()),'shell_eave_anchor_max_displacement':float(np.max(np.linalg.norm((new[shell]-old[shell])[list(range(65))+list(range(N-65,N))+list(range(N,N+65))+list(range(2*N-65,2*N))],axis=1))),'shell_normal_measure':'area-weighted actual outer triangles; not Blender vertex normal or surface shortest distance','paired_angles_old_minmax':[float(angles0.min()),float(angles0.max())],'paired_angles_new_minmax':[float(angles1.min()),float(angles1.max())],'new_normal_projection_minmax':[float(np.abs(np.einsum('ij,ij->i',d1,nv1)).min()),float(np.abs(np.einsum('ij,ij->i',d1,nv1)).max())],'ring_metrics':ringmetrics,'objects':metrics,'contacts':contacts,'limits':'BVH nonshared self triangle pairs excludes adjacent/shared-vertex folding; triangle counts are not penetration depth. Containment not yet checked. No source acceptance.'}
# Blender outer polygon vertex normals, to avoid conflating triangle-area-weighted with original normals.
blangles={}
for state,vs in [('old',old[shell]),('new',new[shell])]:
 me=bpy.data.meshes.new('temporary outer normal only '+state);me.from_pydata(vs[:N].tolist(),[],[list(p.vertices) for p in objs[shell].data.polygons if max(p.vertices)<N]);me.update();nn=np.array([list(v.normal) for v in me.vertices]);nn/=np.linalg.norm(nn,axis=1)[:,None];ang=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',-d1,nn)/L,-1,1)));blangles[state]={'angle_minmax':[float(ang.min()),float(ang.max())],'projection_minmax':[float(np.abs(np.einsum('ij,ij->i',d1,nn)).min()),float(np.abs(np.einsum('ij,ij->i',d1,nn)).max())]};bpy.data.meshes.remove(me)
res['blender_outer_polygon_vertex_normal_metrics']=blangles
# Finite containment witnesses for external neighbors only. Not an exhaustive intersection proof.
def winding(p,v,tt):
 q=v[tt]-p;l=np.linalg.norm(q,axis=2);num=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2]));den=l.prod(1)+np.einsum('ij,ij->i',q[:,0],q[:,1])*l[:,2]+np.einsum('ij,ij->i',q[:,1],q[:,2])*l[:,0]+np.einsum('ij,ij->i',q[:,2],q[:,0])*l[:,1];return float(np.sum(2*np.arctan2(num,den))/(4*np.pi))
contain=[]
for a in main:
 for b in objs:
  if b in main or not any(intersectbox(bounds[state,a],bounds[state,b]) for state in ['old','new']):continue
  for source,target in [(a,b),(b,a)]:
   ids=np.unique(np.linspace(0,len(tri[source])-1,min(64,len(tri[source])),dtype=int));row={'sample_source':source,'target':target,'triangle_ids':ids.tolist(),'method':'up to 64 evenly indexed triangle centroids, same triangle ids old/new, double precision winding; finite witnesses only','states':{}}
   for state,vs in [('old',old),('new',new)]:
    pts=vs[source][tri[source][ids]].mean(1);bb=bounds[state,target];hits=[];tested=0
    for ix,p in zip(ids,pts):
     if not np.all((p>=bb[0])&(p<=bb[1])):continue
     tested+=1;w=winding(p,vs[target],tri[target]);nearest=tree[state,target].find_nearest(p);dist=float(nearest[3]) if nearest else None
     if abs(w)>.5 and dist is not None and dist>1e-6:hits.append({'triangle_id':int(ix),'point':p.tolist(),'winding':w,'distance':dist})
    row['states'][state]={'inside_count':len(hits),'tested_after_bounds':tested,'witnesses':hits}
   row['new_sample_witness_ids']=sorted(set(h['triangle_id'] for h in row['states']['new']['witnesses'])-set(h['triangle_id'] for h in row['states']['old']['witnesses']));contain.append(row)
# Parent-requested bounded local diagnostic: all triangle centroids of rib00 / left existing cloud tube, both directions.
local=[]
for source,target in [('ROOF_MAIN rib 00','CLOUD_0 silhouette decorative proxy'),('CLOUD_0 silhouette decorative proxy','ROOF_MAIN rib 00')]:
 entry={'source':source,'target':target,'states':{}}
 for state,vs in [('old',old),('new',new)]:
  pts=vs[source][tri[source]].mean(1);bb=bounds[state,target];values=[]
  for ix,p in enumerate(pts):
   if not np.all((p>=bb[0])&(p<=bb[1])):continue
   w=winding(p,vs[target],tri[target]);near=tree[state,target].find_nearest(p);dist=float(near[3]);values.append({'triangle':ix,'point':p.tolist(),'winding':w,'nearest_surface_distance':dist,'inside':abs(w)>.5 and dist>1e-6})
  hits=[v for v in values if v['inside']];entry['states'][state]={'all_triangle_centroids':len(pts),'in_bbox':len(values),'inside_count':len(hits),'max_inside_distance':max([v['nearest_surface_distance'] for v in hits],default=0),'samples':values}
 local.append(entry)
res['rib00_cloud0_local_all_centroid_check']=local
res['external_finite_containment']=contain
res['limits']='Self BVH excludes adjacent/shared-vertex folds. External containment samples are finite, not exhaustive. Triangle contact counts not penetration measure. No source acceptance.'
(P/'results/single-a055-check.json').write_text(json.dumps(res,indent=2));print('paired vector',res['paired_vector_max_error'],'anchors',res['shell_eave_anchor_max_displacement']);print('self',[(r['object'],r['self_bvh']) for r in metrics if r['self_bvh']['new']['nonshared_triangle_pairs']]);print('new relationships',sum(r['new_relationship'] for r in contacts));print('normal angles',res['paired_angles_new_minmax'])
# Projection analysis operates only on these new arrays, not the rejected whole-mesh field.
exec((P/'scripts/project_single_arrays.py').read_text())
