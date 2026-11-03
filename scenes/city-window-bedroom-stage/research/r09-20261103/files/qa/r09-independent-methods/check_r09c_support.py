import json,numpy as np,hashlib
from pathlib import Path
from scipy.spatial.transform import Rotation
P=Path('/workspace/scratch/fa58bfcf0425/cityroom-refinement-20261103');O=Path(__file__).parent
B=json.load(open(P/'qa/R09b-camera-fit.json'))['results'];C=json.load(open(P/'qa/R09c-camera-fit.json'))['results'];rows=[]
def proj(r,xyz):
 p=np.array(r['fitted']);v=(xyz-p[:3])@Rotation.from_rotvec(p[3:]).as_matrix();return np.column_stack([r['width']/2+r['fixed_focal_px']*v[:,0]/-v[:,2],r['height']/2-r['fixed_focal_px']*v[:,1]/-v[:,2]])
def error(r,e):
 p=np.array(r['fitted']);pt=np.array(e['xy'])
 if e['kind']=='line':
  a,b=proj(r,np.array([[e['x_world'],4.98,.18],[e['x_world'],4.98,6.438]]));v=b-a;return abs(np.cross(v,pt-a)/np.linalg.norm(v))
 k=e['curve'];radius,z={'seat':(.315,.903),'base':(.301,0)}[k];n=e['original_names'][0];half= k=='base' or n in ['seat_front','seat_rear'];az=np.arctan2(p[1]-1.25,p[0])+(np.pi if n=='seat_rear' else 0)
 t=np.linspace(az-np.pi/2,az+np.pi/2,4097) if half else np.linspace(0,2*np.pi,8193);xyz=np.column_stack([radius*np.cos(t),1.25+radius*np.sin(t),np.full(len(t),z)]);uv=proj(r,xyz);a=uv[:-1];v=uv[1:]-a;u=np.clip(np.sum((pt-a)*v,axis=1)/np.sum(v*v,axis=1),0,1);return float(np.linalg.norm(a+v*u[:,None]-pt,axis=1).min())
for b,c in zip(B,C):
 t=np.arange(2048)*2*np.pi/2048;xyz=np.concatenate([np.column_stack([r*np.cos(t),1.25+r*np.sin(t),np.full(len(t),z)]) for r,z in [(.315,.903),(.301,0),(.098,.455)] ] +[np.array([[x,4.98,z] for x in [1.345,1.4,1.455] for z in [.18,6.438]])]);diff=np.linalg.norm(proj(b,xyz)-proj(c,xyz),axis=1);errs=[{'id':e['id'],'exact_R09b_visible_half_px':float(error(b,e)),'R09c_reported_px':e['after_error_px']} for e in c['training']];rows.append({'camera':b['camera'],'max_sampled_projection_difference_px':float(diff.max()),'pose_position_distance':float(np.linalg.norm(np.array(b['fitted'][:3])-c['fitted'][:3])),'exact_R09b_visible_half_mean_px':float(np.mean([x['exact_R09b_visible_half_px'] for x in errs])),'exact_R09b_visible_half_max_px':max(x['exact_R09b_visible_half_px'] for x in errs),'constraints':errs})
out={'results':rows,'interpretation':'Supports exact R09b as essentially the same conditional half-ring solution; not independent calibration, not full occlusion. Samples are dense arcs not whole mesh.','input_sha256':{n:hashlib.sha256((P/'qa'/n).read_bytes()).hexdigest() for n in ['R09b-camera-fit.json','R09c-camera-fit.json']}};(O/'R09c-support-independent.json').write_text(json.dumps(out,indent=2));print(json.dumps(rows,indent=2))
