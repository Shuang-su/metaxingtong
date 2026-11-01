from PIL import Image
import numpy as np,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[1];params=json.load(open(D/'qa/conditional_projection_parameters.json'));H=np.array(params['H_source_to_working_xz']);im=np.array(Image.open(D/'sources/BV1nxQPBkEGH_2522.827654_low_angle.png').convert('RGB'));mask=np.array(Image.open(D/'qa/LOW_LEFT_native_mask.png'));n=512
xx,zz=np.meshgrid(np.linspace(-.80465,.80465,n),np.linspace(4.45,2.88,n));world=np.stack([xx.ravel(),zz.ravel(),np.ones(n*n)])
res=[]
for name,scale,dx,dz in [('BASE',1,0,0),('STRESS_A',.95,-.05,-.05),('STRESS_B',1.05,.05,.05)]:
 w=world.copy();w[0]=(w[0]-dx)/scale;w[1]=(w[1]-3.665-dz)/scale+3.665;q=np.linalg.inv(H)@w;u=q[0]/q[2];v=q[1]/q[2];x=np.floor(u).astype(int);y=np.floor(v).astype(int);valid=(x>=0)&(x<1919)&(y>=0)&(y<1079);xc=x.clip(0,1918);yc=y.clip(0,1078)
 valid&=(mask[yc,xc]==1)&(mask[yc+1,xc]==1)&(mask[yc,xc+1]==1)&(mask[yc+1,xc+1]==1)
 a=(u-x)[:,None];b=(v-y)[:,None];c=(im[yc,xc]*(1-a)*(1-b)+im[yc,xc+1]*a*(1-b)+im[yc+1,xc]*(1-a)*b+im[yc+1,xc+1]*a*b).clip(0,255).astype(np.uint8)
 rgba=np.zeros((n*n,4),dtype=np.uint8);rgba[:,:3]=[53,61,69];rgba[valid,:3]=c[valid];rgba[valid,3]=255
 path=D/f'textures/DERIVED_PARTIAL_POSTER_{name}.png';Image.fromarray(rgba.reshape(n,n,4)).save(path);Image.fromarray((valid*255).astype(np.uint8).reshape(n,n)).save(D/f'textures/DERIVED_ALPHA_{name}.png');res.append({'variant':name,'scale':scale,'dx':dx,'dz':dz,'coverage_of_inferred_uv':float(valid.mean()),'rgba_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(D/'qa/derived_texture_manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256((D/'sources/BV1nxQPBkEGH_2522.827654_low_angle.png').read_bytes()).hexdigest(),'derived_not_native':True,'resolution':[n,n],'sampling':'bilinear RGB only if all 4 native mask neighbors ==1; otherwise alpha0 neutral missing; no inpaint/AI fill','surface_color':'source-lit photograph, not recovered intrinsic albedo','variants':res},indent=2))
