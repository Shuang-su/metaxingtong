from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,maximum_filter
from scipy.signal import correlate
R=Path(__file__).resolve().parents[1];D=R/'inputs/motion_right_to_front_verified';M=json.loads((D/'metadata.json').read_text()); ims=[Image.open(D/f'{i:03}.jpg').crop((0,27,1180,691)).convert('RGB') for i in range(155)]; gs=[np.array(im.convert('L'),dtype=float)/255 for im in ims];seed=42
# Core coordinate boxes visually grounded in frame042; never include performer, balloon, props or floor.
regions={'rear_lamp_high':(20,65,73,122),'rear_column_foot':(88,281,151,341),'side_window_high':(310,15,365,207),'side_window_low':(318,243,365,287),'near_column_foot':(421,327,548,380),'arch_wall_ornament_high':(766,15,817,104),'arch_wall_ornament_low':(765,175,822,310),'arch_spring_junction':(815,101,960,146),'arch_jamb_foot':(813,343,870,396)}
a=gs[seed];ix=gaussian_filter(a,1,order=(0,1));iy=gaussian_filter(a,1,order=(1,0));xx=gaussian_filter(ix*ix,2);yy=gaussian_filter(iy*iy,2);xy=gaussian_filter(ix*iy,2);h=xx*yy-xy*xy-.05*(xx+yy)**2;pts=[]
for group,(x0,y0,x1,y1) in regions.items():
 mask=np.zeros(a.shape,bool);mask[y0:y1,x0:x1]=1;ys,xs=np.where((h==maximum_filter(h,15))&mask&(h>2e-9));order=np.argsort(h[ys,xs])[::-1][:8]
 for j in order: pts.append({'group':group,'seed_xy':[int(xs[j]),int(ys[j])]})
# Independently reviewed unique lower landmarks, full screenshot coordinates converted by y-27.
pts.extend([{'group':'nearest_column_square_plinth','seed_xy':[994,465]},{'group':'lowest_stair_front_corner','seed_xy':[934,366]},{'group':'side_window_fixed_low_corner','seed_xy':[331,257]}])
def match(a,b,p,pred=None,k=12,rad=23):
 x,y=np.rint(p).astype(int);ex,ey=np.rint(p if pred is None else pred).astype(int)
 if x<k or y<k or x+k>=1180 or y+k>=664:return None
 patch=a[y-k:y+k+1,x-k:x+k+1];patch=patch-patch.mean();pn=np.linalg.norm(patch)
 if pn<.07:return None
 x0=max(k,ex-rad);x1=min(1180-k-1,ex+rad);y0=max(k,ey-rad);y1=min(664-k-1,ey+rad)
 if x1<x0 or y1<y0:return None
 crop=b[y0-k:y1+k+1,x0-k:x1+k+1];n=patch.size;num=correlate(crop,patch,mode='valid',method='fft');one=np.ones(patch.shape);sm=correlate(crop,one,mode='valid',method='fft');sq=correlate(crop*crop,one,mode='valid',method='fft');sc=num/(pn*np.sqrt(np.maximum(sq-sm*sm/n,1e-10)));jy,jx=np.unravel_index(sc.argmax(),sc.shape);score=float(sc[jy,jx]);co=sc.copy();co[max(0,jy-3):jy+4,max(0,jx-3):jx+4]=-1;distinct=score-float(co.max());dx=dy=0
 if 0<jx<sc.shape[1]-1:
  den=sc[jy,jx-1]-2*sc[jy,jx]+sc[jy,jx+1];dx=float(.5*(sc[jy,jx-1]-sc[jy,jx+1])/den) if abs(den)>1e-8 else 0
 if 0<jy<sc.shape[0]-1:
  den=sc[jy-1,jx]-2*sc[jy,jx]+sc[jy+1,jx];dy=float(.5*(sc[jy-1,jx]-sc[jy+1,jx])/den) if abs(den)>1e-8 else 0
 return np.array([x0+jx+dx,y0+jy+dy]) + (np.array(p)-[x,y]),score,distinct
for j,p in enumerate(pts):
 xy=np.full((155,2),np.nan);scores=np.zeros(155);fb=np.full(155,np.nan);xy[seed]=p['seed_xy'];scores[seed]=1;fb[seed]=0;stop={}
 for direction in [-1,1]:
  for i in range(seed+direction,155 if direction==1 else -1,direction):
   prev=i-direction;q=match(gs[prev],gs[i],xy[prev]);
   if q is None or q[1]<.82:stop[str(direction)]={'index':i,'reason':'low_score_or_out_of_bounds','score':None if q is None else q[1]};break
   rev=match(gs[i],gs[prev],q[0],pred=xy[prev],rad=5)
   ef=999 if rev is None else np.linalg.norm(rev[0]-xy[prev])
   if ef>2.0:stop[str(direction)]={'index':i,'reason':'forward_backward','error':float(ef)};break
   xy[i]=q[0];scores[i]=q[1];fb[i]=ef
 p.update(id=j,xy=[None if not np.isfinite(q).all() else q.tolist() for q in xy],scores=scores.tolist(),forward_backward_px=[None if not np.isfinite(q) else float(q) for q in fb],stops=stop);print(j,p['group'],'valid',sum(np.isfinite(xy[:,0])),flush=True)
out={'status':'TENTATIVE_CONTINUOUS_TRACKS_REQUIRE_VISUAL_ENDPOINT_REVIEW','source':'BV1aw411T7ws','seed_frame':seed,'coordinate_domain':'fixed core1180x664 crop[0,27,1180,691]','regions':regions,'method':'Consecutive-frame 25x25 NCC radius23px; score>=.82; reverse search radius5 and FB<=2px; subpixel parabolic peak. No full-image warp; no floor, props or performer seeds. No track resurrection after failure.','tracks':pts,'timestamps':[[q['before']['time'],q['after']['time']] for q in M['frames']]};(R/'qa/continuous_architecture_tracks.json').write_text(json.dumps(out,indent=2))
colors=['#ff5555','#ffb020','#eeee33','#33ff88','#22eeff','#5599ff','#bb66ff','#ff66cc','#ffffff']
for frame in [0,14,28,42,56,70,84,98,112,126,140,154]:
 im=ims[frame].copy();d=ImageDraw.Draw(im)
 for p in pts:
  q=p['xy'][frame]
  if q is None:continue
  x,y=q;col=colors[list(regions).index(p['group'])] if p['group'] in regions else '#ffffff';d.ellipse((x-4,y-4,x+4,y+4),outline=col,width=2);d.text((x+5,y-9),str(p['id']),fill=col)
 d.rectangle((0,635,650,663),fill='#111111');d.text((10,643),f'FRAME {frame:03} | t={M["frames"][frame]["before"]["time"]:.6f} | tentative tracks',fill='white');im.save(R/'qa'/f'tracks_{frame:03}.jpg',quality=95,subsampling=0)
