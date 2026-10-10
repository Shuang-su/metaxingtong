import json,numpy as np,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[1];V=json.loads((R/'analysis/joint_constraints.json').read_text());res=json.loads((R/'analysis/joint_space_results.json').read_text())
def project(cam,p):
 c=(np.array(p)-cam[:3])@Rotation.from_euler('xyz',cam[3:6]).as_matrix();f=cam[6]*1180/36;return np.column_stack([590+f*c[:,0]/-c[:,2],332-f*c[:,1]/-c[:,2]])
def world(p,n,g):
 p=np.array(p,float).copy();p[:,1]=5.44+g[0]*(p[:,1]-5.44)
 if n.startswith('ceiling') or n.startswith('legacy_hypothesis_round'):p[:,2]+=g[1]
 if n.startswith('ceiling'):p[:,0]*=g[2]
 return p
summary={};mapping=[]
for k in ['A','B','D','F','H','I']:
 old=json.loads((R.parent/'analysis'/f'{k}_camera_fit.json').read_text())['params'];old=np.array(old[:3]+[old[3],0,old[4],old[5]])
 panels=[]
 for mode,cam,g in [('R03',old,[1,0,1]),('CAMERA_ONLY_REJECTED',res['camera_only']['cameras'][k]['camera'],[1,0,1]),('JOINT_SPACE_REJECTED',res['shared_depth_roof']['cameras'][k]['camera'],res['shared_depth_roof']['shared'])]:
  im=Image.open(R.parents[1]/'train_hd_recapture_20261010'/V[k]['source_file']).crop(V[k]['crop']).convert('RGB');d=ImageDraw.Draw(im)
  for p in V[k]['points']:
   q=np.array(p['source']);pr=project(cam,world([p['world']],p['name'],g))[0];d.ellipse((q[0]-3,q[1]-3,q[0]+3,q[1]+3),outline='cyan',width=2)
   if np.all(np.abs(pr)<5000):d.line([tuple(q),tuple(pr)],fill='yellow',width=1);d.ellipse((pr[0]-3,pr[1]-3,pr[0]+3,pr[1]+3),outline='red',width=2)
  for l in V[k]['lines']:
   q=l['source'];d.line([tuple(t) for t in q],fill='cyan',width=2);a,b=project(cam,world(l['world'],l['name'],g));dd=b-a
   # Draw infinite projected structural line clipped by Pillow, instead of inventing a longitudinal endpoint.
   if abs(dd[0])>1e-8:
    aa=a+dd*(0-a[0])/dd[0];bb=a+dd*(1180-a[0])/dd[0]
    if np.all(np.abs([aa,bb])<1e5):d.line([tuple(aa),tuple(bb)],fill='red',width=2)
  band=Image.new('RGB',(1180,692),'#202020');band.paste(im,(0,28));ImageDraw.Draw(band).text((8,7),f'{k} {mode} | observed cyan / projected red / displacement yellow',fill='white');panels.append(band)
 out=Image.new('RGB',(1180,692*3));[out.paste(x,(0,j*692)) for j,x in enumerate(panels)];out.save(R/'review'/f'{k}_projection_diagnostic.jpg',quality=90)
 summary[k]={}
 for mode,m in res.items():
  cr=m['cameras'][k];groups={}
  for d in cr['check_details']:
   n=d['name'];group='rack_line' if n.startswith('rack') else ('seat_bay_provisional' if n.endswith(('nearR','midR')) else ('lamp_index_provisional' if 'round' in n else 'endwall_rigid'))
   groups.setdefault(group,[]).extend([abs(x) for x in d.get('errors_px',[d.get('error_px',0)])])
  summary[k][mode]={g:{'n':len(a),'mean_abs_px':float(np.mean(a)),'max_abs_px':float(np.max(a))} for g,a in groups.items()}
 # Explicitly test if annotated rack line was the wall-side rail rather than aisle-side rail.
 for l in V[k]['lines']:
  if not l['name'].startswith('rack'):continue
  record={'view':k,'line':l['name'],'r03_alternatives':{}}
  for x in [.88,1.43]:
   p=np.array(l['world'],float);p[:,0]=np.sign(p[:,0])*x;a,b=project(old,p);dd=b-a;n=np.array([-dd[1],dd[0]])/np.linalg.norm(dd);e=(np.array(l['source'])-a)@n;record['r03_alternatives'][str(x)]=e.tolist()
  mapping.append(record)
(R/'analysis/holdout_by_feature_family.json').write_text(json.dumps(summary,indent=2));(R/'analysis/rack_identity_alternatives.json').write_text(json.dumps(mapping,indent=2))
print(json.dumps(summary,indent=2))
