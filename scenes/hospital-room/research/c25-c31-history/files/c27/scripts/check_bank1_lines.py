from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parents[2];P=R/'c27';j=json.loads((P/'blinds_projection_source.json').read_text());f=json.loads((P/'bank1_fit.json').read_text());names=f['target_group'];par=f['selected_H_G_only'];spec={'H':(650,930,.174,947,204),'G':(80,325,.28,343,254),'N642':(350,600,.18,617,172)};out={}
def projected_polygon(k,idx,trim):
 v=np.array(j['objects'][names[idx]]['world_vertices']);l=v[:,0].min();r=v[:,0].max();v[:,0]=l+(v[:,0]-l)*(r+trim-l)/(r-l)
 q=np.c_[v,np.ones(len(v))]@np.array(j['cameras'][k]['projection']).T;uv=q[:,:2]/q[:,3:4];uv=np.c_[(uv[:,0]+1)*960,(1-uv[:,1])*540];return uv[ConvexHull(uv).vertices]
def bottom_at_x(hull,x):
 ys=[]
 for a,b in zip(hull,np.roll(hull,-1,axis=0)):
  if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(b[0]-a[0])>1e-9:ys.append(a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]))
 return max(ys)
for k,(x0,x1,slope,tx,ty) in spec.items():
 im=Image.open(R/'inputs'/f['sources'][k]['name']).convert('RGB');g=np.array(im,dtype=float).mean(2);xs=np.arange(x0,x1);ys=[]
 for x in xs:
  seed=round(ty+slope*(x-tx));y=np.arange(seed-7,seed+8);score=g[y,x]-(g[y-3,x]+g[y+3,x])/2;ys.append(int(y[score.argmin()]))
 ys=np.array(ys);c=np.polyfit(xs,ys,1)
 for _ in range(5):
  keep=np.abs(ys-np.polyval(c,xs))<2;c=np.polyfit(xs[keep],ys[keep],1)
 x=np.linspace(x0+5,x1-5,24);observed=np.polyval(c,x);h0=projected_polygon(k,0,0);h1=projected_polygon(k,par['removed_bottom_count'],par['right_trim_scene_units']);a=np.array([bottom_at_x(h0,t) for t in x]);b=np.array([bottom_at_x(h1,t) for t in x])
 out[k]={'native_source_search':[x0,x1,slope,tx,ty],'fit_y_ax_b':c.tolist(),'accepted_rows':int(keep.sum()),'median_image_ridge_fit_residual_px':float(np.median(np.abs(ys[keep]-np.polyval(c,xs[keep])))),'before_mean_abs_vertical_px':float(np.abs(a-observed).mean()),'after_mean_abs_vertical_px':float(np.abs(b-observed).mean()),'sample_x':x.tolist(),'observed_y':observed.tolist(),'before_y':a.tolist(),'after_y':b.tolist()}
 d=ImageDraw.Draw(im)
 for pts,col in [(list(zip(x,observed)),'#00e500'),(h0.tolist(),'#ff0033'),(h1.tolist(),'#0080ff')]:d.line(pts,fill=col,width=2)
 d.rectangle((15,880,1250,955),fill='white');ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22);d.text((25,890),k+' native: green observed bottom line; red before; blue candidate',font=ft,fill='black');d.text((25,923),'Fixed cameras. Endpoint/line improvement is not metric 3D calibration.',font=ft,fill='black');im.save(P/(k+'_bank1_evidence_native.png'))
(P/'bank1_line_check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:{a:b for a,b in v.items() if a.endswith('_px')} for k,v in out.items()},indent=2))
