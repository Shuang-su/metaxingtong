from pathlib import Path
import json,numpy as np
from scipy.optimize import minimize_scalar,brentq
R=Path(__file__).resolve().parents[1];D=R/'c30_diagnosis';obs=json.load(open(D/'corrected_bed_edge_observations.json'));bounds=json.load(open(D/'bed_actual_world_bounds.json'));cams=json.load(open(R/'c27/blinds_projection_source.json'))['cameras'];base=bounds['Bed • mattress and sheet']['max'][2];Y=obs['fixed_far_y'];Xbounds=[bounds['Bed • mattress and sheet']['min'][0],bounds['Bed • mattress and sheet']['max'][0]]
pts={k:np.array([r['pixel'] for r in rows],float) for k,rows in obs['views'].items()}
def pred(k,z,y=Y):
 p=np.array(cams[k]['projection']);u=pts[k][:,0]/960-1
 x=(u*(p[3,1]*y+p[3,2]*z+p[3,3])-(p[0,1]*y+p[0,2]*z+p[0,3]))/(p[0,0]-u*p[3,0]);q=np.c_[x,np.full(len(x),y),np.full(len(x),z),np.ones(len(x))]@p.T
 return (1-q[:,1]/q[:,3])*540,x,q[:,3]
def residual(k,z,y=Y,shift=0):return pred(k,z,y)[0]-pts[k][:,1]-shift
def fit(keys,y=Y,shift=0):
 f=lambda z:sum(np.sum(residual(k,z,y,shift)**2) for k in keys)
 z=float(minimize_scalar(f,bounds=(base,base+.25),method='bounded',options={'xatol':1e-13}).x);return z

def summarize(z):
 out={}
 for k in pts:
  v,x,q=pred(k,z);rr=residual(k,z);out[k]={'residual_y_px':rr.tolist(),'range_px':[float(rr.min()),float(rr.max())],'rmse_px':float(np.sqrt(np.mean(rr**2))),'mean_px':float(rr.mean()),'intersected_world_x':x.tolist(),'inside_existing_x_extent':bool(((x>=Xbounds[0])&(x<=Xbounds[1])).all()),'all_in_front':bool((q>0).all())}
 return out
out={'method':'Current shared cameras and existing far y, x extent fixed. At each observed image x, solve the 3D line intersection x then compare projected image y. Positive residual = model edge below source. No H used. No model edit.','source_points':{k:p.tolist() for k,p in pts.items()},'base_z':base,'fixed_far_y':Y,'existing_x_extent':Xbounds,'scan':[],'fits':{},'sensitivity':{}}
for dz in [0,.10,.11,.12,.13,.14,.15,.16]:out['scan'].append({'delta_z':dz,'z':base+dz,'views':summarize(base+dz)})
for label,keys in [('G',['G']),('N642',['N642']),('joint',['G','N642'])]:
 z=fit(keys);out['fits'][label]={'z':z,'delta_z':z-base,'views':summarize(z)}
 out['sensitivity'][label]={'global_observed_y_shift_pm2_fit_z':[fit(keys,shift=2),fit(keys,shift=-2)],'global_observed_y_shift_pm4_fit_z':[fit(keys,shift=4),fit(keys,shift=-4)],'fixed_far_y_minus_plus_0_01_fit_z':[fit(keys,y=Y-.01),fit(keys,y=Y+.01)]}
for k in pts:
 out['sensitivity'][k]['individual_point_z_pm4_intervals']=[]
 for i in range(3):
  lo=brentq(lambda z:residual(k,z)[i]-4,base,base+.25);hi=brentq(lambda z:residual(k,z)[i]+4,base,base+.25);out['sensitivity'][k]['individual_point_z_pm4_intervals'].append([lo,hi])
(D/'height_projection_fit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'fits':out['fits'],'sensitivity':out['sensitivity']},indent=2))
