import json,pathlib,hashlib,numpy as np
from scipy.optimize import minimize_scalar
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104'); O=pathlib.Path(__file__).parent
D=json.load(open(P/'source-diagnosis/landmarks-v1.json'));cam=json.load(open(P/'qa/R06-bounded-fit.json'));results={}
dirs={'C1':np.array([-1,1])/np.sqrt(2),'C2':np.array([1,1])/np.sqrt(2),'C3':np.array([1,-1])/np.sqrt(2),'C4':np.array([-1,-1])/np.sqrt(2)}
for num,name in [(13,'SOURCE_13_high'),(21,'SOURCE_21_high')]:
 im=next(d for d in D['images'] if pathlib.Path(d['source']).stem==str(num));p={x['id']:np.array(x['xy']) for x in im['landmarks']};A=[]
 for xy,uv in zip([p['S'+str(i)] for i in range(1,5)],[[0,1],[1,0],[0,-1],[-1,0]]):
  x,y=xy;u,v=uv;A.extend([[x,y,1,0,0,0,-u*x,-u*y,-u],[0,0,0,x,y,1,-v*x,-v*y,-v]])
 H=np.linalg.svd(A)[2][-1].reshape(3,3);cs={}
 chosen=min([t for t in cam[name]['all_focal_trials'] if t['inside_conservative_box']],key=lambda t:t['mean']);M=np.array(chosen['matrix_world']);f=chosen['lens']/36*1192
 def project(k,r):
  world=np.r_[dirs[k]*r,.495];q=(world-M[:3,3])@M[:3,:3];return np.array([596+f*q[0]/(-q[2]),335.5-f*q[1]/(-q[2])])
 for k in dirs:
  if k not in p:continue
  q=H@[*p[k],1];q=q[:2]/q[2];cs[k]={'observed':p[k].tolist(),'conditional_planar_xy':q.tolist(),'radius_ratio':float(np.linalg.norm(q)),'R06_fixed_camera_projection':project(k,.68).tolist(),'R06_error_px':float(np.linalg.norm(project(k,.68)-p[k]))}
 results[name]={'source_sha256':im['sha256'],'homography':H.tolist(),'corners':cs,'fixed_camera':chosen}
def cost(r):return sum(np.linalg.norm(project_placeholder)**2 for project_placeholder in [])
# Fit a single common concave radius, keep all cameras and outer-tip geometry fixed.
def errors(radius):
 vals=[]
 for name,rec in results.items():
  M=np.array(rec['fixed_camera']['matrix_world']);f=rec['fixed_camera']['lens']/36*1192
  for k,c in rec['corners'].items():
   q=(np.r_[dirs[k]*radius,.495]-M[:3,3])@M[:3,:3];pp=np.array([596+f*q[0]/-q[2],335.5-f*q[1]/-q[2]]);vals.append(float(np.linalg.norm(pp-c['observed'])))
 return vals
fit=minimize_scalar(lambda r:sum(e*e for e in errors(r)),bounds=(.25,1.4),method='bounded');out={'limitations':'Diagnostic only: old manual points may mix metal-band inner/outer edges; correspondence audit pending. Four tips enforce equal-radius orthogonal planar hypothesis. Camera is unaccepted R06 fixed pose. Fit is training, not validation, not applied to models. No native imagery. All seven visible old concave points retained.','baseline_radius':.68,'fit_radius':float(fit.x),'baseline_errors':errors(.68),'fit_errors':errors(fit.x),'sources':results}
(O/'diagnosis.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:out[k] for k in ['baseline_radius','fit_radius','baseline_errors','fit_errors']},indent=2))
