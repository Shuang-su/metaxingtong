import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
src=np.array([[70,162],[75,257],[510,99],[535,200]],float);dst=np.array([[-1.045,3.58],[-1.045,3.12],[1.045,3.58],[1.045,3.12]])
a=[];b=[]
for (u,v),(x,z)in zip(src,dst):a.extend([[u,v,1,0,0,0,-x*u,-x*v],[0,0,0,u,v,1,-z*u,-z*v]]);b.extend([x,z])
h=np.append(np.linalg.solve(a,b),1).reshape(3,3)
def p(u,v):q=h@np.array([u,v,1]);return q[:2]/q[2]
out=[]
for lab,u,v,r in json.load(open(D/'qa/observed_gold_dots.json'))['points_manual_approximate_px']:
 c=p(u,v);rx=np.linalg.norm(p(u+r,v)-c);rz=np.linalg.norm(p(u,v+r)-c);out.append({'id':lab,'x':c[0],'z':c[1],'radius_working':(rx+rz)/2,'projected_radius_mapping_spread':[rx,rz]})
res={'method':'four approximate speaker projected centers to existing circle center x/z, conditional planar homography; NOT camera calibration','limitations':'speaker faces and board not exactly same y; ellipse centers not exact projected 3D centers; all existing physical sizes working assumptions; gold ellipse radii manually approximated; mapping useful only coarse local layout','source_crop_centers_px':src.tolist(),'dest_existing_working_xz':dst.tolist(),'points':out}
(D/'qa/gold_layout_conditional.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
