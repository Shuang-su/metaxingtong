"""Read-only image-space scanline check. No scene or render alteration.
The local search windows were selected after visual inspection of true visible boundaries.
Source left pillar/fold transition is soft; report a manual interval, not exact geometry.
"""
from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parent.parent;S=R.parent/'hospital_anchor_preparation_20261014/restored'
SOURCES={'G':S/'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','H':S/'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','F':S/'hospital-F-tv-BV1GqXMByE1s-t1823.678156-native.png'}
coords={'G':[(500,1162,1156),(900,1171,1169),(1050,1174,1174)],'H':[(300,1801,1802),(500,1814,1815),(700,1827,1828)],'F':[(500,394,377),(700,381,371),(900,367,364),(1050,357,359)]}
res={}
def edge(arr,y,guess,positive=True,half=9):
 row=np.median(arr[y-2:y+3,:,:3],axis=0).mean(axis=1)
 grad=row[4:]-row[:-4]
 lo,hi=guess-half,guess+half
 vals=grad[lo-2:hi-2]
 return int(lo+(np.argmax(vals) if positive else np.argmin(vals)))
for k,rows in coords.items():
 a=np.asarray(Image.open(SOURCES[k])); b=np.asarray(Image.open(R/'renders_C3'/f'{k}_C3_RAW_1920x1080.png'))
 vals=[]
 for y,xs,xc in rows:
  s=edge(a,y,xs);c=edge(b,y,xc);vals.append({'y':y,'source_right_edge_x':s,'C3_right_edge_x':c,'C3_minus_source_px':c-s,'sample_uncertainty_px':2,'visibility':'Both right outside contours actually visible in the native raw/source images; no sofa occlusion.'})
 source_left={'G':[1020,1030],'H':[1640,1650],'F':[218,228]}[k]
 c_left=edge(b,500,{'G':1087,'H':1733,'F':294}[k],positive=False)
 c_right=vals[[v['y'] for v in vals].index(500)]['C3_right_edge_x'];s_right=vals[[v['y'] for v in vals].index(500)]['source_right_edge_x']
 res[k]={'right_outer_visible_scanlines':vals,'visible_fold_width_y500':{'source_left_transition_interval_x':source_left,'source_left_interval_note':'Manual visual band for soft pillar/fold transition, supported by RGB profiles; not an exact physical contact line.','source_width_interval_px':[s_right-source_left[1],s_right-source_left[0]],'C3_pillar_to_fold_boundary_x':c_left,'C3_width_px':c_right-c_left,'C3_boundary_uncertainty_px':2}}
(R/'independent_visual/visible_scanline_measurements.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
print(json.dumps(res,ensure_ascii=False,indent=2))
