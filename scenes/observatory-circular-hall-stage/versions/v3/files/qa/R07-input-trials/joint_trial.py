import json,pathlib,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
P=pathlib.Path(__file__).parent;d=json.load(open(P/'diagnosis.json'));L=json.load(open(P.parent/'observatory-candidate-20261104/source-diagnosis/landmarks-v1.json'));x0=[.68];records=[]
dirs={'S1':[0,1],'S2':[1,0],'S3':[0,-1],'S4':[-1,0],'C1':np.array([-1,1])/np.sqrt(2),'C2':np.array([1,1])/np.sqrt(2),'C3':np.array([1,-1])/np.sqrt(2),'C4':np.array([-1,-1])/np.sqrt(2)}
for number,name in [(13,'SOURCE_13_high'),(21,'SOURCE_21_high')]:
 rec=d['sources'][name];M=np.array(rec['fixed_camera']['matrix_world']);R=M[:3,:3].T;x0.extend([*Rotation.from_matrix(R).as_rotvec(),*(-R@M[:3,3])]);im=next(i for i in L['images'] if pathlib.Path(i['source']).stem==str(number));pts=[p for p in im['landmarks'] if p['id'] in dirs];records.append((name,pts,rec['fixed_camera']['lens']))
def projs(x):
 out=[]
 for i,(name,pts,lens) in enumerate(records):
  p=x[1+6*i:7+6*i];world=np.array([[*(np.array(dirs[k['id']])*(2.4 if k['id'].startswith('S') else x[0])),.495] for k in pts]);v=world@Rotation.from_rotvec(p[:3]).as_matrix().T+p[3:];z=-v[:,2];uv=np.c_[596+lens/36*1192*v[:,0]/z,335.5-lens/36*1192*v[:,1]/z];out.append((uv,z))
 return out
def fun(x):
 return np.concatenate([np.r_[(uv-np.array([p['xy'] for p in rec[1]])).ravel(),np.minimum(z-.05,0)*1000] for (uv,z),rec in zip(projs(x),records)])
fit=least_squares(fun,x0,bounds=([.25]+[-np.inf]*12,[1.4]+[np.inf]*12),max_nfev=3000,xtol=1e-12,ftol=1e-12,gtol=1e-12);out={'scope':'Unapplied numerical trial. Both fixed focal camera poses plus one shared concave radius use all fifteen old manually marked tips/corners. Edge semantic review pending. Not independent validation, physical calibration, or source acceptance. No deleted adverse points.','baseline_radius':.68,'fitted_radius':float(fit.x[0]),'sources':{}}
for i,((name,pts,lens),(uv,z),(old,zold)) in enumerate(zip(records,projs(fit.x),projs(x0))):
 p=fit.x[1+6*i:7+6*i];R=Rotation.from_rotvec(p[:3]).as_matrix();M=np.eye(4);M[:3,:3]=R.T;M[:3,3]=-R.T@p[3:];obs=np.array([q['xy'] for q in pts]);out['sources'][name]={'point_ids':[q['id'] for q in pts],'lens':lens,'observed':obs.tolist(),'baseline_error_px':np.linalg.norm(old-obs,axis=1).tolist(),'fit_error_px':np.linalg.norm(uv-obs,axis=1).tolist(),'depth':z.tolist(),'matrix_world':M.tolist(),'radial':float(np.linalg.norm(M[:2,3])),'height':float(M[2,3])}
(P/'joint-trial.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
