import json,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[1];j=json.loads((P/'blinds_projection_source.json').read_text());f=json.loads((P/'bank1_fit.json').read_text());m=np.array(j['cameras']['665']['projection']);before=[];after=[]
for i,n in enumerate(f['target_group']):
 v=np.array(j['objects'][n]['world_vertices'])
 def maxy(w):
  q=np.c_[w,np.ones(len(w))]@m.T;assert np.all(q[:,3]>0);return float(((1-q[:,1]/q[:,3])*540).max())
 before.append(maxy(v))
 if i<f['selected_H_G_only']['removed_bottom_count']:continue
 lo=v[:,0].min();hi=v[:,0].max();v[:,0]=lo+(v[:,0]-lo)*(hi+f['selected_H_G_only']['right_trim_scene_units']-lo)/(hi-lo);after.append(maxy(v))
out={'view':'665','screen_y_domain':[0,1080],'before_group_max_y':max(before),'after_group_max_y':max(after),'all_target_geometry_above_frame_before_and_after':max(before)<0 and max(after)<0,'new_direct_geometry_occlusion':False,'limitation':'Projection visibility check, not a new photometric/shadow render or calibration validation'}
assert out['all_target_geometry_above_frame_before_and_after'];(P/'665_visibility_check.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
