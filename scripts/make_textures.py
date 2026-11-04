import numpy as np
from PIL import Image,ImageFilter
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1]/'textures';P.mkdir(exist_ok=True)
rng=np.random.default_rng(1104)
def noise(w,h,grid):
 a=rng.random((grid,max(2,int(grid*w/h))))
 return np.asarray(Image.fromarray(np.uint8(a*255)).resize((w,h),Image.Resampling.BICUBIC),dtype=float)/255
w,h=1024,512
x,y=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h))
n=.55*noise(w,h,6)+.23*noise(w,h,21)+.15*noise(w,h,58)+.07*noise(w,h,180)
base=np.zeros((h,w,3));base[:,:,0]=.08+.24*n;base[:,:,1]=.20+.46*n;base[:,:,2]=.014+.07*n
# Subtle fine irregular tissue/tertiary venation. Primary and secondary veins are geometry.
fine=np.maximum(0,np.cos((y*42+x*7+noise(w,h,32)*.7)*np.pi))**24
base+=fine[:,:,None]*np.array([.018,.027,.004])
Image.fromarray(np.uint8(np.clip(base,0,1)*255)).save(P/'leaf-tissue-albedo.png')
Image.fromarray(np.uint8((.34+.20*noise(w,h,80))*255)).save(P/'leaf-tissue-roughness.png')
w=h=1024
n=.65*noise(w,h,7)+.25*noise(w,h,19)+.1*noise(w,h,45)
c=np.zeros((h,w,3));c[:,:,0]=.014+.008*n;c[:,:,1]=.10+.28*n;c[:,:,2]=.16+.32*n
Image.fromarray(np.uint8(c*255)).save(P/'lake-colour-hypothesis.png')
w=h=512
x,y=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));n=noise(w,h,48)
z=.002*np.sin(2*np.pi*(x*14+y*3+n*.32))+.001*np.sin(2*np.pi*(y*20-x*6+n*.17))
gy,gx=np.gradient(z);norm=np.stack([-gx*80,-gy*80,np.ones_like(z)],axis=2);norm/=np.linalg.norm(norm,axis=2)[:,:,None]
Image.fromarray(np.uint8((norm*.5+.5)*255)).save(P/'water-wave-normal.png')
report={'generator':'scripts/make_textures.py','seed':1104,'role':'Original procedural reconstruction textures; not source footage, not depth or hidden geometry evidence','files':[]}
for f in P.glob('*.png'):report['files'].append({'path':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':Image.open(f).size})
(P/'texture-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
