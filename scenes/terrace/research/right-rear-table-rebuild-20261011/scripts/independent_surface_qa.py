import bpy,bmesh,json,pathlib,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
P=(pathlib.Path(__file__).resolve().parents[2] if pathlib.Path(__file__).resolve().parent.name=='scripts' else pathlib.Path(__file__).resolve().parent);D=P/'delivery'

def getgeom(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles()
 v=np.array([list(o.matrix_world@p.co) for p in m.vertices],dtype=np.float64);t=np.array([list(p.vertices) for p in m.loop_triangles],dtype=int);edges=np.unique(np.sort(np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1),axis=0)
 bvh=BVHTree.FromPolygons([Vector(p) for p in v],[tuple(p) for p in t],all_triangles=True,epsilon=0.0);e.to_mesh_clear();return v,t,edges,bvh

def closest_edges(v1,e1,v2,e2,upper):
 best=upper;witness=None
 qa=v2[e2[:,0]];qb=v2[e2[:,1]];v=qb-qa;c=(v*v).sum(axis=1);qmin=np.minimum(qa,qb);qmax=np.maximum(qa,qb)
 for ids in np.array_split(np.arange(len(e1)),max(1,len(e1)//64)):
  pa=v1[e1[ids,0]];pb=v1[e1[ids,1]];pmin=np.minimum(pa,pb);pmax=np.maximum(pa,pb)
  gap=np.maximum(0,np.maximum(pmin[:,None,:]-qmax[None,:,:],qmin[None,:,:]-pmax[:,None,:]));ii,jj=np.where((gap*gap).sum(axis=2)<=best*best)
  if not len(ii):continue
  p0=pa[ii];u=pb[ii]-p0;q0=qa[jj];vv=v[jj];w=p0-q0;a=(u*u).sum(axis=1);cc=c[jj];b=(u*vv).sum(axis=1);d=(u*w).sum(axis=1);e=(vv*w).sum(axis=1)
  aa=np.maximum(a,1e-30);ccs=np.maximum(cc,1e-30)
  # The constrained minimum is either interior/interior or one of the four endpoint-to-opposing-segment cases.
  cand=[(np.zeros(len(ii)),np.clip(e/ccs,0,1)),(np.ones(len(ii)),np.clip((e+b)/ccs,0,1)),(np.clip(-d/aa,0,1),np.zeros(len(ii))),(np.clip((b-d)/aa,0,1),np.ones(len(ii)))]
  den=a*cc-b*b;valid=den>1e-25;ss=np.zeros(len(ii));tt=ss.copy();ss[valid]=(b[valid]*e[valid]-cc[valid]*d[valid])/den[valid];tt[valid]=(a[valid]*e[valid]-b[valid]*d[valid])/den[valid];valid&=(ss>=0)&(ss<=1)&(tt>=0)&(tt<=1)
  cand.append((ss,tt))
  for n,(s,t) in enumerate(cand):
   ds=((w+s[:,None]*u-t[:,None]*vv)**2).sum(axis=1)
   if n==4:ds[~valid]=np.inf
   j=int(np.argmin(ds));dist=math.sqrt(float(ds[j]))
   if dist<best:best=dist;witness={'rib_point':(p0[j]+s[j]*u[j]).tolist(),'white_point':(q0[j]+t[j]*vv[j]).tolist(),'type':'edge_edge'}
 return best,witness

white=getgeom(bpy.data.objects['White_sphere_under_table']);wv,wt,we,wb=white
out={'candidate_blend_sha256':hashlib.sha256((D/'Terrace_RightRearTable_Rebuilt_20261011.blend').read_bytes()).hexdigest(),'method':'Evaluated triangulated world-space surfaces. BVH triangle intersection query; nearest vertex-to-triangle in both directions; all unique triangulated edge pairs checked for closest segment points after conservative AABB lower-bound pruning. This covers curved strip segments, surface interiors, edges and vertices, rather than vertices only.','units':'Blender scene units','white_evaluated_vertices':len(wv),'white_evaluated_triangles':len(wt),'rib_checks':[]}
for o in sorted([o for o in bpy.data.objects if o.name.startswith('Side_table_flat_rib_')],key=lambda o:o.name):
 v,t,e,b=getgeom(o);over=b.overlap(wb);best=math.inf;wit=None
 for p in v:
  co,no,ix,dist=wb.find_nearest(Vector(p))
  if dist<best:best=dist;wit={'rib_point':p.tolist(),'white_point':list(co),'type':'rib_vertex_white_triangle'}
 for p in wv:
  co,no,ix,dist=b.find_nearest(Vector(p))
  if dist<best:best=dist;wit={'rib_point':list(co),'white_point':p.tolist(),'type':'white_vertex_rib_triangle'}
 best,ew=closest_edges(v,e,wv,we,best)
 if ew:wit=ew
 r={'object':o.name,'intersection_pairs':len(over),'min_surface_separation':0.0 if over else best,'closest_points':wit,'evaluated_vertices':len(v),'evaluated_triangles':len(t)};out['rib_checks'].append(r);print(json.dumps(r),flush=True)
out['minimum_separation']=min(r['min_surface_separation'] for r in out['rib_checks']);out['no_rib_white_surface_intersection']=all(r['intersection_pairs']==0 for r in out['rib_checks'])
(D/'independent_surface_separation_qa.json').write_text(json.dumps(out,indent=2));print('SURFACE_DONE',flush=True)
