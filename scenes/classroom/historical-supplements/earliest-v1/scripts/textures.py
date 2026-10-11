from PIL import Image,ImageFilter
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'textures';R.mkdir(exist_ok=True)
rng=np.random.default_rng(4122024)
def tex(name,base,h,n=512,rough=.6,strength=2):
 base=np.clip(base,0,1);Image.fromarray(np.uint8(base*255)).save(R/(name+'_BaseColor.png'))
 if np.isscalar(rough):rough=np.clip(rough+rng.normal(0,.012,(n,n)),0,1)
 Image.fromarray(np.uint8(rough*255)).save(R/(name+'_Roughness.png'))
 dy,dx=np.gradient(h);nm=np.dstack((-dx*strength,-dy*strength,np.ones_like(h)));nm/=np.linalg.norm(nm,axis=2)[...,None];Image.fromarray(np.uint8((nm*.5+.5)*255)).save(R/(name+'_Normal.png'))
for name,c in [('Plaster',(.57,.67,.71)),('Chalkboard',(.075,.24,.175)),('Cork',(.60,.54,.40)),('Ceiling',(.77,.80,.79))]:
 n=512;y,x=np.mgrid[:n,:n];h=rng.normal(0,.025,(n,n));b=np.ones((n,n,3))*c+h[:,:,None]*.18
 if name=='Chalkboard':
  low=np.array(Image.fromarray(np.uint8(rng.random((32,32))*255)).resize((n,n),Image.Resampling.BICUBIC))/255-.5;b+=low[:,:,None]*.055
 tex(name,b,h,n,.83,1.5)
for name,n,c in [('DeskOak',1024,(.49,.28,.115)),('FloorOak',1024,(.57,.32,.14))]:
 y,x=np.mgrid[:n,:n];warp=np.sin(y/n*17+x/n*3)*5+np.sin(y/n*5)*8
 grain=np.sin((x+warp)*.37)*.013+np.sin((x+warp)*1.8)*.008+rng.normal(0,.005,(n,n));grain+=np.sin((x+warp)*.043)*.025
 base=np.ones((n,n,3))*c+grain[:,:,None]
 if name=='FloorOak':
  plw=128
  for k in range(8):
   base[:,k*plw:(k+1)*plw]+=rng.uniform(-.028,.025)
   base[:,k*plw:k*plw+2]*=.42
   for yy in [int((k%3)*n/3),int((k%3)*n/3+n*.6)%n]:base[yy:yy+2,k*plw:(k+1)*plw]*=.5
 tex(name,base,grain,n,.45 if name=='DeskOak' else .56,2)
