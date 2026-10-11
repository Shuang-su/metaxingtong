exec(open(__file__.replace('joint_space.py','fit_diagnostic.py')).read().split('out={}')[0])
# Independent annotation correction: D right ceiling seam follows inner ivory edge, not outer black light rail.
V['D']['lines'][1]['source']=[[881,1],[827,274]]
for k in ['A','B','D']:
 for p in V[k]['points']:
  if p['name'].startswith('legacy_hypothesis_round') and int(p['name'].split('round')[-1])%2==0:p['split']='fit';p['sigma_px']=4
(R/'analysis/joint_constraints.json').write_text(json.dumps(V,indent=2,ensure_ascii=False))
ks=['A','B','D','H','I','F']
# Fixed working-unit transverse dimensions serve as gauge; they are NOT measured source dimensions.
def transform(p,name,g):
 p=np.asarray(p,float).copy();p[...,1]=5.44+g[0]*(p[...,1]-5.44)
 if name.startswith('ceiling') or name.startswith('legacy_hypothesis_round'):p[...,2]+=g[1]
 if name.startswith('ceiling'):p[...,0]*=g[2]
 return p
def items(cam,k,g,split,weighted=False):
 rr=[];details=[]
 for p in V[k]['points']:
  if p['split']!=split:continue
  w=transform([p['world']],p['name'],g);pr=project(cam,w)[0];e=pr-p['source'];rr.extend(e/(p['sigma_px'] if weighted else 1));details.append({'name':p['name'],'error_px':float(np.linalg.norm(e)),'projected':pr.tolist(),'source':p['source']})
 for l in V[k]['lines']:
  if l['split']!=split:continue
  w=transform(l['world'],l['name'],g);a,b=project(cam,w);d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d);e=(np.array(l['source'])-a)@n;rr.extend(e/(l['sigma_px'] if weighted else 1));details.append({'name':l['name'],'errors_px':e.tolist()})
 return np.array(rr),details
initial=np.concatenate([oldcam(k) for k in ks]);lo=np.tile([-1.45,-8,.65,1.15,-.12,-.3,12],len(ks));hi=np.tile([1.45,4.5,2.2,2,.12,1.2,50],len(ks))
result={}
for label,g0,gl,gh in [('camera_only',[],[],[]),('shared_depth',[1],[.65],[1.5]),('shared_depth_roof',[1,0,1],[.65,-.12,.8],[1.5,.3,1.25])]:
 def getg(x):
  if not g0:return [1,0,1]
  if len(g0)==1:return [x[-1],0,1]
  return x[-3:]
 def res(x):
  g=getg(x);rr=[]
  for j,k in enumerate(ks):rr.extend(items(x[j*7:j*7+7],k,g,'fit',True)[0])
  return np.array(rr)
 init=np.r_[initial,g0];lower=np.r_[lo,gl];upper=np.r_[hi,gh];sol=least_squares(res,np.clip(init,lower+1e-4,upper-1e-4),bounds=(lower,upper),loss='soft_l1',f_scale=2,max_nfev=1800)
 g=np.array(getg(sol.x));rr={'shared':g.tolist(),'cameras':{},'active_bounds':np.where(np.minimum(abs(sol.x-lower),abs(sol.x-upper))<.001)[0].tolist(),'singular_values':np.linalg.svd(sol.jac,compute_uv=False).tolist()}
 for j,k in enumerate(ks):
  cam=sol.x[j*7:j*7+7];a,ad=items(cam,k,g,'fit');b,bd=items(cam,k,g,'check');ob,od=items(oldcam(k),k,[1,0,1],'check')
  rr['cameras'][k]={'camera':cam.tolist(),'fit_rms_components':float(np.sqrt(np.mean(a*a))),'check_rms_components':float(np.sqrt(np.mean(b*b))),'old_check_rms_components':float(np.sqrt(np.mean(ob*ob))),'fit_details':ad,'check_details':bd,'old_check_details':od}
  print(label,k,'focal',round(cam[-1],2),'check',round(np.sqrt(np.mean(ob*ob)),2),'->',round(np.sqrt(np.mean(b*b)),2),flush=True)
 result[label]=rr;print(label,'SHARED',g,'bounds',rr['active_bounds'],flush=True)
(R/'analysis/joint_space_results.json').write_text(json.dumps(result,indent=2))
