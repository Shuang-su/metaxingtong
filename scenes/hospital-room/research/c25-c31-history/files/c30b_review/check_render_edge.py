from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
R=Path(__file__).resolve().parents[1];D=R/'c30b_review';m=json.load(open(R/'c30b/four_view_edge_metrics.json'));out={}
for k,entry in m['views'].items():
 a=np.asarray(Image.open(R/f'c30b/region_tests/{k}_C30B_REGION_ONLY.png').convert('RGB'),float);rows=[];cand=entry[[key for key in entry if key not in ['source_points','C29']][0]]
 for (x,y),pred in zip(entry['source_points'],cand['predicted_edge_y']):
  row={'x':x,'source_y':y,'analytic_proxy_y_used_only_to_locate_search':pred}
  if pred>=1080:row.update({'visible_edge_y':None,'status':'ideal proxy already below image; inspect image column for absence, no extrapolated pixel score','residual_lower_bound_px_if_below_frame':1080-y});rows.append(row);continue
  lo=max(0,int(pred)-15);hi=min(1080,int(pred)+45);prof=gaussian_filter1d(a[lo:hi,x-2:x+3].mean((1,2)),1.5);g=np.diff(prof);pk,_=find_peaks(g,prominence=2);idx=int(np.argmax(g));edge=lo+idx
  row.update({'automatic_edge_y':edge,'automatic_source_residual_px':edge-y,'gradient':float(g[idx]),'positive_gradient_candidates':[[lo+int(t),float(g[t])] for t in pk],'search_y_half_open':[lo,hi]});rows.append(row)
 out[k]=rows
(D/'actual_render_edge_observations.json').write_text(json.dumps({'method':'appearance gradient with explicit censoring outside image; manual context review required','views':out},indent=2));print(json.dumps(out,indent=2))
