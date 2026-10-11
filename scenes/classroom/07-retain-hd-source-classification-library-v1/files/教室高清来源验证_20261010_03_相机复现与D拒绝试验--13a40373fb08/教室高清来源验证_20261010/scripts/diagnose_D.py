import numpy as np,json,itertools
from scipy.spatial.transform import Rotation
from pathlib import Path
p=Path('classroom_hd_alignment_20261010');r=json.load(open(p/'qa/scene_inspection.json'));vis=json.load(open(p/'qa/D_desktop_visibility.json'));cams={c['name']:c for c in r['cameras']};objs={o['name']:o for o in r['objects']}
def proj(X,cam):
 c=cams['SOURCE_'+cam];q=(X-np.array(c['location']))@Rotation.from_euler('xyz',c['rotation']).as_matrix();f=c['lens']/36*1180;return np.stack([590+f*q[:,0]/-q[:,2],332-f*q[:,1]/-q[:,2]],axis=1)
records=[]
for n,count in vis['pixel_counts'].items():
 o=objs[n];X=np.array(list(itertools.product(*zip(o['min'],o['max']))));uv=proj(X,'D');record={'name':n,'visible_pixels':count,'projected_bbox_min':uv.min(0).tolist(),'projected_bbox_max':uv.max(0).tolist(),'entire_bbox_outside_left':bool(uv[:,0].max()<0)};records.append(record)
sweeps=[]
for n in ['R2C1 rounded oak desktop','R3C2 rounded oak desktop']:
 o=objs[n];X=np.array(list(itertools.product(*zip(o['min'],o['max']))));C=proj(X,'C')
 for dy in [0,-.1,-.2,-.3,-.4,-.5,-.6,-.8,-1.0,-1.2]:
  new=X+[0,dy,0];D=proj(new,'D');cc=proj(new,'C');sweeps.append({'name':n,'shared_delta_y':dy,'D_x_min':float(D[:,0].min()),'D_x_max':float(D[:,0].max()),'D_y_min':float(D[:,1].min()),'D_y_max':float(D[:,1].max()),'C_corner_rms_change_px':float(np.sqrt(np.mean(np.linalg.norm(cc-C,axis=1)**2)))})
out={'source_count_lower_bound':14,'model_total':20,'model_visible':12,'zero_visible_objects':[x for x in records if not x['visible_pixels']],'all_zero_visible_wholly_left_of_frame':all(x['entire_bbox_outside_left'] for x in records if not x['visible_pixels']),'all_desktops':records,'bounded_forward_shift_sweep':sweeps,'interpretation':'The 8 invisible desktops are outside D frustum, not merely hidden behind chairs. Bringing two nearest excluded units into frame requires shared forward shifts. This diagnostic alone does not establish source identity or a successful layout repair; evaluate C drift and source wood-segment match before accepting.'}
(p/'qa/D_root_cause_and_shift_sweep.json').write_text(json.dumps(out,indent=2));print(json.dumps({'all_off_left':out['all_zero_visible_wholly_left_of_frame'],'sweeps':sweeps},indent=2))
