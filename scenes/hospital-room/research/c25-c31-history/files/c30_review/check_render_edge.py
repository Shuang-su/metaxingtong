from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy.ndimage import gaussian_filter1d
R=Path(__file__).resolve().parents[1];D=R/'c30_review';m=json.load(open(R/'c30/four_view_edge_metrics.json'));out={}
for k,entry in m['views'].items():
 a=np.asarray(Image.open(R/f'c30/region_tests/{k}_C30_REGION_ONLY.png').convert('RGB'),float);rows=[]
 for (x,y),pred in zip(entry['source_points'],entry['C30']['predicted_edge_y']):
  lo=max(0,int(pred)-30);hi=min(1080,int(pred)+40);prof=gaussian_filter1d(a[lo:hi,x-2:x+3].mean((1,2)),1.5);g=np.diff(prof);idx=int(np.argmax(g));edge=lo+idx
  rows.append({'x':x,'source_y':y,'analytic_top_line_y':pred,'observed_positive_gradient_edge_y':edge,'observed_source_residual_px':edge-y,'analytic_vs_render_offset_px':edge-pred,'edge_gradient':float(g[idx]),'search_y_half_open':[lo,hi]})
 out[k]=rows
(D/'actual_render_edge_observations.json').write_text(json.dumps({'method':'positive vertical intensity gradient in local candidate ROI, sigma1.5 and 5-column average; manual visual context required; not a mesh silhouette mask','views':out},indent=2));print(json.dumps(out,indent=2))
