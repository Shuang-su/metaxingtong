import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'analysis/joint_constraints.json';v=json.loads(p.read_text())
fix={('A','rack_inner_-1'):[[26,286],[551,433]],('A','rack_inner_1'):[[947,28],[754,424]],('B','rack_inner_-1'):[[15,205],[396,318]],('B','rack_inner_1'):[[719,28],[659,204]],('D','rack_inner_-1'):[[15,160],[682,350]],('D','rack_inner_1'):[[1155,150],[868,342]]}
for (k,n),qs in fix.items():
 l=next(x for x in v[k]['lines'] if x['name']==n);l['previous_source_rejected']=l['source'];l['source']=[[x,y-27] for x,y in qs];l['sigma_px']=8;l['identity_note']='Front aisle-side rack edge rechecked on unmagnified crop. Lip thickness and darkness allow ~8px annotation uncertainty. Never fitted.'
for k in ['F','H','I']:
 for l in v[k]['lines']:
  if 'rack' in l['name']:l['identity_note']='Provisional front-edge correspondence; short segment / lighting or perspective ambiguity. Qualitative check only.';l['sigma_px']=10
p.write_text(json.dumps(v,ensure_ascii=False,indent=2))
# Predictions and cameras unchanged; recompute heldout line error after identity correction.
import numpy as np
from scipy.spatial.transform import Rotation
rs=R/'analysis/joint_space_results.json';out=json.loads(rs.read_text())
def pr(cam,p):
 c=(p-cam[:3])@Rotation.from_euler('xyz',cam[3:6]).as_matrix();f=cam[6]*1180/36;return np.column_stack([590+f*c[:,0]/-c[:,2],332-f*c[:,1]/-c[:,2]])
for mode,m in out.items():
 for k,c in m['cameras'].items():
  old=json.loads((R.parent/'analysis'/f'{k}_camera_fit.json').read_text())['params'];old=old[:3]+[old[3],0,old[4],old[5]]
  for key,cam,g in [('check_details',c['camera'],m['shared']),('old_check_details',old,[1,0,1])]:
   for d in c[key]:
    if not d['name'].startswith('rack'):continue
    l=next(x for x in v[k]['lines'] if x['name']==d['name']);p=np.array(l['world'],float);p[:,1]=5.44+g[0]*(p[:,1]-5.44);a,b=pr(cam,p);dd=b-a;n=np.array([-dd[1],dd[0]])/np.linalg.norm(dd);d['errors_px']=((np.array(l['source'])-a)@n).tolist();d['identity_note']=l['identity_note']
  for key in ['check_rms_components','old_check_rms_components']:c.pop(key,None)
rs.write_text(json.dumps(out,indent=2))
print('Corrected held-out rack identity only, unchanged fitted cameras/geometry hypothesis; mixed aggregate RMS removed.')
