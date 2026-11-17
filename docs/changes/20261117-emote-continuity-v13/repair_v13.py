#!/usr/bin/env python3
"""Non-generative, reversible local motion/background experiments. No API."""
from pathlib import Path
import importlib.util,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,distance_transform_edt,binary_dilation
DOC=Path(__file__).resolve().parent;ROOT=DOC.parents[2]
s=importlib.util.spec_from_file_location('v12',ROOT/'docs/changes/20261116-motion-prop-v12/repair_v12.py');v12=importlib.util.module_from_spec(s);s.loader.exec_module(v12)
SRC03=v12.SRC03
SRC02=ROOT/'emotes/sunburst/agent-emotes/02-butterfly/versions/20261115-user-color-reference/v11-color-r5/02-v11-CANDIDATE-master-768.gif'
SRC11=ROOT/'emotes/sunburst/agent-emotes/11-count/versions/20261116-motion-v12/v12-prop-r6/11-v12-CANDIDATE-master-768.gif'
def head_trial(im,amount,frame=4):
 a=np.array(im);yy,xx=np.indices(a.shape[:2]);edge=np.interp(yy,[0,120,160,240,270,315,345,420,460,550,768],[360,425,395,375,352,355,380,402,380,390,390])
 # All Nailv pixels to the right of this conservative boundary are fixed.
 color_mask=np.array(Image.open(SRC03.parent/f'allowed-mask-{frame:02}.png'))>0
 protect=(xx>=edge)|(yy>=560)|binary_dilation(color_mask,iterations=8)
 weight=np.clip(distance_transform_edt(~protect)/45,0,1)
 # Local forward displacement peaks at face/jaw, returns to zero at cuffs.
 ys=np.array([0,95,140,220,360,465,510,560,767]);vs=np.array([0,0,.30,.65,1,1,.40,0,0])*amount
 sy=yy.astype(float)
 for _ in range(35):sy=yy-np.interp(sy,ys,vs)*weight
 changed_map=np.abs(sy-yy)>1e-5;allowed=changed_map&~protect
 paint=np.stack([map_coordinates(a[:,:,k].astype(float),[sy,xx],order=1,mode='nearest') for k in range(3)],axis=2).round().astype('uint8');paint[~allowed]=a[~allowed]
 q=v12.quantize(im,Image.fromarray(paint),allowed)
 return q,allowed,protect,{'maximum_displacement_px':amount,'source_y_knots':ys.tolist(),'forward_displacement_y_knots':vs.tolist(),'foreground_boundary_y':[0,120,160,240,270,315,345,420,460,550,768],'foreground_boundary_x':[360,425,395,375,352,355,380,402,380,390,390],'v11_color_mask_protection_dilation_px':8,'frame':frame,'method':'same-frame local vertical mesh; no global translation or inserted frame; experimental'}
def desk_trial(original,v12im,ref):
 a=np.array(original);current=np.array(v12im);geom,_=v12.wood_geometry(original);target,_=v12.wood_geometry(ref);mask=v12.prop_mask(original,geom);protect=v12.hair_protection(original)
 sx=target['base_width']/geom['base_width'];sy=(target['bottom_y']-target['top_y'])/(geom['bottom_y']-geom['top_y']);tx=target['base_center']-sx*geom['base_center'];ty=target['bottom_y']-sy*geom['bottom_y']
 yy,xx=np.indices(a.shape[:2]);weight=np.clip(distance_transform_edt(~protect)/20,0,1);srcx=xx+weight*((xx-tx)/sx-xx);srcy=yy+weight*((yy-ty)/sy-yy)
 cov=map_coordinates(mask.astype(float),[srcy,srcx],order=1,mode='constant',cval=0)
 # Only revealed desk/air pixels; original stabilized prop and actor remain exact.
 allowed=mask&(cov<.01)&(yy>=688)&~protect
 bg=a.copy().astype(float)
 for y in range(688,768):
  left=np.median(a[y,500:515],axis=0);right=np.median(a[y,738:753],axis=0)
  t=np.clip((np.arange(768)-507)/238,0,1)
  bg[y]=left[None,:]*(1-t[:,None])+right[None,:]*t[:,None]
 paint=current.copy();paint[allowed]=np.rint(bg[allowed]).clip(0,255).astype('uint8')
 q=v12.quantize(v12im,Image.fromarray(paint),allowed)
 return q,allowed,{'source':'same frame clear desk rows beside prop','left_columns':[500,515],'right_columns':[738,753],'coverage_max':.01,'minimum_y':688,'prop_pixels_changed':0}
def main():
 out=DOC/'prototypes-r1';out.mkdir(exist_ok=False);fs,_=v12.load(SRC03)
 canvas=Image.new('RGB',(4*400,590),'#eee');d=ImageDraw.Draw(canvas)
 for j,amount in enumerate([0,16,24,32]):
  q,m,p,rec=head_trial(fs[3],amount);q.convert('RGB').save(out/f'03-F04-head-{amount:02}.png');Image.fromarray(m.astype('uint8')*255).save(out/f'03-F04-allowed-{amount:02}.png');Image.fromarray(p.astype('uint8')*255).save(out/f'03-F04-protected-{amount:02}.png');(out/f'03-F04-head-{amount:02}.json').write_text(json.dumps(rec,indent=2)+'\n');canvas.paste(q.convert('RGB').crop((0,100,400,670)),(j*400,20));d.text((j*400+3,3),f'F04 head displacement {amount}',fill='black')
 canvas.save(out/'03-native-head-trials.png')
 src,_=v12.load(v12.SRC11);old,_=v12.load(SRC11);canvas=Image.new('RGB',(4*520,105),'#eee');d=ImageDraw.Draw(canvas)
 for j,n in enumerate([28,32,33,50]):
  q,m,rec=desk_trial(src[n-1],old[n-1],src[0]);q.convert('RGB').save(out/f'11-F{n:02}-desk.png');Image.fromarray(m.astype('uint8')*255).save(out/f'11-F{n:02}-allowed.png');(out/f'11-F{n:02}-desk.json').write_text(json.dumps(rec,indent=2)+'\n')
  for k,im in enumerate([old[n-1],q.convert('RGB')]):canvas.paste(im.crop((500,680,760,765)),(j*520+k*260,20));d.text((j*520+k*260+3,3),f'F{n:02} '+('v12' if k==0 else 'desk trial'),fill='black')
 canvas.save(out/'11-native-desk-trials.png')
if __name__=='__main__':main()
