#!/usr/bin/env python3
"""Local color candidates from two user-selected references; no generation API."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageSequence,ImageDraw
from scipy.ndimage import label,find_objects,distance_transform_edt,binary_closing
from scipy.spatial import cKDTree
DOC=Path(__file__).resolve().parent;ROOT=DOC.parents[2]
sys.path.insert(0,str(DOC.parent/'20261113-nailv-color-review'))
from build_color_candidates import lab,rgb,palette_preserve

SOURCES={
 '02-butterfly':'versions/20261115-boundary-refinement/v8-local-r1/02-v8-CANDIDATE-master-768.gif',
 '03-awake':'versions/20261115-transition-v9/v9-shared-collar-r3/03-v9-CANDIDATE-master-768.gif'}
POOLS={}

def set_common_pool(name,frames):
 sets=[set(c for _,c in im.getcolors(maxcolors=256)) for im in frames]
 colors=np.array(sorted(set.intersection(*sets)),dtype='uint8');ci=colors.astype(int)
 pool=colors[(ci[:,0]-ci[:,1]>=2)&(ci[:,0]-ci[:,1]<=32)&(ci[:,1]-ci[:,2]>=-2)&(ci[:,1]-ci[:,2]<=27)&(ci[:,0]>=85)&(ci[:,0]<=220)]
 assert len(pool)>=12,(name,len(pool))
 POOLS[name]=pool
 return pool

def load(name):
 im=Image.open(ROOT/'emotes/sunburst/agent-emotes'/name/SOURCES[name]);fs=[];times=[]
 for f in ImageSequence.Iterator(im):fs.append(f.convert('RGB'));times.append(f.info['duration'])
 return fs,times

def reference_samples():
 specs={
 'PNG':('OpenAI Playground 2026-11-05 at 12.43.45.png',{'hair_crown':[360,175,420,220],'hair_side':[794,524,818,551],'hair_shadow':[914,661,936,690],'bang':[516,421,534,469],'left_upper_iris':[318,700,340,717],'left_lower_iris':[336,736,361,745],'right_upper_iris':[575,612,601,626],'right_lower_iris':[644,643,669,653]}),
 'single_frame_named_GIF':('naigreen-not-angry.gif',{'hair_crown':[167,76,187,95],'hair_side':[89,305,105,324],'bang':[225,132,232,155],'left_lower_iris':[150,216,173,221],'right_lower_iris':[244,214,264,220]})}
 out={}
 for key,(filename,boxes) in specs.items():
  im=Image.open(DOC/'references'/filename).convert('RGB');a=np.array(im);out[key]={'filename':filename,'samples':{}}
  for region,(x0,y0,x1,y1) in boxes.items():
   v=np.median(a[y0:y1,x0:x1].reshape(-1,3),axis=0);out[key]['samples'][region]={'box':[x0,y0,x1,y1],'median_rgb':v.tolist(),'lab':lab(v).tolist()}
 return out

def masks(name,im,n):
 a=np.array(im).astype(int);r,g,b=a.transpose(2,0,1);yy,xx=np.indices(r.shape)
 # Warm taupe hair interiors only. Skin is redder/brighter; dark ink and
 # pale clothing/flowers remain outside these thresholds and spatial gates.
 eligible=(r-g>=5)&(r-g<=42)&(g-b>=-5)&(g-b<=30)&(r>=95)&(r<=210)&(g>=65)&(b>=60)&(yy<575)
 eligible&=~((r>170)&(r-g>33)&(r-b>43))
 cc,num=label(eligible);sizes=np.bincount(cc.ravel());objects=find_objects(cc)
 choices=[]
 for k,sl in enumerate(objects,1):
  if sl and sizes[k]>1000 and sl[0].start<300:choices.append((sizes[k],k))
 assert choices,(name,n,'no hair anchor')
 main=max(choices)[1];ys,xs=np.where(cc==main);cx=float(xs.mean());head_left=int(xs.min());head_right=int(xs.max());hair=np.zeros(r.shape,bool)
 selected=[]
 for k,sl in enumerate(objects,1):
  if not sl or sizes[k]<60:continue
  ys,xs=np.where(cc[sl]==k);xs=xs+sl[1].start;ys=ys+sl[0].start
  top=ys.min();mx=xs.mean()
  height=int(ys.max()-ys.min()+1)
  take=(top<440 and sizes[k]>=800) or (top<145 and sizes[k]>=300) or (250<top<440 and height>35 and sizes[k]>150)
  take|=(150<top<300 and head_left+45<mx<head_right-45 and sizes[k]>=150)
  take|=(top<490 and abs(mx-cx)>90 and sizes[k]>650)
  take=take and head_left-55<=mx<=head_right+55
  if take:hair[sl]|=cc[sl]==k;selected.append({'area':int(sizes[k]),'box':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]})
 base=ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261113-local-patch-review/v7-green-local-r2'
 green=np.array(Image.open(base/f'color-mask-{n:02}.png'))>0
 rows=json.loads((base/'construction.json').read_text())['frames'];rec=rows[n-1]
 if name.startswith('03'):
  pl=rec['placement'];dy=pl['bang']['dy'];eye_top=(313 if n<=4 or n>=40 else 333)+dy
  split=550+pl['bang']['dx']
 else:
  labcc,count=label(green);cand=[]
  for k,sl in enumerate(find_objects(labcc),1):
   if not sl:continue
   h=sl[0].stop-sl[0].start;w=sl[1].stop-sl[1].start
   if h>35 and h>1.4*w:cand.append((int((labcc[sl]==k).sum()),sl))
  if cand:
   sl=max(cand,key=lambda x:x[0])[1];eye_top=max(260,sl[0].stop-8)
  else:eye_top=300
  split=rec['placement']['head_center_x']
 bang=green&(yy<eye_top);eyes=green&~bang
 # Preserve neck bows, garment trim, hands and skin irrespective of color.
 if name.startswith('03'):
  hair&=~((yy>=420)&(xx>470)&(xx<640))
  # Left sleeve moves across the dark braid. Retain that occluded deep braid
  # unchanged rather than recoloring garment shadows with the same RGB.
  hair&=~((yy>=440)&(xx<655))
 else:
  hair&=~((yy>=410)&(xx>cx-65)&(xx<cx+75))
  if n==17:
   # Only these original Nailv hair islands remain visible behind Xingtong.
   visible=((xx>=340)&(xx<490)&(yy>=70)&(yy<175))|((xx>=530)&(xx<570)&(yy>=270)&(yy<360))|((xx>=490)&(xx<555)&(yy>=405)&(yy<480))
   hair=eligible&visible
 hair&=~green
 # Keep already-reviewed correct hands and repairs protected as well.
 handbase=ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261113-local-patch-review/v6-contour-and-motion'
 handdir=handbase/('dynamic-candidate' if name.startswith('02') else 'dynamic-candidate-r1')
 protected_path=handdir/f'protected-{n:02}.png'
 if protected_path.exists():hair&=~(np.array(Image.open(protected_path))>0)
 return {'hair':hair,'bang':bang,'left_iris':eyes&(xx<split),'right_iris':eyes&(xx>=split)}, {'hair_anchor_center_x':cx,'hair_components':selected,'eye_top':int(eye_top),'eye_split_x':float(split)}

def transform(name,im,n,samples):
 ms,details=masks(name,im,n);a=np.array(im);l=lab(a);out=l.copy();p=samples['PNG']['samples'];g=samples['single_frame_named_GIF']['samples']
 targets={}
 # PNG carries most authority; GIF-name sample contributes separate eye
 # hues. No copying of its red neckband, text, or floating decorations.
 hair_samples=[p[k]['lab'] for k in ['hair_crown','hair_side','hair_shadow']]
 hair_ab=np.median(np.array(hair_samples),axis=0)[1:]
 targets['hair']=hair_ab
 targets['bang']=.75*np.array(p['bang']['lab'][1:])+.25*np.array(g['bang']['lab'][1:])
 for side in ['left','right']:
  # Include the olive upper iris as well as the pale yellow-green lower rim.
  png_iris=.55*np.array(p[side+'_upper_iris']['lab'][1:])+.45*np.array(p[side+'_lower_iris']['lab'][1:])
  targets[side+'_iris']=.75*png_iris+.25*np.array(g[side+'_lower_iris']['lab'][1:])
 union=np.zeros(a.shape[:2],bool)
 for key,m in ms.items():
  union|=m;alpha=np.clip(distance_transform_edt(m)/2.0,0,1)
  if key=='hair':
   alpha*=np.clip((l[:,:,0]-30)/20,0,1)
   out[:,:,0]+=10.0*alpha
   strength=.65
  else:
   out[:,:,0]+=(4.0 if key=='bang' else 0)*alpha;strength=.80
  out[:,:,1:]=out[:,:,1:]*(1-strength*alpha[:,:,None])+targets[key]*(strength*alpha[:,:,None])
 b=rgb(out);b[~union]=a[~union]
 # Hair shares many palette colors with protected clothing. Reuse existing
 # warm neutral colors for hair, reserving free GIF slots for distinct greens.
 # This prevents the much larger hair area swallowing the iris colors.
 if name in POOLS:neutral=POOLS[name]
 else:
  colors=np.unique(a.reshape(-1,3),axis=0);ci=colors.astype(int)
  neutral=colors[(ci[:,0]-ci[:,1]>=2)&(ci[:,0]-ci[:,1]<=32)&(ci[:,1]-ci[:,2]>=-2)&(ci[:,1]-ci[:,2]<=27)&(ci[:,0]>=85)&(ci[:,0]<=220)]
 tree=cKDTree(lab(neutral));hair=ms['hair'];_,ii=tree.query(lab(b[hair]));hair_base=a.copy();hair_base[hair]=neutral[ii]
 accent=union&~hair
 b[hair]=hair_base[hair]
 q,slots=palette_preserve(Image.fromarray(hair_base),Image.fromarray(b),accent)
 assert np.array_equal(np.array(q.convert('RGB'))[~union],a[~union])
 return q,ms,{'regions':{k:int(m.sum()) for k,m in ms.items()},'palette_slots':slots,'placement':details,'target_ab':{k:v.tolist() for k,v in targets.items()},'hair_L_delta':10.0,'hair_chroma_mix':.65,'accent_chroma_mix':.8}

def prototype():
 samples=reference_samples();(DOC/'reference-sampling.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')
 out=DOC/'prototype-r5-recheck';out.mkdir(exist_ok=False)
 for name,n in [('02-butterfly',27),('03-awake',17)]:
  fs,_=load(name);set_common_pool(name,fs);im=fs[n-1];q,ms,rec=transform(name,im,n,samples)
  q.convert('RGB').save(out/f'{name}-F{n}-candidate.png');a=np.array(im).copy();colors={'hair':[255,0,150],'bang':[0,200,0],'left_iris':[0,150,220],'right_iris':[240,180,0]}
  for key,m in ms.items():
   Image.fromarray(m.astype('uint8')*255).save(out/f'{name}-F{n}-{key}-mask.png');a[m]=np.rint(a[m]*.45+np.array(colors[key])*.55).astype('uint8')
  Image.fromarray(a).save(out/f'{name}-F{n}-mask-overlay.png');(out/f'{name}-F{n}.json').write_text(json.dumps(rec,indent=2)+'\n')
  c=Image.new('RGB',(1536,790),'#eee');d=ImageDraw.Draw(c);d.text((4,3),'current',fill='black');d.text((772,3),'user-reference color r5 recheck',fill='black');c.paste(im,(0,22));c.paste(q.convert('RGB'),(768,22));c.save(out/f'{name}-F{n}-comparison.png')
  print(name,rec['regions'],rec['palette_slots'])

if __name__=='__main__':prototype()
