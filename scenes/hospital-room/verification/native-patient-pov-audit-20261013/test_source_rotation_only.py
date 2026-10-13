"""Point-only bearing test. Never resample, align, register, or warp image pixels."""
from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).parent
farA=np.array([[1026,604],[1557,578],[1584,892],[536,296],[744,475]],float)
farB=np.array([[1009,584],[1552,559],[1577,877],[507,271],[722,452]],float)
# Endboard aperture top tangency/edge points: static object features, not bright patches.
nearA=np.array([[850,976],[938,976],[1080,970],[1370,968],[1515,970]],float)
nearB=np.array([[830,1011],[937,1010],[1080,1006],[1380,1005],[1550,1009]],float)

def proj(x,p,variable):
 fa=np.exp(x[3]);fb=np.exp(x[4]) if variable else fa
 r=np.c_[(p-np.array([960,540]))/fa,np.ones(len(p))]@Rotation.from_rotvec(x[:3]).as_matrix().T
 return r[:,:2]/r[:,2,None]*fb+np.array([960,540])
rows=[]
for variable in [False,True]:
 bounds=(np.r_[[-.15]*3,np.log([1100]*(2 if variable else 1))],np.r_[[.15]*3,np.log([3000]*(2 if variable else 1))]);st=np.r_[[0,0,0],np.log([1900]*(2 if variable else 1))]
 sol=least_squares(lambda x:(proj(x,farA,variable)-farB).ravel()/3,st,bounds=bounds,max_nfev=5000)
 e=proj(sol.x,farA,variable)-farB;h=proj(sol.x,nearA,variable)-nearB
 rows.append({'free_focal_ratio':variable,'rotation_vector_radians':sol.x[:3].tolist(),'focal_A_px':float(np.exp(sol.x[3])),'focal_B_px':float(np.exp(sol.x[4] if variable else sol.x[3])),'far_train_rms_euclidean_px':float(np.sqrt(np.mean((e**2).sum(1)))),'near_holdout_rms_euclidean_px':float(np.sqrt(np.mean((h**2).sum(1)))),'near_holdout_residual_xy':h.tolist(),'far_residual_xy':e.tolist()})
(R/'source_only_motion_test.json').write_text(json.dumps({'method':'Point-only rotation bearing test fitted to 3 TV-frame corners, middle mullion top and ceiling junction; five near endboard features held out. No D coordinates used. No pixels transformed.','manual_feature_uncertainty_px':8,'far_A':farA.tolist(),'far_B':farB.tolist(),'near_A':nearA.tolist(),'near_B':nearB.tolist(),'tests':rows,'conclusion':'Near/far displacement is inconsistent with a single optical-center rotation at plausible focal lengths, even with a free focal ratio. This supports depth-dependent parallax conditional on a static endboard, but does not identify pure horizontal translation, physical scale, or unique camera trajectory.'},indent=2));print(json.dumps(rows,indent=2))
