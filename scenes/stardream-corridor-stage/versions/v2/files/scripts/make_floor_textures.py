import numpy as np,pathlib,json,hashlib
from PIL import Image
from scipy.ndimage import gaussian_filter
P=pathlib.Path(__file__).resolve().parents[1];N=1024;rng=np.random.default_rng(8052024);noise=rng.standard_normal((N,N));broad=gaussian_filter(noise,24,mode='wrap');broad=(broad-broad.mean())/broad.std();medium=gaussian_filter(noise,3,mode='wrap');medium/=medium.std();fine=rng.standard_normal((N,N));y,x=np.mgrid[0:N,0:N]/N
# Periodic synthetic cellular hairlines, not sampled from source imagery.
centers=rng.random((28,2));d1=np.full((N,N),np.inf);d2=d1.copy()
for cy,cx in centers:
 dx=np.minimum(abs(x-cx),1-abs(x-cx));dy=np.minimum(abs(y-cy),1-abs(y-cy));d=np.sqrt(dx*dx+dy*dy);m=d<d1;d2=np.where(m,d1,np.minimum(d2,d));d1=np.minimum(d1,d)
veins=np.exp(-((d2-d1)/.0018)**2);base=np.clip(.24+.018*broad+.008*medium+.004*fine-.06*veins,.05,.4);rgb=np.stack([base*1.02,base,base*.94],axis=-1);rough=np.clip(.63+.035*medium+.03*veins,.4,.8);height=.12*medium-.35*veins;dy,dx=np.gradient(height);nx=-dx*.55;ny=-dy*.55;nz=np.ones_like(nx);nn=np.sqrt(nx*nx+ny*ny+nz*nz);norm=np.stack([nx/nn,ny/nn,nz/nn],-1)*.5+.5
files=[]
for name,arr in [('stone_diffuse.png',rgb),('stone_roughness.png',np.repeat(rough[:,:,None],3,axis=2)),('stone_normal.png',norm)]:
 p=P/'textures'/name;Image.fromarray(np.uint8(np.clip(arr,0,1)*255)).save(p);files.append({'path':'textures/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'size':[N,N]})
(P/'qa/R03-texture-manifest.json').write_text(json.dumps({'method':'Seeded periodic synthetic stone proxy; not photographs, not captured source texture, not depth map. RGB diffuse, linear roughness and tangent normal. Source grain/vein correspondence remains FAILED.','seed':8052024,'files':files},indent=2))
