import numpy as np,json
from pathlib import Path
from scipy.spatial.transform import Rotation
D=Path(__file__).resolve().parents[1];v1=json.load(open(D/'qa/R09-camera-fit.json'))['results'][2];v2=json.load(open(D/'qa/R09b-camera-fit.json'))['results'][2];front=json.load(open(D/'sources/landmarks-v2/landmarks-v2-review-F09.json'))['additional_front_contour_samples'];theta=np.arange(1024)*2*np.pi/1024;world=np.c_[.301*np.cos(theta),1.25+.301*np.sin(theta),np.zeros(1024)]
def distances(p):
 c=(world-np.array(p[:3]))@Rotation.from_rotvec(p[3:]).as_matrix();uv=np.c_[1920+v2['fixed_focal_px']*c[:,0]/(-c[:,2]),1080-v2['fixed_focal_px']*c[:,1]/(-c[:,2])];a=uv;b=np.roll(a,-1,axis=0);ab=b-a;out=[]
 for point in front:
  u=np.array(point['xy_native']);t=np.clip(((u-a)*ab).sum(1)/(ab*ab).sum(1),0,1);dist=np.min(np.linalg.norm(a+t[:,None]*ab-u,axis=1));out.append(dict(point,error_px=float(dist)))
 return out
rows=[]
for name,p in [('R08_initial',v1['initial']),('R09_v1_used_ambiguous_F09',v1['fitted']),('R09b_selected',v2['fitted'])]+[(f'R09b_start{i}_solution',r['solution']) for i,r in enumerate(v2['runs'])]:
 ds=distances(p);rows.append({'candidate':name,'pose':p,'new_front_diagnostic_points':ds,'mean_px':float(np.mean([x['error_px'] for x in ds])),'max_px':float(max(x['error_px'] for x in ds))})
common=[x for x in v1['training'] if x['id']!='F09'];after=v2['training'];r={'method':'Newly annotated visible front contour not included in either fit. Seen-source follow-up diagnostic, not blind test. Distance to same hypothetical R08 base cap circle r.301 z0, not whole mesh silhouette proof.','front_diagnostics':rows,'common_8_training_comparison':{'r09_v1_excluding_invalid_F09':{'mean':float(np.mean([x['after_error_px'] for x in common])),'max':float(max(x['after_error_px'] for x in common))},'r09b':{'mean':float(np.mean([x['after_error_px'] for x in after])),'max':float(max(x['after_error_px'] for x in after))}},'limit':'F09 invalidation removes unreliable endpoint semantics, but R09b worsens some remaining training points. No claim of uniform improvement or calibration.'};(D/'qa/R09b-alternative-diagnostics.json').write_text(json.dumps(r,indent=2));print([(x['candidate'],x['mean_px'],x['max_px']) for x in rows])
