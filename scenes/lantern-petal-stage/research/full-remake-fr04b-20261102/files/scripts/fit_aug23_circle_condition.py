# Single fixed-f work condition, ring silhouette soft points only. No model edits or f sweep.
import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
D=Path(__file__).resolve().parents[1];q=json.load(open(D/'qa/aug23-upperlip-soft-points-independent.json'));uv=np.array([p['xy_native'] for p in q['points']],float);a=np.arange(2048)*2*np.pi/2048;circle=np.c_[5*np.cos(a),5*np.sin(a),np.full(len(a),.34)];f=4000.;pp=np.array([1920,1080]);
def camera(p):
 C=np.array([0.,-np.exp(p[0]),np.exp(p[1])]);target=np.array([p[2],p[3],.34]);fw=target-C;fw/=np.linalg.norm(fw);right=np.cross(fw,[0,0,1]);right/=np.linalg.norm(right);down=np.cross(fw,right);R=np.array([np.cos(p[4])*right+np.sin(p[4])*down,-np.sin(p[4])*right+np.cos(p[4])*down,fw]);return C,R

def points(p):
 C,R=camera(p);v=(circle-C)@R.T;return v[:,:2]/v[:,2,None]*f+pp

def residual(p):
 pts=points(p);return np.sqrt(((uv[:,None,:]-pts[None,:,:])**2).sum(axis=2).min(axis=1))/12
p0=[np.log(35),np.log(35),0,0,0];res=least_squares(residual,p0,bounds=([np.log(10),np.log(5),-10,-10,-.5],[np.log(100),np.log(100),10,10,.5]),max_nfev=400,diff_step=1e-4);C,R=camera(res.x);err=residual(res.x)*12;out={'status':'conditional single-circle training diagnostic, NOT calibration or source acceptance','source':q['source'],'source_sha256':q['source_sha256'],'resolution':[3840,2160],'fixed_f_pixels':f,'fixed_principal_point':pp.tolist(),'camera_center':C.tolist(),'world_to_camera':R.tolist(),'world_azimuth_gauge':'camera x=0,y<0 chosen convention; circle cannot identify global azimuth of roof/columns','circle_virtual_midline':{'r':5,'z':.34,'entity':'STAGE_UPPER_LIP has finite band r4.965..5.035,z.315..365; midline is not exact visible edge'},'point_count':len(uv),'all_points_training_no_holdout':True,'normal_distance_approx_px':err.tolist(),'max_px':float(err.max()),'mean_px':float(err.mean()),'termination':str(res.message),'parameters':res.x.tolist(),'limits':['working scale radius5 not metres','f4000 is predefined illustrative condition; no search or focal calibration','one circle alone leaves azimuth/depth-scale and geometry ambiguities','finite lip width, source reflections and physical top-vs-band edge unresolved','all other objects must be judged independently; do not hide poor roof/urn alignment by circle fit']};(D/'qa/aug23-circle-work-camera.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
