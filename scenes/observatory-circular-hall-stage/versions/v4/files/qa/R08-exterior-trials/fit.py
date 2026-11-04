import json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull
from pathlib import Path
P=Path(__file__).parent
G=json.load(open(P/'geometry.json')); A={x['id']:x for x in json.load(open(P.parent/'observatory-source15-camera-diagnostic-20261104/annotations.json'))['annotations']}
# Actual finite wall and column vertices. Convex envelope is a conditional silhouette,
# not an occlusion proof nor a correspondence to any named column.
V=np.concatenate([np.array(o['vertices']) for n,o in G['objects'].items() if n.startswith(('WALL_','COLUMN_'))])
xy=np.unique(V[:,:2].round(7),axis=0); xy=xy[ConvexHull(xy).vertices]
V=np.array([[x,y,z] for x,y in xy for z in [.4,5.5]])
S=np.array(G['objects']['ROOF_centre_spire']['vertices']); tip=S[np.abs(S[:,2]-S[:,2].max())<1e-5].mean(0)
obs=np.array(A['L05']['pixels']+A['L06']['pixels']); target=np.array(A['P01']['pixels'])
def matrix(p):
 y,z,yaw,pitch,roll=p; f=np.array([np.sin(yaw)*np.cos(pitch),np.cos(yaw)*np.cos(pitch),np.sin(pitch)])
 r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
 return np.array([0,y,z]),np.column_stack([r*np.cos(roll)+u*np.sin(roll),u*np.cos(roll)-r*np.sin(roll),-f])
def project(v,p,lens):
 c,r=matrix(p);v=(v-c)@r;d=-v[:,2]
 if d.min()<=0:raise ValueError('behind camera')
 return np.column_stack([596+1192*lens/36*v[:,0]/d,335.5-1192*lens/36*v[:,1]/d]),d

def residual(p,lens,detail=False):
 q,d=project(V,p,lens);h=ConvexHull(q).vertices; edges=[]
 for i,j in zip(h,np.roll(h,-1)):
  if np.linalg.norm(V[i,:2]-V[j,:2])<1e-6:edges.append((q[i],q[j]))
 if len(edges)<2: return np.ones(10)*10000
 # left/right separately, without letting a left sample snap to right edge
 edges.sort(key=lambda ab:float((ab[0][0]+ab[1][0])/2)); ee=[edges[0],edges[-1]]
 errors=[]
 for k,pt in enumerate(obs):
  a,b=ee[k//4];t=np.clip(np.dot(pt-a,b-a)/np.dot(b-a,b-a),0,1);errors.append(float(np.linalg.norm(pt-(a+t*(b-a)))))
 t,_=project(tip[None],p,lens);r=np.r_[np.array(errors)/4,(t[0]-target)/3]
 if detail:return dict(wall_errors_px=errors,tip_error_px=float(np.linalg.norm(t[0]-target)),tip_projection=t[0].tolist(),edges=[[a.tolist(),b.tolist()] for a,b in ee],minimum_wall_depth=float(d.min()),camera_position=matrix(p)[0].tolist(),camera_rotation=matrix(p)[1].tolist())
 return r
M=np.array(G['camera']['matrix_world']);f=-M[:3,2];initial=np.array([-24,11,np.arctan2(f[0],f[1]),np.arctan2(f[2],np.linalg.norm(f[:2])),0])
if __name__ == "__main__":
 out={'scope':'Conditional camera-only training on L05/L06 wall-column convex silhouette and P01 top-cap centre. Fixed camera x=0 is an explicit front-axis hypothesis. Manual 4/3px scales are not statistical sigma. No visibility proof. All other annotations retained as diagnostics, not trained. Geometry unchanged.','model_sha256':G['model_sha256'],'baseline':residual(initial,18,True),'trials':[]}
 for lens in [12,18,24,35,50]:
  seed=initial.copy();seed[:2]=[min(-12.01,-24*lens/18),max(1.01,7+(11-7)*lens/18)]
  sol=least_squares(lambda p:residual(p,lens),seed,bounds=([-100,1,-.5,-.6,-.08],[-12,30,.5,.2,.08]),max_nfev=1800,xtol=1e-11,ftol=1e-11,gtol=1e-11)
  out['trials'].append(dict(lens=lens,parameters=sol.x.tolist(),cost=float(sol.cost),success=bool(sol.success),evaluations=sol.nfev,**residual(sol.x,lens,True)))
  print(lens,sol.cost,sol.x,flush=True)
 json.dump(out,open(P/'trials.json','w'),indent=2)
