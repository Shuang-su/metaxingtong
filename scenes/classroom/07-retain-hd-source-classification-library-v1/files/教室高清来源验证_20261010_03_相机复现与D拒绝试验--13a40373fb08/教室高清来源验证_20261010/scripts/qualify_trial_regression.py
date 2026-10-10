import numpy as np,json,itertools
from scipy.spatial.transform import Rotation
from pathlib import Path
p=Path('classroom_hd_alignment_20261010');r=json.load(open(p/'qa/scene_inspection.json'));cams={c['name']:c for c in r['cameras']};motion=json.load(open(p/'qa/motion_camera_fit.json'));cams['HD_classroom_motion_4282']={'location':motion['camera_location'],'rotation':motion['camera_rotation_xyz'],'lens':motion['lens_mm']};objs={o['name']:o for o in r['objects']};file=p/'rejected_shift/qa/change_manifest.json';a=json.load(open(file))
for t in a['projection_regression_all_source_cameras']:
 o=objs[t['desk_group']+' rounded oak desktop'];X=np.array(list(itertools.product(*zip(o['min'],o['max']))));cam=cams[t['camera']];R=Rotation.from_euler('xyz',cam['rotation']).as_matrix();states=[]
 for dy in [0,a['shared_group_y_shifts'][t['desk_group']]]:
  q=(X+[0,dy,0]-np.array(cam['location']))@R;f=cam['lens']/36*1180;uv=np.stack([590+f*q[:,0]/-q[:,2],332-f*q[:,1]/-q[:,2]],1);front=bool(np.all(q[:,2]<-.001));inside=front and bool(uv[:,0].max()>0 and uv[:,0].min()<1180 and uv[:,1].max()>0 and uv[:,1].min()<664);states.append({'all_corners_in_front':front,'bbox_intersects_view':inside})
 t['before_visibility']=states[0];t['after_visibility']=states[1];raw=t.pop('corner_rms_shift_px');t['raw_unclipped_projection_change_px']=raw;t['in_frame_projection_change_px']=raw if states[0]['bbox_intersects_view'] and states[1]['bbox_intersects_view'] else None
 t['interpretation']='Geometric projection change, not image residual. Offscreen/behind-camera/near-plane values must not be presented as visual errors. No full render regression claimed except C and D.'
a['actual_D_count_trial_result']={'visible_desktops':14,'new_fragments_pixels':{'R2C1':110,'R3C2':477},'decision':'Rejected. The two additions are only left-edge fragments, no reliable source identity; C furniture geometry visibly worsens.'};file.write_text(json.dumps(a,indent=2))
