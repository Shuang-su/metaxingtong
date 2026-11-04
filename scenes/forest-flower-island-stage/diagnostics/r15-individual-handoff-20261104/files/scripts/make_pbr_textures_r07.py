"""Deterministic original procedural color approximations, not extracted/baked source textures."""
import numpy as np,pathlib,json,hashlib
from scipy.ndimage import gaussian_filter
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];rng=np.random.default_rng(110406);N=1024;y,x=np.mgrid[:N,:N]/N
noise=gaussian_filter(rng.random((N,N)),8);noise=(noise-noise.min())/(noise.max()-noise.min());fine=rng.random((N,N))
channels={}
bark=.45+.25*np.sin(x*math if False else x*160+noise*9)+.12*fine
bark=np.clip(bark,0,1);channels['bark_color']=np.stack([.08+.19*bark,.065+.14*bark,.035+.075*bark],-1)
vein=np.exp(-((y-.5)/.018)**2)+.45*np.exp(-((np.mod(x*9+np.abs(y-.5)*8,1)-.5)/.08)**2)
g=.30+.20*noise+.12*vein;channels['leaf_color']=np.stack([.12+.12*noise+.04*vein,g,.025+.055*noise],-1)
channels['moss_color']=np.stack([.07+.12*noise,.13+.20*noise,.025+.065*noise],-1)
records=[]
for name,a in channels.items():
 a=np.clip(a,0,1);a=np.where(a<=.0031308,12.92*a,1.055*a**(1/2.4)-.055);p=ROOT/'textures'/(name+'-r07.png');Image.fromarray((a*255).astype('uint8')).save(p);b=p.read_bytes();records.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),size=[N,N],role='Original generated PBR approximation; not photograph and not original 3D shader baking'))
(ROOT/'textures/manifest-r07.json').write_text(json.dumps({'seed':110406,'color_space':'linear intended palette explicitly encoded to sRGB' ,'generator':'scripts/make_pbr_textures_r07.py','textures':records,'source_fidelity':'unaccepted approximation'},indent=2)+'\n')
