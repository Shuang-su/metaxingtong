import pathlib,json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
P=pathlib.Path(__file__).resolve().parents[1];src=json.load(open(P/'source-analysis/landmarks-v1.json'));seeds=json.load(open(P/'qa/R01-camera-seeds.json'))
# Assumed correspondences to visible line supports, not observed world endpoints.
def line(a,b):return np.array([a,b],float)
floors={'L':line([-2.45,-6,.055],[-2.45,6,.055]),'R':line([2.45,-6,.055],[2.45,6,.055]),'BACK':line([-2.5,5.95,.055],[2.5,5.95,.055])}
sets={'008':('SOURCE_08_wide',{'008-S8':floors['L'],'008-S9':floors['R'],'008-S10':floors['BACK'],'008-S11':floors['BACK']}),'023':('SOURCE_23_oblique',{'023-S1':floors['R'],'023-S2':floors['L'],'023-S4':floors['BACK'],'023-S3':line([2.5,6,0],[2.5,6,3.8])}),'026':('SOURCE_26_side',{'026-S1':line([2.4575,2,0],[2.4575,2,3.8]),'026-S2':line([2.4575,0,0],[2.4575,0,3.8]),'026-S3':line([2.4575,0,0],[2.4575,0,3.8]),'026-S4':line([2.4575,-2,0],[2.4575,-2,3.8]),'026-S5':line([2.45,-6,.11],[2.45,6,.11]),'026-S6':line([2.45,-6,.11],[2.45,6,.11]),'026-S7':line([2.45,-6,0],[2.45,6,0]),'026-S8':line([2.45,-6,0],[2.45,6,0])})}
out={}
for frame,(name,mapping) in sets.items():
 seed=seeds[name];M=np.array(seed['matrix_world']);rv=Rotation.from_matrix(M[:3,:3]).as_rotvec();x0=np.r_[rv,M[:3,3]];f=seed['lens']/36*1192;obs={l['id']:np.array(l['endpoints'],float) for l in src['frames'][frame]['line_segments']}
 def projection_lines(x):
  R=Rotation.from_rotvec(x[:3]).as_matrix();C=x[3:];ret={}
  for key,w in mapping.items():
   q=(w-C)@R;z=-q[:,2];h=np.c_[596*z+f*q[:,0],335.5*z-f*q[:,1],z];l=np.cross(h[0],h[1]);l/=max(np.linalg.norm(l[:2]),1e-12);ret[key]=l
  return ret
 def residuals(x):return np.concatenate([np.c_[obs[k],np.ones(2)]@l for k,l in projection_lines(x).items()])
 lo=np.r_[rv-.6,[-2.3,-5.8,.25]];hi=np.r_[rv+.6,[2.3,5.8,3.55]];fit=least_squares(residuals,x0,bounds=(lo,hi),max_nfev=2500,xtol=1e-12,ftol=1e-12,gtol=1e-12);mat=np.eye(4);mat[:3,:3]=Rotation.from_rotvec(fit.x[:3]).as_matrix();mat[:3,3]=fit.x[3:];sv=np.linalg.svd(fit.jac,compute_uv=False)
 out[name]={'lens':seed['lens'],'matrix_world':mat.tolist(),'world_line_assumptions':{k:v.tolist() for k,v in mapping.items()},'observed_segments':{k:obs[k].tolist() for k in mapping},'baseline_signed_endpoint_errors_px':residuals(x0).tolist(),'fit_signed_endpoint_errors_px':residuals(fit.x).tolist(),'mean_abs':float(np.mean(abs(residuals(fit.x)))),'max_abs':float(max(abs(residuals(fit.x)))),'jacobian_singular_values_unscaled':sv.tolist(),'limitations':'Manual visible segment endpoints constrain infinite support lines, not exact world endpoints. Geometry/instance/band-center assumptions unverified. Fixed original focal length, bounded pose trial. Jacobian uses unscaled radians and arbitrary working units, not confidence/metric precision. All source acceptance FAILED; floor reflections and unknown scene state remain.'}
 print(name,'mean/max',out[name]['mean_abs'],out[name]['max_abs'],'C',fit.x[3:],'sv',sv)
(P/'qa/R02-line-fit.json').write_text(json.dumps(out,indent=2))
