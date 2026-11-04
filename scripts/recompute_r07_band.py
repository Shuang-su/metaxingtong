import json,pathlib,numpy as np
from scipy.optimize import minimize_scalar
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'qa';D=json.load(open(P/'R07-input-trials/diagnosis.json'))
# CCW outer polygon identical to R06; even indexes are cardinal outer tips.
angles=np.arange(8)*np.pi/4;poly=np.c_[np.cos(angles),np.sin(angles)]*np.array([2.4,.68]*4)[:,None]
def inset(w):
 out=[]
 for i in range(8):
  a,b,c=poly[(i-1)%8],poly[i],poly[(i+1)%8];u=(b-a)/np.linalg.norm(b-a);v=(c-b)/np.linalg.norm(c-b);n=np.array([-u[1],u[0]]);m=np.array([-v[1],v[0]]);start=a+w*n;end=b+w*m;t=np.linalg.solve(np.column_stack([u,-v]),end-start)[0];out.append(start+t*u)
 return np.array(out)
refs={'SOURCE_13_high':{'S1':[542,386],'S2':[749,421],'S3':[692,555],'S4':[423,492]},'SOURCE_21_high':{'S1':[495,290],'S2':[686,290],'S4':[470,390]}};idx={'S1':2,'S2':0,'S3':6,'S4':4}
def errors(polyin):
 out={}
 for name,pts in refs.items():
  c=D['sources'][name]['fixed_camera'];M=np.array(c['matrix_world']);f=c['lens']/36*1192;points=[]
  for k,xy in pts.items():
   q=(np.r_[polyin[idx[k]],.495]-M[:3,3])@M[:3,:3];pp=[596+f*q[0]/-q[2],335.5-f*q[1]/-q[2]];points.append({'id':k,'observed':xy,'projected':pp,'error_px':float(np.linalg.norm(np.array(pp)-xy)),'depth':float(-q[2])})
  out[name]=points
 return out
baseline=np.c_[np.cos(angles),np.sin(angles)]*np.array([2.304,.584]*4)[:,None]
fit=minimize_scalar(lambda w:sum(p['error_px']**2 for rows in errors(inset(w)).values() for p in rows),bounds=(.005,.20),method='bounded');new=inset(fit.x)
out={'scope':'Unapplied band-only trial. R06 outer polygon and cameras fixed. Candidate parallel straight-edge inset is a hypothesis, not proven source equality. Seven newly inspected approximate inner tips are training, subjective bounds6px(source13)/8px(source21), not statistical uncertainty. Source21 S3 occluded and retained as null. Legacy mixed concave trials invalid for same-boundary fitting. All scene/source acceptance FAILED.','width':float(fit.x),'outer_xy':poly.tolist(),'inner_xy':new.tolist(),'baseline':errors(baseline),'trial':errors(new)}
(P/'R07-band-trial-recomputed.json').write_text(json.dumps(out,indent=2));print('width',fit.x);print('baseline',[round(p['error_px'],2) for v in out['baseline'].values() for p in v]);print('trial',[round(p['error_px'],2) for v in out['trial'].values() for p in v]);print('inner',new)
