"""Deterministic authored material maps. No source-image pixels or AI enhancement."""
from pathlib import Path
import numpy as np, json, hashlib
from scipy.ndimage import gaussian_filter,map_coordinates
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'textures/r09';OUT.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(2026102909)
def noise(h,w,gy,gx):
 a=rng.random((gy,gx));yy,xx=np.mgrid[:h,:w];return map_coordinates(a,[yy/h*(gy-1),xx/w*gx],order=3,mode='grid-wrap')
def save(name,a):Image.fromarray(np.uint8(np.clip(a,0,1)*255)).save(OUT/name)
def normal(height,strength):
 dy,dx=np.gradient(height);n=np.stack([-dx*strength,-dy*strength,np.ones_like(dx)],-1);n/=np.linalg.norm(n,axis=-1,keepdims=True);return n*.5+.5
W,H=2048,1024;wood=np.zeros((H,W,3));height=np.zeros((H,W));rough=np.zeros((H,W))
for board in range(8):
 h=H//8;y,x=np.mgrid[:h,:W];base=noise(h,W,7,24);warp=10*(noise(h,W,8,20)-.5)+3*np.sin(x*.0025+board);phase=y*.92+warp
 grain=.46*np.sin(phase)+.20*np.sin(phase*2.73)+.12*np.sin(phase*6.81);knots=np.zeros_like(phase)
 for k in range(3):
  cx=rng.uniform(90,W-90);cy=rng.uniform(20,h-20);rad=np.sqrt(((x-cx)*.10)**2+((y-cy)*1.7)**2);fall=np.exp(-rad/25);knots+=fall*(.8*np.sin(rad*1.3)-.8*np.exp(-rad/8))
 scratches=np.zeros_like(phase)
 for k in range(30):
  cy=rng.uniform(0,h);cx=rng.uniform(0,W);length=rng.uniform(60,420);line=cy+1.5*np.sin(x*.009+k);scratches+=np.exp(-((y-line)/.46)**2)*np.exp(-((x-cx)/length)**6)*rng.uniform(.2,.7)
 micro=rng.normal(0,.018,(h,W));wear=np.exp(-np.minimum(y,h-1-y)/2)*.09
 tone=.53+.07*grain+.13*(base-.5)+.10*knots-.12*scratches+micro+wear
 tint=np.array([.72,.61,.49])*(.91+board*.022);wood[board*h:(board+1)*h]=tone[...,None]*tint+np.array([.045,.050,.054]);height[board*h:(board+1)*h]=grain*.075+knots*.05-scratches*.07+micro;rough[board*h:(board+1)*h]=np.clip(.79-.09*grain+.08*scratches+.05*(base-.5),.58,.96)
save('deck_weathered_color.png',wood);save('deck_weathered_roughness.png',rough);save('deck_weathered_normal.png',normal(height,2.0))
# Local finite shore: all visible prop supports stay on the -0.08 plateau.
def shore_z(x,y):
 shore=8.55+.18*np.sin(y*.67)+.08*np.sin(y*1.9)
 left=np.clip((x-2.5)/1.18,0,1);left=left*left*(3-2*left)
 wet=np.clip((x-7.35)/(shore-7.35),0,1);wet=wet*wet*(3-2*wet)
 end=np.clip((np.abs(y)-8.3)/3.7,0,1);end=end*end*(3-2*end)
 return -.08-.50*(1-left)-.48*wet-.45*end
h=w=1024;v,u=np.mgrid[:h,:w];xx=2.5+u/(w-1)*7.1;yy=-12+v/(h-1)*24;zz=shore_z(xx,yy);sandnoise=.55*noise(h,w,35,35)+.3*noise(h,w,130,130)+.15*rng.random((h,w));wet=np.clip((-zz-.15)/.32,0,1);sand=(.72+.30*(sandnoise-.5))*(1-.48*wet)
save('shore_color.png',sand[...,None]*np.array([.36,.29,.23]));save('shore_roughness.png',.88-.35*wet+.04*(sandnoise-.5));save('shore_normal.png',normal(sandnoise,1.6))
h=w=512;y,x=np.mgrid[:h,:w];waves=.50*np.sin(y*.17+1.8*np.sin(x*.018))+.22*np.sin(y*.43+x*.04)+.12*np.sin(y*.73-x*.08)+.10*noise(h,w,32,32)
save('water_ripple_normal.png',normal(waves,1.7))
h=w=512;y,x=np.mgrid[:h,:w];fiber=noise(h,w,36,70)*.7+rng.random((h,w))*.3;rad=((x-w*.5)/(w*.46))**2+((y-h*.5)/(h*.40))**2;glow=np.exp(-rad*1.3)
save('paper_color.png',(0.91+fiber[...,None]*.07)*np.array([.91,.50,.16]));save('paper_emission.png',(0.22+.78*glow)[...,None]*np.array([1.,.45,.08]));save('paper_normal.png',normal(fiber,.24))
# Portable Radiance RGBE files, literal scanline RLE. These are authored sky hypotheses.
def write_hdr(path,rgb):
 h,w,_=rgb.shape;mx=np.max(rgb,axis=-1);mant,exp=np.frexp(mx);scale=mant*256/np.maximum(mx,1e-32);rgbe=np.zeros((h,w,4),dtype=np.uint8);rgbe[:,:,:3]=np.clip(rgb*scale[...,None],0,255).astype('uint8');rgbe[:,:,3]=np.where(mx>1e-32,exp+128,0).astype('uint8')
 with open(path,'wb') as f:
  f.write(f'#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y {h} +X {w}\n'.encode())
  for row in rgbe:
   f.write(bytes([2,2,w>>8,w&255]))
   for c in range(4):
    for start in range(0,w,127):part=row[start:start+127,c];f.write(bytes([len(part)]));f.write(part.tobytes())
h,w=512,1024;y,x=np.mgrid[:h,:w];az=x/w*2*np.pi;alt=np.cos(y/(h-1)*np.pi);cloud=.58*noise(h,w,14,28)+.28*noise(h,w,28,56)+.14*noise(h,w,64,128);mask=np.clip((cloud-.43)*4.7,0,1);mask*=np.clip((alt+.035)/.15,0,1);mask*=np.clip((1.08-alt)/.30,0,1);azdist=np.arctan2(np.sin(az-.15),np.cos(az-.15));sunsector=np.exp(-(azdist/.65)**2);hz=np.exp(-np.abs(alt)/.19);sun=np.exp(-(azdist/.018)**2-((alt-.035)/.012)**2)*22
for state in ['S40_sunset','S105_bluehour']:
 if state=='S40_sunset':zen=np.array([.055,.095,.19]);horizon=np.array([.90,.49,.34]);shadow=np.array([.12,.065,.11]);rim=np.array([.65,.18,.11]);level=1.
 else:zen=np.array([.008,.025,.075]);horizon=np.array([.34,.21,.19]);shadow=np.array([.035,.035,.07]);rim=np.array([.22,.085,.085]);level=.16
 sky=zen[None,None,:]*(1-hz[...,None])+horizon[None,None,:]*hz[...,None]*(.48+.52*sunsector[...,None]);lit=np.exp(-((mask-.28)/.18)**2)*sunsector*hz
 sky=sky*(1-mask[...,None]*.88)+shadow[None,None,:]*mask[...,None]+rim[None,None,:]*lit[...,None];sky+=sun[...,None]*np.array([1.,.48,.23])*level*(1-mask[...,None]);sky=np.maximum(sky,.002)
 write_hdr(OUT/(state+'.hdr'),sky);save(state+'_preview.jpg',np.power(sky/(1+sky),1/2.2))
manifest={'origin':'deterministic authored textures; not extracted source pixels; not AI-generated source replacements','seed':2026102909,'units':'model units; all texture scale, grain, cloud pattern and surface roughness inferred','sky_states':{'S40_sunset':'pink warm state suggested by 00:40:37 / N2453','S105_bluehour':'cooler blue state suggested by N6318 / N6766; no exact transition timing inferred'},'files':[]}
for p in sorted(OUT.iterdir()):
 if p.name=='texture-manifest.json':continue
 b=p.read_bytes();manifest['files'].append({'name':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(OUT/'texture-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('TEXTURES_READY',len(manifest['files']))
