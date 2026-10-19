from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parents[2];P=R/'c29';old=json.load(open(R/'c29_diagnosis/c28_curtain_mesh_readonly.json'));v=np.array(old['verts_local']);mat=np.array(old['matrix_world']);cams=json.load(open(R/'c27/blinds_projection_source.json'))['cameras']
def crossings(A,B,same=False):
 p=A[:-1,None,:];r=(A[1:]-A[:-1])[:,None,:];q=B[None,:-1,:];s=(B[1:]-B[:-1])[None,:,:];cr=lambda x,y:x[...,0]*y[...,1]-x[...,1]*y[...,0];den=cr(r,s);g=np.abs(den)>1e-12;t=np.divide(cr(q-p,s),den,out=np.zeros_like(den),where=g);u=np.divide(cr(q-p,r),den,out=np.zeros_like(den),where=g);hit=g&(t>1e-7)&(t<1-1e-7)&(u>1e-7)&(u<1-1e-7)
 if same:hit&=np.abs(np.arange(len(A)-1)[:,None]-np.arange(len(B)-1)[None,:])>1
 return int(hit.sum())
out={}
for kind in ['MATERIAL','WHITE']:
 w=np.array(json.load(open(P/(kind+'_actual_curtain_vertices.json'))));checks=[]
 for row in range(65):
  a=w[row*225:(row+1)*225,:2];b=w[14625+row*225:14625+(row+1)*225,:2];checks.append([crossings(a,b),crossings(a,a,True),crossings(b,b,True)])
 assert np.max(checks)==0
 A=np.c_[v,np.ones(len(v))]@mat.T;B=np.c_[w,np.ones(len(w))]@mat.T;entry={'all_65_sections_crossing_counts':checks,'world_bounds_before':[A[:,:3].min(0).tolist(),A[:,:3].max(0).tolist()],'world_bounds_after':[B[:,:3].min(0).tolist(),B[:,:3].max(0).tolist()],'views':{}}
 for k in ['H','G','N642','665']:
  polys=[]
  for V in [A,B]:
   q=V@np.array(cams[k]['projection']).T;a=q[:,:2]/q[:,3:4];uv=np.c_[(a[:,0]+1)*960,(1-a[:,1])*540];polys.append(uv[ConvexHull(uv).vertices])
  dif=[]
  for y in range(1080):
   b=[]
   for h in polys:
    xs=[a[0]+(c[0]-a[0])*(y-a[1])/(c[1]-a[1]) for a,c in zip(h,np.roll(h,-1,axis=0)) if min(a[1],c[1])<=y<=max(a[1],c[1]) and abs(a[1]-c[1])>1e-9];b.append(None if not xs else[min(xs),max(xs)])
   if all(x is not None for x in b):dif.append(np.max(np.abs(np.array(b[1])-b[0])))
  entry['views'][k]={'max_convex_outer_edge_shift_px':float(max(dif)) if dif else None,'valid_image_rows':len(dif),'limitation':'convex projected envelope, not raster occlusion or lighting guarantee'}
 out[kind]=entry
(P/'valid_geometry_verification.json').write_text(json.dumps(out,indent=2));print({k:v['views'] for k,v in out.items()})
