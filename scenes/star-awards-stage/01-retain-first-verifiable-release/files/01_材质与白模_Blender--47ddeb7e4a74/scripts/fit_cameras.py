import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pathlib import Path
P=Path(__file__).resolve().parents[1]
# Middle dark star outer silhouette; source pixels measured manually, occluded tips excluded.
obs={
'C':{1:[622,81],2:[906,61],3:[694,235],4:[747,474],6:[363,474],7:[416,235],8:[205,61],9:[488,81]},
'A':{1:[937,139],2:[1165,73],3:[970,280],4:[992,514],6:[638,500],7:[711,286],8:[464,118],9:[785,150]},
'B':{1:[193,113],2:[558,53],3:[294,263],4:[356,470],5:[161,367]}}
# Approximate correspondence points must be reviewed in overlays, not interpreted as metric truth.
def star(k):
 a=np.arange(10)*np.pi/5;r=np.where(np.arange(10)%2==0,3.,1.35)
 x=r*np.sin(a);z=2.427+r*np.cos(a);y=4-k*np.abs(x)
 return np.stack([x,y,z],1)
def proj(v,c):
 x,y,z,tx,tz,f,roll=c
 pos=np.array([x,y,z]);tar=np.array([tx,3,tz]);forward=tar-pos;forward/=np.linalg.norm(forward)
 right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward)
 R=np.stack([right,up,forward]);q=(v-pos)@R.T
 uv=q[:,:2]/q[:,2,None];co,si=np.cos(roll),np.sin(roll);uv=uv@np.array([[co,-si],[si,co]])
 return np.stack([590+f*uv[:,0],331.5-f*uv[:,1]],1)
order=['C','A','B'];init=[.65]+[0,-6,2,0,2.6,700,0]+[-3,-6,2,0,2.5,700,0]+[3,-6,2,0,2.5,700,0]
lo=[0]+[-8,-18,.2,-4,.1,350,-.2]*3;hi=[1.6]+[8,-2,6,4,5,1800,.2]*3

def residual(p):
 vv=star(p[0]);out=[]
 for j,key in enumerate(order):
  c=p[1+7*j:8+7*j];uv=proj(vv,c)
  for idx,pix in obs[key].items():out.extend((uv[idx]-pix))
 # Weak frontward cameras; no vanishing point metric claim.
 out.append((p[6]-900)*0.1)
 return out
r=least_squares(residual,init,bounds=(lo,hi),max_nfev=10000,loss='soft_l1',f_scale=12)
report={'k':r.x[0],'star_R':3,'star_inner':1.35,'star_center_z':2.427,'definition':'Folded shared star, dimensionless units; sparse hand-selected silhouette fit, not global fidelity validation.','cameras':{},'observations':obs}
for j,key in enumerate(order):
 c=r.x[1+7*j:8+7*j];uv=proj(star(r.x[0]),c);err=[np.linalg.norm(uv[idx]-pix) for idx,pix in obs[key].items()]
 report['cameras'][key]={'params':c.tolist(),'predicted':uv.tolist(),'mean_sparse_error_px':float(np.mean(err)),'max_sparse_error_px':float(max(err))}
print(json.dumps(report,indent=2));(P/'qa/camera_fit.json').write_text(json.dumps(report,indent=2))
from PIL import Image,ImageDraw
for key in order:
 im=Image.open(P/f'references/{key}_source.png').convert('RGB');d=ImageDraw.Draw(im);uv=report['cameras'][key]['predicted']
 for i in range(10):d.line([tuple(uv[i]),tuple(uv[(i+1)%10])],fill='cyan',width=3);d.text(tuple(uv[i]),str(i),fill='yellow')
 for i,p in obs[key].items():d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),outline='red',width=2)
 im.save(P/f'qa/{key}_landmark_fit.jpg')
