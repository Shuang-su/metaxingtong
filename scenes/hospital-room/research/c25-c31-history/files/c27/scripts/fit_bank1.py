from pathlib import Path
import numpy as np,json,hashlib
from scipy.optimize import minimize_scalar
R=Path(__file__).resolve().parents[2];P=R/'c27';j=json.loads((P/'blinds_projection_source.json').read_text())
names=sorted(n for n in j['objects'] if n.startswith('Blind bank 1'))
obs={'H':[947.,204.],'G':[343.,254.],'N642':[617.,172.]}
files={'H':'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','G':'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','N642':'BV1GqXMByE1s_642.617525_right_turn_native.png'}
right=max(np.array(j['objects'][names[0]]['world_vertices'])[:,0])
def proj(k,idx,delta):
 v=np.array(j['objects'][names[idx]]['world_vertices']);xmin=v[:,0].min();xmax=v[:,0].max()
 v[:,0]=xmin+(v[:,0]-xmin)*(xmax+delta-xmin)/(xmax-xmin)
 # One consistent visible lower cap vertex, not an arbitrary in-plane sample.
 cap=v[v[:,0]>v[:,0].max()-1e-6];q=np.c_[cap,np.ones(len(cap))]@np.array(j['cameras'][k]['projection']).T
 uv=q[:,:2]/q[:,3:4];uv=np.c_[(uv[:,0]+1)*960,(1-uv[:,1])*540]
 return uv[np.argmax(uv[:,1])]
trials=[]
for removed in range(3):
 def objective(x):return sum(np.sum((proj(k,removed,x)-obs[k])**2) for k in ['H','G'])
 fit=minimize_scalar(objective,bounds=(-.18,0),method='bounded',options={'xatol':1e-10})
 trials.append({'removed_bottom_count':removed,'right_trim_scene_units':float(fit.x),'fit_rmse_px':float(np.sqrt(fit.fun/4))})
best=min(trials,key=lambda x:x['fit_rmse_px']);i=best['removed_bottom_count'];dx=best['right_trim_scene_units']
out={'fit_views':['H','G'],'check_view':'N642 (previously viewed, not used in this parameter fit; NOT blind test)','source_vertices':'blinds_projection_source.json','endpoint_definition':'Visible lowest remaining slat right tip, lower cap envelope; manually reviewed native endpoints','manual_native_uncertainty_px':2,'observation_xy':obs,'sources':{k:{'name':f,'sha256':hashlib.sha256((R/'inputs'/f).read_bytes()).hexdigest()} for k,f in files.items()},'target_group':names,'fixed':['all cameras','chairs and other furniture','all non-bank1 geometry','left endpoints','slat depth/thickness','remaining slat spacing'],'trials_H_G_only':trials,'selected_H_G_only':best,'before_right_extent':float(right),'after_right_extent':float(right+dx),'results':{}}
for k in obs:
 a=proj(k,0,0);b=proj(k,i,dx);out['results'][k]={'before_xy':a.tolist(),'after_xy':b.tolist(),'before_endpoint_distance_px':float(np.linalg.norm(a-obs[k])),'after_endpoint_distance_px':float(np.linalg.norm(b-obs[k]))}
out['status']='candidate for real rendering and full-scene checks, not spatial calibration'
(P/'bank1_fit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['trials_H_G_only','selected_H_G_only','results']},indent=2))
