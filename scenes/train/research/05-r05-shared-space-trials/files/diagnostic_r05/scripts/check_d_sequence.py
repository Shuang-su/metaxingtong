import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[1];cam=np.array(json.loads((R/'analysis/seat_contour_refined_fit.json').read_text())['shared_head_and_rack_height']['cameras']['D']['camera'])
pairs=[]
for y,q in zip([-1.88,-.53,.82,2.17,3.52],[[723,171],[750,244],[766,284],[775,312],[782,328]]):pairs.append(([0,y,2.565],np.array(q)-[0,27]))
for side,q in [(-1,[750,353]),(1,[819,352])]:pairs.append(([side*.445,5.4345,2.545],np.array(q)-[0,27]))
P=np.array([p for p,q in pairs]);Q=np.array([q for p,q in pairs])
def project(v,p):
 c=(np.array(p)-v[:3])@Rotation.from_euler('xyz',v[3:6]).as_matrix();f=v[-1]*1180/36;return np.column_stack([590+f*c[:,0]/-c[:,2],332-f*c[:,1]/-c[:,2]])
s=least_squares(lambda a:(project(np.r_[cam[:3],a,cam[-1]],P)-Q).ravel(),cam[3:6],loss='soft_l1',f_scale=4)
v=np.r_[cam[:3],s.x,cam[-1]];out={'source':'Dseq_03_clean_paused.jpg','role':'same D baseline temporal continuation; not independent side-to-side baseline','camera_d2':cam.tolist(),'camera_dseq3_rotation_only':v.tolist(),'train_errors':np.linalg.norm(project(v,P)-Q,axis=1).tolist(),'holdout':[]}
for n,p,q in [('near_two_back_N1',[.4425,-3.72,1.28],[790,548]),('near_two_back_N2',[.4425,-1.92,1.28],[806,480]),('left_head_strip',[-1.368,-2.7,1.787],[294,331]),('door_window_top',[0,5.448,2.1],[787,390])]:
 target=np.array(q)-[0,27];pr=project(v,[p])[0];out['holdout'].append({'name':n,'source':target.tolist(),'projected':pr.tolist(),'error_px':float(np.linalg.norm(pr-target))})
(R/'analysis/Dseq3_rotation_holdout.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
