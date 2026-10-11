from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy.ndimage import gaussian_filter,maximum_filter,uniform_filter
from scipy.signal import correlate2d
R=Path(__file__).resolve().parents[1];V=R.parent/'castlehall_hd_verification_20261010/references'
a=np.asarray(Image.open(V/'hall_right_arch_4528_paused_core.png').convert('L'),float)/255;b=np.asarray(Image.open(V/'hall_right_arch_4529_natural_ui_clear_core.png').convert('L'),float)/255
ix=gaussian_filter(a,1,order=(0,1));iy=gaussian_filter(a,1,order=(1,0));xx=gaussian_filter(ix*ix,2);yy=gaussian_filter(iy*iy,2);xy=gaussian_filter(ix*iy,2);h=xx*yy-xy*xy-.05*(xx+yy)**2
mask=np.zeros(a.shape,bool);mask[8:285,745:863]=True
# Only static right-wall panel/moulding regions; balloons, character, UI and floor excluded.
peaks=(h==maximum_filter(h,11))&mask&(h>0);ys,xs=np.where(peaks);order=np.argsort(h[ys,xs])[::-1][:70]
matches=[]
for i in order:
 x,y=xs[i],ys[i];k=7;p=a[y-k:y+k+1,x-k:x+k+1];p=p-p.mean();pn=np.sqrt((p*p).sum())
 if pn<.1:continue
 # Prior displacement only defines a bounded match window, not image registration.
 dx=155;dy=15;radius=30;cx=x+dx;cy=y+dy;x0=max(k,cx-radius)-k;y0=max(k,cy-radius)-k;x1=min(1180-k,cx+radius)+k;y1=min(664-k,cy+radius)+k
 crop=b[y0:y1,x0:x1];corr=correlate2d(crop,p,mode='valid');ones=np.ones(p.shape);sm=correlate2d(crop,ones,mode='valid');sq=correlate2d(crop*crop,ones,mode='valid');den=np.sqrt(np.maximum(sq-sm*sm/p.size,1e-10))*pn;score=corr/den
 jy,jx=np.unravel_index(np.argmax(score),score.shape);best=score[jy,jx];xx=x0+jx+k;yy=y0+jy+k
 if best>.88:matches.append([int(x),int(y),int(xx),int(yy),float(best)])

def dlt(a,b):
 # maps a -> b; used only to classify consistent static-plane correspondences.
 A=[]
 for (x,y),(u,v) in zip(a,b):A.extend([[-x,-y,-1,0,0,0,u*x,u*y,u],[0,0,0,-x,-y,-1,v*x,v*y,v]])
 _,_,vt=np.linalg.svd(np.asarray(A));H=vt[-1].reshape(3,3);return H/H[2,2]
x=np.array([m[:2] for m in matches]);y=np.array([m[2:4] for m in matches]);rng=np.random.default_rng(11);best=[]
for t in range(300):
 try:
  j=rng.choice(len(x),4,replace=False);H=dlt(x[j],y[j]);q=np.c_[x,np.ones(len(x))]@H.T;q=q[:,:2]/q[:,2:];ins=np.where(np.linalg.norm(q-y,axis=1)<2)[0]
  if len(ins)>len(best):best=ins
 except:pass
H=dlt(x[best],y[best]);q=np.c_[x,np.ones(len(x))]@H.T;q=q[:,:2]/q[:,2:];err=np.linalg.norm(q-y,axis=1);best=np.where(err<2)[0]
result={'method':'Harris corners and 15x15 normalized cross-correlation patches in explicit static wall masks. Plane homography used only for correspondence outlier rejection, not to warp reference images.','matches':[matches[i] for i in best],'detected':len(order),'matched':len(matches),'inliers':len(best),'plane_reprojection_px':[float(err[i]) for i in best]};(R/'qa/static_wall_patch_matches.json').write_text(json.dumps(result,indent=2));print('inliers',len(best),'median plane residual',np.median(err[best]))
im=Image.new('RGB',(2360,664));im.paste(Image.open(V/'hall_right_arch_4528_paused_core.png'),(0,0));im.paste(Image.open(V/'hall_right_arch_4529_natural_ui_clear_core.png'),(1180,0));d=ImageDraw.Draw(im)
for n,i in enumerate(best):
 x,y,u,v,_=matches[i];d.ellipse((x-3,y-3,x+3,y+3),outline='cyan');d.ellipse((u+1177,v-3,u+1183,v+3),outline='cyan')
im.save(R/'qa/static_wall_correspondences.jpg',quality=94)
