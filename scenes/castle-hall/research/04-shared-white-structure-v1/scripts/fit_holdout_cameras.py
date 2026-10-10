from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math
from scipy.signal import correlate2d
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[1];V=R.parent/'castlehall_hd_verification_20261010/references'
exec((R/'scripts/fit_source_cameras.py').read_text().split('out={}')[0])
V=R.parent/'castlehall_hd_verification_20261010/references'
a=np.asarray(Image.open(V/'hall_right_arch_4528_paused_core.png').convert('L'),float)/255
b=np.asarray(Image.open(R/'inputs/holdout_arch_4527_paused_core.png').convert('L'),float)/255
mp=json.loads((R/'qa/static_wall_patch_matches.json').read_text())['matches'];p28=np.array(json.loads((R/'qa/planar_camera_fit_4528.json').read_text())['parameters']);matches=[]
for x,y,_,_,_ in mp:
 k=8;orig=a[y-k:y+k+1,x-k:x+k+1];best=(-1,None,None,None)
 for scale in [.9,1,1.1,1.2,1.3,1.4]:
  n=int(round(17*scale));n=n if n%2 else n+1;p=np.asarray(Image.fromarray(np.float32(orig),mode='F').resize((n,n),Image.Resampling.BILINEAR),float);p-=p.mean();pn=np.linalg.norm(p);kk=n//2
  cx=x+100;cy=y+45;radius=65;x0=max(kk,cx-radius)-kk;y0=max(kk,cy-radius)-kk;x1=min(1180-kk,cx+radius)+kk;y1=min(664-kk,cy+radius)+kk
  crop=b[y0:y1,x0:x1];one=np.ones(p.shape);corr=correlate2d(crop,p,mode='valid');sm=correlate2d(crop,one,mode='valid');sq=correlate2d(crop*crop,one,mode='valid');score=corr/(np.sqrt(np.maximum(sq-sm*sm/p.size,1e-10))*pn);jy,jx=np.unravel_index(score.argmax(),score.shape)
  if score[jy,jx]>best[0]:best=(score[jy,jx],x0+jx+kk,y0+jy+kk,scale)
 if best[0]>.84:matches.append([x,y,int(best[1]),int(best[2]),float(best[0]),best[3]])
def dlt(a,b):
 A=[]
 for (x,y),(u,v) in zip(a,b):A.extend([[-x,-y,-1,0,0,0,u*x,u*y,u],[0,0,0,-x,-y,-1,v*x,v*y,v]])
 _,_,vt=np.linalg.svd(np.asarray(A));H=vt[-1].reshape(3,3);return H/H[2,2]
x=np.array([m[:2] for m in matches]);y=np.array([m[2:4] for m in matches]);rng=np.random.default_rng(22);best=[]
for t in range(500):
 try:
  j=rng.choice(len(x),4,replace=False);H=dlt(x[j],y[j]);q=np.c_[x,np.ones(len(x))]@H.T;q=q[:,:2]/q[:,2:];ins=np.where(np.linalg.norm(q-y,axis=1)<2.2)[0]
  if len(ins)>len(best):best=ins
 except:pass
x=x[best];y=y[best];M,C,f=matrix(p28);dirs=np.stack(((x[:,0]-590)/f,(332-x[:,1])/f,np.ones(len(x))),axis=-1)@M;t=(7-C[0])/dirs[:,0];world=C+dirs*t[:,None]
def res(p):return np.r_[(project(world,p)-y).ravel(),(p[-1]-p28[-1])/100,p[5]/.1,(p[2]-p28[2])*2]
sol=least_squares(res,p28,bounds=([-7,-18,.3,-.1,-.4,-.15,450],[5,3,4,1.6,.4,.15,2000]),max_nfev=2000);p=sol.x;M,C,f=matrix(p);err=np.linalg.norm(project(world,p)-y,axis=1)
out={'role':'Held-out geometry view; camera calibrated using unchanged planar wall ornaments only, never arch/tread geometry. No geometry feedback from this frame. Nearby motion frame, not independent calibrated baseline.','source':'inputs/holdout_arch_4527_paused_core.png','time':4527.768968,'parameters':p.tolist(),'location':C.tolist(),'right':M[0].tolist(),'up':M[1].tolist(),'forward':M[2].tolist(),'focal_pixels':float(f),'lens_mm':float(f*36/1180),'matches':np.c_[x,y].tolist(),'points':len(x),'wall_feature_median_px':float(np.median(err)),'wall_feature_max_px':float(max(err))}
(R/'qa/holdout_camera_4527.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
im=Image.new('RGB',(2360,664));im.paste(Image.open(V/'hall_right_arch_4528_paused_core.png'),(0,0));im.paste(Image.open(R/'inputs/holdout_arch_4527_paused_core.png'),(1180,0));d=ImageDraw.Draw(im)
for (xx,yy),(u,v) in zip(x,y):d.ellipse((xx-3,yy-3,xx+3,yy+3),outline='cyan');d.ellipse((u+1177,v-3,u+1183,v+3),outline='cyan')
im.save(R/'qa/holdout_wall_camera_correspondences.jpg',quality=93)
