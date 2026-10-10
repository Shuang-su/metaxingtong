import json,numpy as np
from pathlib import Path
from scipy.optimize import minimize_scalar
R=Path('/workspace/scratch/fa58bfcf0425/garden_v4_horizontal_trial_20261010');G=R.parent/'garden_hd_revision_20261010';fits=json.load(open(G/'qa/joint_candidate_v3_conservative.json'))['fits'];cams={d['tag']:d for d in fits}
h=json.load(open(R.parent/'garden_hd_holdout_600_20261010/qa/holdout_fit.json'));cams['HD600']={**cams['HD1326'],'principal_point':h['principal_point'],'parameters':cams['HD1326']['parameters'][:6]+[h['lens_mm']*1180/36]}
obs={'HD668':[356,993],'HD1326':[276,894],'HD600':[171,1037],'HD1519':[362,1162]};unc={'HD668':[5,10],'HD1326':[5,8],'HD600':[5,5],'HD1519':[5,15]}
def project(tag,a):
 d=cams[tag];p=np.array(d['parameters']);B=np.array(d['camera_basis_cv']);w=np.array([[-a,-1.475,1.73],[a,-1.475,1.73]]);q=(w-p[:3])@B.T;return q[:,:2]/q[:,2:]*p[6]+d['principal_point']
train=['HD668','HD1326'];held=['HD600','HD1519']
def cost(a):return sum(np.sum(((project(tag,a)[:,0]-obs[tag])/unc[tag])**2)for tag in train)
f=minimize_scalar(cost,bounds=(1.8,6.0),method='bounded');a=float(f.x);rows=[]
for tag in train+held:
 before=project(tag,5);after=project(tag,a);row={'tag':tag,'split':'train'if tag in train else'held_out','source_mid_urn_centers_x':obs[tag],'marking_uncertainty_px':unc[tag],'baseline_projected_xy':before.tolist(),'trial_projected_xy':after.tolist(),'baseline_horizontal_residual_px':(before[:,0]-obs[tag]).tolist(),'trial_horizontal_residual_px':(after[:,0]-obs[tag]).tolist(),'trial_horizontal_rms_px':float(np.sqrt(np.mean((after[:,0]-obs[tag])**2)))};rows.append(row)
report={'single_shared_half_spacing':a,'baseline_half_spacing':5,'locked_y':-1.475,'locked_cap_z':1.73,'train':train,'held_out':held,'camera_policy':'All existing v3 camera poses/intrinsics frozen. HD600 uses the one previously recorded window-scale diagnostic. No per-frame geometry or new camera fitting.','rows':rows,'identification':'Cross-frame source middle urn pair identity independently reviewed; left/right exact same physical depth remains an assumption.','retracted_metric':'Earlier 600 report compared source middle urns to nearest-facade model row y=-.025. Its 160-180px figures are not accepted matched-entity residuals. Replaced by explicit middle-row mapping at y=-1.475 here.','acceptance':'Unvalidated single-parameter diagnostic; camera/depth coupling unresolved. Do not adopt as proven reconstruction.'}
json.dump(report,open(R/'qa/one_parameter_preflight.json','w'),indent=2);print(json.dumps(report,indent=2))
