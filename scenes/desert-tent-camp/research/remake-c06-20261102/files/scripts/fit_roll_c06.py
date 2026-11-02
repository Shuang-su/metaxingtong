import numpy as np,json,math,time
from pathlib import Path
from scipy.optimize import least_squares
R=Path(__file__).resolve().parents[1];q=json.load(open(R/'qa/roll_c06/roll_native_review.json'));params=json.load(open(R/'qa/C01_parameters.json'))['camera_params_historical_working_transcription'];cams=[]
for p in params:
 c=np.array(p[:3]);fw=np.array([p[3],2,p[4]])-c;fw/=np.linalg.norm(fw);rt=np.cross(fw,[0,0,1]);rt/=np.linalg.norm(rt);up=np.cross(rt,fw);cams.append((c,np.array([rt,-up,fw]),p[5]))
def project(X,i):
 c,B,f=cams[i];a=(np.atleast_2d(X)-c)@B.T;return a[:,:2]/a[:,2,None]*f+[960,540]
def geometry(p,radius):
 axis=np.array([p[2],p[3],1.]);axis/=np.linalg.norm(axis);a=np.array([p[0],p[1],radius*np.sqrt(1-axis[2]**2)]);b=a+axis*p[4];u=np.cross(axis,[0,0,1.]);u/=np.linalg.norm(u);v=np.cross(axis,u);return a,b,axis,u,v
ang=np.arange(360)*np.pi/180;circle=np.stack([np.cos(ang),np.sin(ang)],axis=1)
def measure(p,radius,return_detail=False):
 a,b,axis,u,v=geometry(p,radius);radial=circle[:,0,None]*u+circle[:,1,None]*v;res=[];details=[]
 for i,record in enumerate(q['records']):
  row={'source':i+1};top=project(b+radius*radial,i);obs=np.array(record['upper_outline']);dist=np.min(np.linalg.norm(obs[:,None,:]-top[None,:,:],axis=2),axis=1);res.extend(dist/5);row['upper_arc_nearest_distance_px']=dist.tolist()
  for name,t in [('upper',.77),('lower',.25)]:
   c=a+(b-a)*t;view=cams[i][0]-c;visible=radial@view>=-.05;ring=project(c+radius*radial[visible],i);obs=np.array(record[name+'_band_visible_endpoints']);d=np.min(np.linalg.norm(obs[:,None,:]-ring[None,:,:],axis=2),axis=1);res.extend(d/6);normal=view-axis*np.dot(view,axis);normal/=np.linalg.norm(normal);mid=project(c+radius*normal,i)[0];dm=mid-np.array(record[name+'_band_soft_midpoint']);res.extend(dm/8);row[name+'_band_outline_distance_px']=d.tolist();row[name+'_soft_front_mid_projected']=mid.tolist();row[name+'_soft_mid_residual_px']=float(np.linalg.norm(dm))
  details.append(row)
 return details if return_detail else np.array(res)
lo=[-4.5,3.5,-1.2,-1.2,1.0];hi=[-1.5,9,1.5,1.8,2.5];starts=[[-2.9,6.3,.36,.93,1.55],[-2.8,6.6,.2,.6,1.7],[-3.1,5.8,.6,1.3,1.8],[-2.5,7,.1,.3,1.5]];runs=[]
for radius in [.28,.32,.36]:
 results=[]
 for seed in starts:
  fit=least_squares(lambda p:measure(p,radius),seed,bounds=(lo,hi),max_nfev=300,xtol=1e-9,ftol=1e-9,gtol=1e-9);a,b,axis,u,v=geometry(fit.x,radius);results.append({'parameters_bottomXY_tiltXY_length':fit.x.tolist(),'cost':float(np.dot(fit.fun,fit.fun)),'optimizer_success':bool(fit.success),'nfev':fit.nfev,'start':seed,'bottom_axis_center_working':a.tolist(),'top_axis_center_working':b.tolist(),'axis':axis.tolist(),'radius_working':radius,'details':measure(fit.x,radius,True),'bound_hit':bool(np.any(np.minimum(fit.x-lo,np.array(hi)-fit.x)<1e-4))})
 results.sort(key=lambda x:x['cost']);runs.append({'radius_working':radius,'runs':results,'selection_within_radius':'minimum declared two-source soft training cost only; no third'})
nom=next(x for x in runs if x['radius_working']==.32)['runs'][0];out={'stage':'C06 new conditional rolled-cloth candidate, not recovered original shape','observations':'same upper free-end arc and band regions; view-dependent outline-to-projected-circle distance, never paired outline point triangulation','fixed_source_cameras':params,'soft_uncertainty_px':{'upper_arc':5,'strap_extent':6,'front_band_midpoint':8},'working_assumptions':['circular cross-section straight roll; actual soft cloth differs','ground lower-cap tangency enforced as inferred support, not observed source contact','upper/lower strap fractions .77/.25 assumed; not measured','fixed radius profiles .28/.32/.36, scale arbitrary','nominal .32 chosen BEFORE viewing resulting source residuals; sensitivity profiles all retained'],'all_profiles':runs,'nominal_candidate':nom,'third_used':False,'source_acceptance':False};(R/'qa/roll_c06/conditional_fit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'nominal':nom,'profile_costs':[(x['radius_working'],x['runs'][0]['cost']) for x in runs]},indent=2))
