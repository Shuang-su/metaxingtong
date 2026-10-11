from PIL import Image
import numpy as np, os
root=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'textures')
rng=np.random.default_rng(513)
n=1024;y,x=np.mgrid[:n,:n]
noise=rng.normal(0,1,(n,n)); weave=(np.sin(x*np.pi/2)+np.sin(y*np.pi/2))*.5
fine=noise*.045+weave*.025
base=np.zeros((n,n,3));base[:]=(.53,.62,.76);base+=fine[...,None]
Image.fromarray(np.uint8(np.clip(base,0,1)*255)).save(root+'/silver_fabric_basecolor.png')
rough=np.clip(.3+noise*.035+weave*.02,.19,.48)
Image.fromarray(np.uint8(np.clip(np.uint8(rough*255).astype(np.int16)+28,0,255))).save(root+'/silver_fabric_roughness.png')
dx=np.gradient(fine,axis=1)*.45;dy=np.gradient(fine,axis=0)*.45
normal=np.dstack((.5-dx,.5-dy,np.ones((n,n))))
Image.fromarray(np.uint8(np.clip(normal,0,1)*255)).save(root+'/silver_fabric_normal.png')
for name,col in [('speaker_grille',(0.032,.037,.05)),('stage_dark',(.024,.027,.07))]:
 v=np.empty((512,512,3));v[:]=col
 if name=='speaker_grille':
  yy,xx=np.mgrid[:512,:512];holes=((xx%8-3.5)**2+(yy%8-3.5)**2)<5;v[holes]*=.18
 else:v+=rng.normal(0,.002,v.shape)
 Image.fromarray(np.uint8(np.clip(v,0,1)*255)).save(root+'/'+name+'.png')
