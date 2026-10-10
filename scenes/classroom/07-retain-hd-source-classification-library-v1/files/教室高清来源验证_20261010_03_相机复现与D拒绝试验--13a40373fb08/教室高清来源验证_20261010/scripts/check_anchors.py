import json,numpy as np
from scipy.spatial.transform import Rotation
from pathlib import Path
p=Path('classroom_hd_alignment_20261010');r=json.load(open(p/'qa/scene_inspection.json'))
world={'board_TL':[1.9,.084,2.060728],'board_TR':[-1.9,.084,2.060728],'board_BL':[1.9,.084,.593477],'board_BR':[-1.9,.084,.593477],'book_TL':[3.049261,.458706,1.783019],'book_TR':[2.287747,.458706,1.783019],'clock':[-1.82,.1065,2.340059],'teacher_L':[-.363664,2.074549,.846306],'teacher_R':[-1.279898,2.074549,.846306]}
obs={'A':{'board_TR':[880,357],'board_BR':[893,583],'book_TL':[96,366],'book_TR':[235,369],'clock':[864,309]},'C':{'board_TL':[447,223],'board_TR':[739,222],'board_BL':[449,341],'board_BR':[738,340],'book_TL':[344,243],'book_TR':[406,243],'clock':[732,196],'teacher_L':[630,324],'teacher_R':[722,324]},'D':{'board_TL':[584,52],'board_BL':[584,312],'book_TL':[370,104],'book_TR':[488,103],'teacher_L':[894,284],'teacher_R':[1117,284]}}
for i,(y,x) in enumerate([(7.803765,399),(8.500465,243),(9.197165,110)]):
 for j,(z,py) in enumerate([(1.827585,[112,134,150][i]),(1.011108,[373,369,362][i])]):
  key=f'window_{i}_{j}';world[key]=[4.050608,y,z];obs.setdefault('B',{})[key]=[x,py]
out=[]
for name,points in obs.items():
 c=next(c for c in r['cameras'] if c['name']=='SOURCE_'+name);R=Rotation.from_euler('xyz',c['rotation']).as_matrix();records=[]
 for key,uv in points.items():
  q=(np.array(world[key])-c['location'])@R;f=c['lens']/36*1180;proj=np.array([590+f*q[0]/-q[2],332-f*q[1]/-q[2]]);records.append({'label':key,'world':world[key],'source_px':uv,'projected_px':proj.tolist(),'error_px':float(np.linalg.norm(proj-uv))})
 errs=np.array([x['error_px'] for x in records]);out.append({'camera':c,'rms_px':float(np.sqrt(np.mean(errs**2))),'median_px':float(np.median(errs)),'max_px':float(errs.max()),'points':records,'scope':'Manual architecture/teacher-desk spot checks at native 1180x664; not image-wide error, not independent of historic model fitting. Picking uncertainty ~2-4px. B repetitive-window identity inherited, not independently established.'})
(p/'qa/new_source_anchor_errors.json').write_text(json.dumps(out,indent=2));print([(x['camera']['name'],x['rms_px'],x['max_px']) for x in out])
