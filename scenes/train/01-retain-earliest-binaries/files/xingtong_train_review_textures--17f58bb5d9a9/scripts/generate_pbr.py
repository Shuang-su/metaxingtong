from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parents[1]/'textures';R.mkdir(exist_ok=True)
rng=np.random.default_rng(2703);N=1024;y,x=np.mgrid[0:N,0:N].astype(float)/N

def noise(scale=4):return gaussian_filter(rng.random((N,N)).astype(np.float32),scale,mode='wrap')
def save(stem,base,height,rough,strength=2):
 a=np.clip(base,0,1);Image.fromarray((a*255).astype('uint8')).save(R/f'{stem}_basecolor.png')
 Image.fromarray((np.clip(rough,0,1)*255).astype('uint8')).save(R/f'{stem}_roughness.png')
 dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*strength;dy=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*strength
 norm=np.stack([-dx,-dy,np.ones_like(dx)],-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
 Image.fromarray(((norm*.5+.5)*255).astype('uint8')).save(R/f'{stem}_normal.png')
# Original authored seamless-ish physically motivated microstructure maps; no reference image projection.
grain=np.sin(2*np.pi*(x*40+1.8*np.sin(y*2*np.pi)+.45*np.sin(y*16*np.pi)))
fine=noise(.8)-.5;g=(grain*.025+(noise((12,1))-.5)*.7+fine*.12)
base=np.stack([.255+g,.128+g*.52,.065+g*.28],-1);save('walnut',base,grain*.1+fine*.3,.40+fine*.12,2)
grain2=np.sin(2*np.pi*(x*63+.8*np.sin(y*2*np.pi)))
g=grain2*.018+(noise((12,1))-.5)*.55+fine*.1;save('rosewood',np.stack([.34+g,.145+g*.47,.09+g*.30],-1),grain2*.08+fine*.4,.38+fine*.1,2)
# Pebbled hide via multiple frequencies and irregular shallow cells.
h=noise(1.6);h=(h-h.min())/(h.max()-h.min());pebbles=np.maximum(0,.54-h);fine=noise(.3)-.5;g=(h-.5)*.055
save('forest_leather',np.stack([.041+g*.45,.096+g,.069+g*.70],-1),pebbles*2+fine*.11,.24+(h-.5)*.10,5)
weave=np.sin(x*N*np.pi/2)*np.sin(y*N*np.pi/3)*.035+(noise(.3)-.5)*.04
save('burgundy_velvet',np.stack([.29+weave,.032+weave*.25,.036+weave*.25],-1),weave,.86+weave*.5,2)
fine=noise(.3)-.5;save('ceiling_cream',np.stack([.69+fine*.02,.57+fine*.02,.38+fine*.02],-1),fine*.12,.75+fine*.06,1)
# Small-scale floor fleck with long narrow plank line; color intentionally restrained.
g=noise((3,.5))-.5;line=(x>.989)*-.11
save('floor_wood',np.stack([.19+g*.1+line,.095+g*.055+line*.5,.052+g*.028+line*.25],-1),g*.18+line,.36+g*.15,1.5)
print('18 PBR bitmap maps written',R)
