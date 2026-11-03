from pathlib import Path
import json,numpy as np,hashlib
from scipy.spatial.transform import Rotation
P=Path('/workspace/scratch/fa58bfcf0425/cityroom-refinement-20261103');O=Path(__file__).parent
fs=[P/'qa/R09-camera-fit.json',P/'qa/R09b-camera-fit.json'];rs=[json.load(open(f))['results'][2] for f in fs];v2=json.load(open(P/'sources/landmarks-v2/landmarks-v2-review-F09.json'));t=np.linspace(0,2*np.pi,8193)[:-1];xyz=np.stack([.301*np.cos(t),1.25+.301*np.sin(t),t*0],1)
rows=[]
for label,r in zip(['R09','R09b'],rs):
 p=np.array(r['fitted']);q=(xyz-p[:3])@Rotation.from_rotvec(p[3:]).as_matrix();uv=np.stack([r['width']/2+r['fixed_focal_px']*q[:,0]/-q[:,2],r['height']/2-r['fixed_focal_px']*q[:,1]/-q[:,2]],1)
 a=uv;b=np.roll(uv,-1,axis=0);ab=b-a;detail=[]
 for x in v2['additional_front_contour_samples']:
  pt=np.array(x['xy_native']);k=np.clip(np.sum((pt-a)*ab,1)/np.sum(ab*ab,1),0,1);near=a+ab*k[:,None];dist=np.linalg.norm(near-pt,axis=1);front=np.sum((xyz[:,:2]-[0,1.25])*(p[:2]-xyz[:,:2]),axis=1)>0;fi=int(np.argmin(np.where(front,dist,np.inf)));i=dist.argmin();detail.append({'id':x['id'],'error_px':float(dist[i]),'front_arc_only_error_px':float(dist[fi]),'nearest_xy':near[i].tolist(),'nearest_base_ring_world_xy':xyz[i,:2].tolist(),'radial_facing_camera_dot':float(np.dot(xyz[i,:2]-[0,1.25],p[:2]-xyz[i,:2]))})
 rows.append({'solution':label,'unfitted_new_front_points':detail,'mean':float(np.mean([d['error_px'] for d in detail])),'max':max(d['error_px'] for d in detail)})
ids={d['id'] for d in rs[1]['training']};old={d['id']:d for d in rs[0]['training']};same=[{'id':x['id'],'r09_px':old[x['id']]['after_error_px'],'r09b_px':x['after_error_px']} for x in rs[1]['training']]
out={'file_hashes':{str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in fs},'same_8_valid_constraints':same,'new_seen_diagnostics':rows,'limitations':'Not blind. Distance to assumed base circle; source boundary may be different profile surface and shadow/contact. New points were not used in either fit.'};(O/'R09-R09b-F-comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(rows,indent=2))
