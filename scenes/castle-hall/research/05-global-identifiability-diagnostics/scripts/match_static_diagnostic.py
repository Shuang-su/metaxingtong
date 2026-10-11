from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,maximum_filter,uniform_filter
from scipy.signal import correlate
R=Path(__file__).resolve().parents[1]
def run(an,bn,regions,outname):
 ai=Image.open(R/'inputs'/an).convert('RGB');bi=Image.open(R/'inputs'/bn).convert('RGB');a=np.asarray(ai.convert('L'),float)/255;b=np.asarray(bi.convert('L'),float)/255
 ix=gaussian_filter(a,1,order=(0,1));iy=gaussian_filter(a,1,order=(1,0));xx=gaussian_filter(ix*ix,2);yy=gaussian_filter(iy*iy,2);xy=gaussian_filter(ix*iy,2);h=xx*yy-xy*xy-.05*(xx+yy)**2;matches=[]
 for name,box,target,prior_scale,maxn in regions:
  x0,y0,x1,y1=box;tx0,ty0,tx1,ty1=target;mask=np.zeros(a.shape,bool);mask[y0:y1,x0:x1]=True;ys,xs=np.where((h==maximum_filter(h,11))&mask&(h>1e-9));order=np.argsort(h[ys,xs])[::-1][:maxn]
  for ii in order:
   x,y=int(xs[ii]),int(ys[ii]);k=9
   if min(x,y)<k or x+k>=1180 or y+k>=664:continue
   patch=ai.convert('L').crop((x-k,y-k,x+k+1,y+k+1));best=None
   # Bounded target ROI grounded by visual identity, not a free whole-image search.
   # Approximate relative ROI position defines a broad local window; descriptors are resampled, full references never warped.
   ex=tx0+(x-x0)/(x1-x0)*(tx1-tx0);ey=ty0+(y-y0)/(y1-y0)*(ty1-ty0)
   for scale in prior_scale*np.array([.9,.95,1.,1.05,1.1]):
    sz=int(round((2*k+1)*scale));sz+=1-sz%2;kk=sz//2;p=np.array(patch.resize((sz,sz),Image.Resampling.BICUBIC),float)/255;p-=p.mean();pn=np.linalg.norm(p)
    if pn<.18:continue
    bx0=max(0,int(ex-28)-kk);by0=max(0,int(ey-28)-kk);bx1=min(1180,int(ex+29)+kk);by1=min(664,int(ey+29)+kk);crop=b[by0:by1,bx0:bx1]
    if min(crop.shape)<sz:continue
    num=correlate(crop,p,mode='valid',method='fft');sm=correlate(crop,np.ones(p.shape),mode='valid',method='fft');sq=correlate(crop*crop,np.ones(p.shape),mode='valid',method='fft');score=num/(np.sqrt(np.maximum(sq-sm*sm/p.size,1e-9))*pn)
    jy,jx=np.unravel_index(np.argmax(score),score.shape);val=float(score[jy,jx]);copy=score.copy();copy[max(0,jy-3):jy+4,max(0,jx-3):jx+4]=-1;second=float(copy.max());rec={'group':name,'source_xy':[x,y],'target_xy':[int(bx0+jx+kk),int(by0+jy+kk)],'score':val,'distinctness':val-second,'descriptor_scale':float(scale)}
    if best is None or val>best['score']:best=rec
   if best and best['score']>.82 and best['distinctness']>.025:matches.append(best)
 # Remove duplicate target neighborhoods, keeping higher-scoring match.
 keep=[]
 for m in sorted(matches,key=lambda z:z['score'],reverse=True):
  if all(np.linalg.norm(np.array(m['target_xy'])-n['target_xy'])>=4 for n in keep):keep.append(m)
 keep.sort(key=lambda z:(z['group'],z['source_xy'][1]));out={'source':an,'target':bn,'method':'Harris points and scale-adaptive patch NCC inside manually identity-checked region pairs. Descriptor patches may be resized; source/reference images are not warped. Tentative correspondences require visual review; rigid body assumptions are not guaranteed.','matches':keep};(R/'qa'/(outname+'.json')).write_text(json.dumps(out,indent=2))
 can=Image.new('RGB',(2360,664));can.paste(ai);can.paste(bi,(1180,0));d=ImageDraw.Draw(can);colors={'near_wall':'cyan','side_window':'lime','back_lamp':'yellow','rear_column_base':'orange','table_cake':'magenta','floor_left':'red','floor_right':'red'}
 for i,m in enumerate(keep):
  x,y=m['source_xy'];u,v=m['target_xy'];co=colors.get(m['group'],'white');d.ellipse((x-3,y-3,x+3,y+3),outline=co,width=2);d.text((x+4,y-7),str(i),fill=co);d.ellipse((u+1177,v-3,u+1183,v+3),outline=co,width=2);d.text((u+1184,v-7),str(i),fill=co)
 can.save(R/'qa'/(outname+'.jpg'),quality=95,subsampling=0);print(outname,len(keep),{g:sum(x['group']==g for x in keep) for g in set(x['group'] for x in keep)})
run('hall_right_arch_4528_paused_core.png','hall_right_arch_4529_natural_ui_clear_core.png',[
 ('near_wall',(748,10,857,285),(902,8,1018,281),1.0,45),
 ('side_window',(313,18,383,251),(483,15,553,248),1.0,35),
 ('back_lamp',(30,47,75,128),(216,65,260,139),1.,25),
 ('rear_column_base',(101,291,181,331),(273,299,352,341),1.,25),
 ('table_cake',(238,240,285,297),(375,239,421,295),1.,25),
 ('floor_left',(42,390,382,580),(133,382,430,563),.9,40),
 ('floor_right',(708,401,1034,584),(748,409,1080,604),1.,40),
], 'pair_4528_4529_tentative')
run('hall_A_2712_paused_core.png','hall_B_4509_paused_core.png',[
 ('back_lamp',(365,10,424,60),(449,176,482,211),.62,20),
 ('back_lamp_right',(768,5,820,61),(701,176,733,216),.62,20),
 ('rear_column_base_left',(282,296,340,334),(398,352,435,379),.65,25),
 ('near_column_base_left',(177,302,274,348),(312,366,390,398),.7,25),
 ('table_cake',(78,196,138,288),(254,289,302,354),.65,30),
 ('table_cake_rear_left',(345,222,423,285),(431,312,480,352),.63,25),
 ('floor_left',(41,407,394,613),(227,440,450,594),.65,60),
 ('floor_right',(759,432,1005,603),(701,451,878,590),.68,55),
], 'pair_2713_4509_tentative')
