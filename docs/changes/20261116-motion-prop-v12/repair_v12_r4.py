#!/usr/bin/env python3
"""Original-pixel mouth phase trial and local metronome registration. No API."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageSequence,ImageDraw
from scipy.ndimage import label,binary_fill_holes,binary_dilation,distance_transform_edt,map_coordinates

DOC=Path(__file__).resolve().parent;ROOT=DOC.parents[2]
SRC03=ROOT/'emotes/sunburst/agent-emotes/03-awake/versions/20261115-user-color-reference/v11-color-r5/03-v11-CANDIDATE-master-768.gif'
SRC11=ROOT/'emotes/sunburst/agent-emotes/11-count/versions/20261115-desk-continuity/v10-desk-r1/11-v10-CANDIDATE-master-768.gif'

def load(p):
 im=Image.open(p);fs=[];ts=[]
 for f in ImageSequence.Iterator(im):fs.append(f.convert('RGB'));ts.append(f.info['duration'])
 return fs,ts
def quantize(before,after,mask):
 p=before.quantize(colors=256,method=Image.Quantize.MAXCOVERAGE,dither=Image.Dither.NONE)
 assert p.convert('RGB').tobytes()==before.tobytes()
 q=after.quantize(palette=p,dither=Image.Dither.NONE);p.paste(q,(0,0),Image.fromarray(mask.astype('uint8')*255))
 assert np.array_equal(np.array(p.convert('RGB'))[~mask],np.array(before)[~mask])
 return p

def mouth_trial(im):
 donor=Image.open(DOC/'03-strip0-cell04.png').convert('RGB');a=np.array(im);b=np.array(donor)
 # The original cell's closed mouth is a real earlier expression, not a
 # synthesized in-between. Both source shoulder fingers are outside this mask.
 polygon=[(171,469),(195,461),(234,460),(248,469),(250,482),(230,490),(198,496),(178,496),(171,487)]
 mm=Image.new('L',im.size);ImageDraw.Draw(mm).polygon(polygon,fill=255);mask=np.array(mm)>0
 alpha=np.clip(distance_transform_edt(mask)/2,0,1)
 paint=np.rint(a*(1-alpha[:,:,None])+b*alpha[:,:,None]).astype('uint8')
 q=quantize(im,Image.fromarray(paint),mask)
 return q,mask,{'source':'strip-0 cell4','frame':5,'polygon':polygon,'inward_feather_px':2,'status':'mouth-only partial candidate, does not resolve body pose jump'}

def wood_geometry(im):
 a=np.array(im).astype(int);r,g,b=a.transpose(2,0,1);yy,xx=np.indices(r.shape)
 m=(xx>505)&(xx<755)&(yy>410)&(yy<716)&(r>110)&(r<187)&(r-g>20)&(g-b>9)
 cc,_=label(m);counts=np.bincount(cc.ravel());counts[0]=0;k=int(counts.argmax());wood=cc==k
 ys,xs=np.where(wood);bottom=int(ys.max())
 # Casing and base are separated by dark ink, so the top is measured across
 # all warm wood pixels, not from the base component's upper horizontal edge.
 top=int(np.flatnonzero(m.sum(axis=1)>=5)[0])
 # Base width from the lower wood body, away from the thin outlined corners.
 lines=[]
 for y in range(bottom-15,bottom-4):
  x=np.flatnonzero(wood[y]);
  if len(x)>100:lines.append((int(x.min()),int(x.max())))
 assert len(lines)>3,{'top':top,'bottom':bottom,'component_pixels':len(xs)}
 left,right=np.median(lines,axis=0)
 return {'top_y':top,'bottom_y':bottom,'base_left':float(left),'base_right':float(right),'base_center':float((left+right)/2),'base_width':float(right-left),'wood_pixels':int(wood.sum())},wood

def hair_protection(im):
 a=np.array(im).astype(int);r,g,b=a.transpose(2,0,1);yy,xx=np.indices(r.shape)
 m=(xx<560)&(yy<610)&(r>100)&(b-r>3)&(b-g>3)
 cc,_=label(m);counts=np.bincount(cc.ravel());counts[0]=0
 core=cc==int(counts.argmax())
 # Keep the complete foreground and a 12 px edge buffer around the gray fringe.
 # The pointer can pass behind this foreground; it must never drag hair.
 return binary_dilation(binary_fill_holes(core),iterations=12)|(xx<505)

def prop_mask(im,geom):
 a=np.array(im);yy,xx=np.indices(a.shape[:2]);nonwhite=np.min(a,axis=2)<242
 roi=(xx>=505)&(xx<755)&(yy>=410)&(yy<733)
 # Above the desk, object connectivity separates the pendulum/body from hair.
 protected=hair_protection(im)
 upper=nonwhite&roi&(yy<690)&~protected;cc,_=label(upper);seed=int(cc[675,620]);assert seed
 m=(cc==seed)
 lo=int(geom['base_left'])-6;hi=int(geom['base_right'])+7
 lower=roi&(yy>=690)&(xx>=lo)&(xx<=hi)&(np.max(a,axis=2)<195)
 m|=lower;m=binary_fill_holes(m);m=binary_dilation(m,iterations=2)&roi&~protected
 return m

def prop_repair(im,reference):
 geom,wood=wood_geometry(im);target,_=wood_geometry(reference);a=np.array(im);mask=prop_mask(im,geom)
 sx=target['base_width']/geom['base_width'];sy=(target['bottom_y']-target['top_y'])/(geom['bottom_y']-geom['top_y'])
 tx=target['base_center']-sx*geom['base_center'];ty=target['bottom_y']-sy*geom['bottom_y']
 yy,xx=np.indices(a.shape[:2]);srcx=(xx-tx)/sx;srcy=(yy-ty)/sy
 coverage=map_coordinates(mask.astype(float),[srcy,srcx],order=1,mode='constant',cval=0)
 warped=np.stack([map_coordinates(a[:,:,k].astype(float),[srcy,srcx],order=1,mode='constant',cval=252) for k in range(3)],axis=2)
 bg=np.empty_like(a);bg[:]=np.median(a[10:40,600:730].reshape(-1,3),axis=0)
 # Same-frame clear desk rows restore only pixels vacated by the prop.
 for y in range(688,768):bg[y]=np.median(a[y,30:100],axis=0)
 union=(mask|(coverage>0))&~hair_protection(im)
 painted=np.rint(bg*(1-coverage[:,:,None])+warped*coverage[:,:,None]).clip(0,255).astype('uint8');painted[~union]=a[~union]
 q=quantize(im,Image.fromarray(painted),union)
 return q,union,mask,{'source_geometry':geom,'target_geometry':target,'scale_x':sx,'scale_y':sy,'translate_x':tx,'translate_y':ty,'method':'local prop affine registration from its original wood casing; original pendulum retained'}

def prototype():
 out=DOC/'prototype-r3';out.mkdir(exist_ok=False)
 fs,_=load(SRC03);q,m,rec=mouth_trial(fs[4]);q.convert('RGB').save(out/'03-F05-mouth-candidate.png');Image.fromarray(m.astype('uint8')*255).save(out/'03-F05-mouth-mask.png');(out/'03-F05-mouth.json').write_text(json.dumps(rec,indent=2)+'\n')
 fs,_=load(SRC11);rows=[]
 for n in [1,28,50,54]:
  q,m,prop,rec=prop_repair(fs[n-1],fs[0]);q.convert('RGB').save(out/f'11-F{n:02}-candidate.png');Image.fromarray(m.astype('uint8')*255).save(out/f'11-F{n:02}-allowed.png');Image.fromarray(prop.astype('uint8')*255).save(out/f'11-F{n:02}-source-prop-mask.png');rows.append({'frame':n,**rec})
 (out/'11-parameters.json').write_text(json.dumps(rows,indent=2)+'\n')
 canvas=Image.new('RGB',(4*260,2*370),'#eee');d=ImageDraw.Draw(canvas)
 for j,n in enumerate([1,28,50,54]):
  for k,im in enumerate([fs[n-1],Image.open(out/f'11-F{n:02}-candidate.png')]):
   canvas.paste(im.crop((500,405,760,753)),(j*260,k*370+22));d.text((j*260+3,k*370+3),f'F{n:02} '+('before' if k==0 else out.name),fill='black')
 canvas.save(out/'11-native-comparison.png');print(json.dumps(rows,indent=2))

if __name__=='__main__':prototype()
