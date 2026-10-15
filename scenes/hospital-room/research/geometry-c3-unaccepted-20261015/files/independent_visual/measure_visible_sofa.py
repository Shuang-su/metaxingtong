from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parent.parent
samples={'G':{'left':[(227,894),(309,885),(422,879),(528,875),(588,877)],'right':[(802,868),(839,864),(868,866)]},'H':{'left':[(882,804),(963,798),(1080,795),(1196,793)],'right':[(1332,791),(1440,787),(1481,788)]}}
res={'excluded_samples': [{'view':'H','source_xy':[1228,798],'reason':'Dark shoulder / inter-cushion shadow makes color-threshold extraction unreliable; do not interpret threshold crossing as outer contour.'},{'view':'H','source_xy':[1493,793],'reason':'Rounded shoulder is not a right straight-side correspondence.'}]}
for view,parts in samples.items():
 res[view]={}
 for variant in ['D','C2','C3']:
  a=np.asarray(Image.open(R/('renders_D_baseline' if variant=='D' else f'renders_{variant}')/f'{view}_{variant}_RAW_1920x1080.png')).astype(float)
  rr={}
  for part,points in parts.items():
   rr[part]=[]
   for x,sy in points:
    v=np.median(a[740:940,x-1:x+2,:3],axis=1);is_sofa=(v[:,0]-v[:,1]>38)&(v[:,0]-v[:,2]>55)
    valid=np.where(np.convolve(is_sofa.astype(int),np.ones(4,dtype=int),'valid')==4)[0]
    cy=int(valid[0]+740) if len(valid) else None
    rr[part].append({'source_xy':[x,sy],'render_xy':[x,cy],'dy_render_minus_source_px':cy-sy if cy is not None else None,'uncertainty_px':4,'branch':'visible upper silhouette; no hidden continuation or rounded-shoulder side-edge matching'})
  res[view][variant]=rr
(R/'independent_visual/visible_sofa_measurements.json').write_text(json.dumps(res,ensure_ascii=False,indent=2));print(json.dumps(res,ensure_ascii=False))
