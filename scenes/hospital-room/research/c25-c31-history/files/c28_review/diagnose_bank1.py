import json,pathlib,numpy as np
from scipy.optimize import least_squares
R=pathlib.Path(__file__).resolve().parents[1];P=R/'c27';O=R/'c28_review'
j=json.loads((P/'blinds_projection_source.json').read_text());f=json.loads((P/'bank1_fit.json').read_text());l=json.loads((P/'bank1_line_check.json').read_text());names=f['target_group'];v=np.array(j['objects'][names[1]]['world_vertices']);lo=v[:,0].min();hi=v[:,0].max();v[:,0]=lo+(v[:,0]-lo)*(hi+f['selected_H_G_only']['right_trim_scene_units']-lo)/(hi-lo)
obs={k:np.array(f['observation_xy'][k]) for k in ['H','G','N642']};proj={k:np.array(j['cameras'][k]['projection']) for k in obs};cap=v[v[:,0]>v[:,0].max()-1e-6]
def project(k,x):
 q=np.c_[np.atleast_2d(x),np.ones(len(np.atleast_2d(x)))]@proj[k].T;uv=q[:,:2]/q[:,3:4];return np.c_[(uv[:,0]+1)*960,(1-uv[:,1])*540]
def tip(k,x):
 uv=project(k,x);return uv[np.argmax(uv[:,1])]
def residual(k,x):return project(k,x)[0]-obs[k]
basepoint=cap[np.argmax(project('H',cap)[:,1])];out={'basepoint':basepoint.tolist(),'cap_indices':{k:int(np.argmax(project(k,cap)[:,1])) for k in obs},'basepoints':{k:cap[np.argmax(project(k,cap)[:,1])].tolist() for k in obs},'jacobian_px_per_world_unit':{},'fits':{}}
for k in obs:
 eps=1e-5;J=np.stack([(project(k,basepoint+eps*np.eye(3)[i])[0]-project(k,basepoint-eps*np.eye(3)[i])[0])/(2*eps) for i in range(3)],axis=1);out['jacobian_px_per_world_unit'][k]=J.tolist()
for views in [['H','G'],['H','G','N642']]:
 def fun(delta):return np.concatenate([residual(k,basepoint+delta) for k in views])
 for bound in [0.02,0.05,0.1,0.2,0.5,2,100]:
  res=least_squares(fun,[0,0,0],bounds=(-bound,bound));point=basepoint+res.x;key='_'.join(views)+'_limit_'+str(bound);out['fits'][key]={'delta_xyz':res.x.tolist(),'endpoint_rmse_px':float(np.sqrt(np.mean(np.array(res.fun).reshape(-1,2)**2)*2)),'residuals_px':{k:residual(k,point).tolist() for k in obs},'endpoint_error_px':{k:float(np.linalg.norm(residual(k,point))) for k in obs}}
# Joint linear condition and endpoint delta from least squares, for reference.
J=np.concatenate([np.array(out['jacobian_px_per_world_unit'][k]) for k in ['H','G']]);sv=np.linalg.svd(J,compute_uv=False);out['HG_jacobian_singular_values']=sv.tolist();out['HG_condition']=float(sv[0]/sv[-1]);out['HG_linear_delta_xyz']=np.linalg.lstsq(J,np.concatenate([obs[k]-project(k,basepoint)[0] for k in ['H','G']]),rcond=None)[0].tolist()
# Baseline bottom line slope and signed residuals.
out['bottom_lines']={}
for k,z in l.items():
 x=np.array(z['sample_x']);y=np.array(z['after_y']);c=np.polyfit(x,y,1);out['bottom_lines'][k]={'candidate_slope':float(c[0]),'observed_slope':z['fit_y_ax_b'][0],'signed_mean_error_px':float(np.mean(y-z['observed_y'])),'residual_at_left_right_px':(y-np.array(z['observed_y']))[[0,-1]].tolist()}
(O/'endpoint_diagnosis.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
