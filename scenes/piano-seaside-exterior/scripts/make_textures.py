from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]/'textures';root.mkdir(exist_ok=True)
r=np.random.default_rng(20261029);h,w=512,1024
y,x=np.mgrid[0:h,0:w];grain=np.sin(y*.43+np.sin(x*.025)*2)+.4*np.sin(y*1.1+x*.002);noise=r.normal(0,1,(h,w));v=np.clip(.56+grain*.055+noise*.028,0,1)
for center in [(260,170),(700,340)]:
 d=np.sqrt(((x-center[0])*.27)**2+(y-center[1])**2);v-=np.exp(-d/13)*.2
rgb=np.clip(v[...,None]*np.array([105,72,48])[None,None,:],0,255).astype('uint8');Image.fromarray(rgb).save(root/'deck_color.png');Image.fromarray(np.clip(210+noise*8+grain*4,0,255).astype('uint8')).save(root/'deck_roughness.png')
