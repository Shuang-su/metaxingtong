from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];P=R/'c28'
spec={'H':('hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png',900,[195,171,147,124,100],.174,(650,925),(935,962)), 'G':('hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png',300,[242,216,190,165,140],.28,(80,325),(330,370))}
spec['N642']=('BV1GqXMByE1s_642.617525_right_turn_native.png',550,[157,131,105,81,57],.196,(350,600),(605,635))
out={}
for k,(f,xref,seeds,slope,domain,ends) in spec.items():
 im=Image.open(R/'inputs'/f).convert('RGB');g=np.array(im,float).mean(2);draw=ImageDraw.Draw(im);lines=[]
 for idx,yseed in enumerate(seeds):
  xs=np.arange(*domain);ys=[]
  for x in xs:
   local_slope=(.1905+.006*idx) if k=='H' else ((.276+.011*idx) if k=='G' else (.224+.010*idx));yc=round(yseed+local_slope*(x-xref));y=np.arange(yc-5,yc+6);score=g[y,x]-(g[y-3,x]+g[y+3,x])/2;ys.append(int(y[score.argmin()]))
  ys=np.array(ys);c=np.polyfit(xs,ys,1)
  for _ in range(5):
   keep=np.abs(ys-np.polyval(c,xs))<2;c=np.polyfit(xs[keep],ys[keep],1)
  trace=[]
  for x in range(ends[0]-20,ends[1]+1):
   yc=round(np.polyval(c,x));y=np.arange(yc-2,yc+3);contrast=(g[y-3,x]+g[y+3,x])/2-g[y,x];trace.append([x,float(contrast.max())])
  t=np.array(trace);baseline=np.median(t[:15,1]);threshold=max(2.,baseline*.4);cand=t[(t[:,0]>=ends[0])&(t[:,1]>=threshold),0];end=float(cand.max()) if len(cand) else None
  lines.append({'remaining_slat_index':idx+2,'source_native_seed':[xref,yseed],'fit_y_ax_b':c.tolist(),'search_domain':domain,'inlier_count':int(keep.sum()),'median_ridge_residual':float(np.median(np.abs(ys[keep]-np.polyval(c,xs[keep])))),'endpoint_contrast_trace':trace,'threshold_heuristic':threshold,'candidate_endpoint_xy':None if end is None else[end,float(np.polyval(c,end))],'endpoint_status':'image contrast heuristic, needs visual review; not an approved fitting landmark'})
  draw.line([(domain[0],np.polyval(c,domain[0])),(ends[1],np.polyval(c,ends[1]))],fill=(0,220,0),width=1)
  if end:draw.ellipse((end-3,np.polyval(c,end)-3,end+3,np.polyval(c,end)+3),outline='red',width=1)
 out[k]={'source':f,'lines':lines};im.save(P/(k+'_upper_lines_native.png'))
(P/'upper_line_observations.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:[(q['remaining_slat_index'],q['candidate_endpoint_xy'],q['fit_y_ax_b']) for q in v['lines']] for k,v in out.items()},indent=2))
