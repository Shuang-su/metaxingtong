from PIL import Image,ImageFilter
import numpy as np,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/textures';n=512;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(9)
for name,col,typ in [('warm_deck',(.48,.28,.16),'wood'),('wall_cedar',(.45,.235,.13),'wood'),('tree_bark',(.12,.085,.061),'bark'),('white_wicker',(.83,.82,.75),'woven'),('linen',(.88,.87,.81),'cloth'),('gravel',(.8,.8,.76),'stone'),('autumn_gold',(.80,.40,.065),'leaf'),('autumn_yellow',(.89,.64,.17),'leaf'),('green_leaf',(.16,.27,.075),'leaf'),('moon',(.93,.72,.32),'moon')]:
 h=.5+rng.normal(0,.025,(n,n));rough=.7
 if typ=='wood':h+=.07*np.sin(x*.3+np.sin(y*.025)*1.8)+.028*np.sin(x*1.3+np.sin(y*.02)*2)
 if typ=='bark':h+=.17*np.sin(x*.16+np.sin(y*.026)*1.2)+.04*np.sin(x*.8)
 if typ=='woven':h+=.13*np.sin(x*.6)*np.sin(y*.6)
 if typ=='cloth':h+=.045*np.sin(x*2)*np.sin(y*2)
 if typ=='leaf':h+=.05*np.cos(y*.08)+.09*np.exp(-((x-256)/6)**2)
 if typ=='stone':h+=.08*np.sin(x*.6)*np.cos(y*.4)
 if typ=='moon':
  rough=.8
  for _ in range(65):
   xx,yy=rng.uniform(0,n,2);rr=rng.uniform(6,65);h-=rng.uniform(.07,.23)*np.exp(-((x-xx)**2+(y-yy)**2)/(rr**2))
 col=np.array(col);v=col[None,None,:]*(.66+h[...,None]*.7);Image.fromarray(np.uint8(np.clip(v,0,1)*255)).save(R+'/'+name+'_basecolor.png')
 Image.fromarray(np.uint8(np.clip(rough+(h-.5)*.12,0,1)*255)).save(R+'/'+name+'_roughness.png')
 gy,gx=np.gradient(h);nm=np.dstack((.5-gx*.7,.5-gy*.7,np.ones_like(h)));Image.fromarray(np.uint8(np.clip(nm,0,1)*255)).save(R+'/'+name+'_normal.png')
