from PIL import Image,ImageFilter
import numpy as np,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/textures';n=512;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(81)
for name,col,typ in [('violet_masonry',(.24,.21,.34),'brick'),('aged_limestone',(.47,.43,.42),'stone'),('purple_paving',(.21,.10,.20),'pave'),('dark_wood',(.14,.052,.075),'wood'),('cyan_glass',(.06,.38,.47),'glass'),('leaf',(.13,.22,.055),'leaf')]:
 noise=rng.normal(0,.025,(n,n));h=.6+noise
 if typ=='brick':h-=.35*((y%42<3)|((x+(y//42%2)*64)%128<3))
 if typ=='pave':h-=.33*((y%128<5)|((x+(y//128%2)*128)%256<5));h+=.04*np.sin(x/12+y/17)
 if typ=='stone':h+=.08*np.sin(x/13)*np.sin(y/19)
 if typ=='wood':h+=.06*np.sin(x*.4+np.sin(y*.015)*2)
 if typ=='glass':h+=.06*np.sin(x/6)*np.sin(y/7)
 if typ=='leaf':h+=.05*np.sin(x/8)
 v=np.array(col)[None,None,:]*(.55+h[...,None]);Image.fromarray(np.uint8(np.clip(v,0,1)*255)).save(R+'/'+name+'_basecolor.png')
 Image.fromarray(np.uint8(np.clip(.72+noise if typ!='glass' else .25+noise,0,1)*255)).save(R+'/'+name+'_roughness.png')
 gy,gx=np.gradient(h);normal=np.dstack((.5-gx,.5-gy,np.ones_like(h)));Image.fromarray(np.uint8(np.clip(normal,0,1)*255)).save(R+'/'+name+'_normal.png')
