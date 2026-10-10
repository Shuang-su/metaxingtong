from PIL import Image,ImageFilter
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];T=R/'textures';N=512;rng=np.random.default_rng(71110)
y,x=np.mgrid[:N,:N]/N
# Authored tileable mathematical PBR surfaces, no scene photographs.
def noise(freq):
 z=np.zeros((N,N))
 for i in range(12):
  a,b=rng.integers(-freq,freq+1,2);z+=np.sin(2*np.pi*(a*x+b*y)+rng.random()*6.28)/(i+3)
 return z
n=noise(5);fine=noise(32)
def save(stem,base,rough,field,normals=.6):
 field=field-field.mean();v=np.array(base)[None,None,:]+field[:,:,None]
 Image.fromarray(np.uint8(np.clip(v,0,255))).save(T/f'{stem}_BaseColor.png',optimize=True)
 Image.fromarray(np.uint8(np.clip(rough+field*.26,0,255))).save(T/f'{stem}_Roughness.png',optimize=True)
 gy,gx=np.gradient(field);v=np.stack((-gx*normals*.04,-gy*normals*.04,np.ones((N,N))),2);v/=np.linalg.norm(v,axis=2)[:,:,None]
 Image.fromarray(np.uint8(np.clip((v*.5+.5)*255,0,255))).save(T/f'{stem}_Normal.png',optimize=True)
vein=np.sin(2*np.pi*(4*x+2*y)+n*5+.25*fine);veins=(np.exp(-abs(vein)*24)+.38*np.exp(-abs(np.sin(2*np.pi*(9*x-7*y)+n*8))*34))
save('IvoryMarble',(218,197,164),54,n*8-veins*55+fine*1.3,.25)
save('DarkMarble',(56,39,40),65,n*7+veins*39,.22)
save('RoseStone',(162,118,100),146,n*8+fine*1.2,.25)
save('Plaster',(127,86,94),195,n*4+fine*.7,.20)
weave=np.sin(2*np.pi*x*200)*np.sin(2*np.pi*y*200)
save('IvoryLinen',(230,217,195),214,n*1.5+weave*2.2,.9)
save('AntiqueGold',(157,104,48),97,n*5+fine*1.1,.23)
print('TEXTURES_READY')
