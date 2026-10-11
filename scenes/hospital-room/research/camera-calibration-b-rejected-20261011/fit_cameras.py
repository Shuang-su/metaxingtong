import numpy as np,json
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from pathlib import Path
r=Path(__file__).parent;j=json.loads((r/'scene_anchor_inventory.json').read_text());objs={o['name']:o for o in j['objects']}
TV='TV • rectangular black frame'; M='Window • calibrated vertical mullion'
def pt(obj,label):return objs[obj]['points'][label]
def top(obj):
 p=np.array(pt(obj,'origin'));p[2]=max(v[2] for v in objs[obj]['points'].values());return p.tolist()
def line(obj):
 p=np.array(pt(obj,'origin'));q=p.copy();p[2]=.4;q[2]=2.5;return [p.tolist(),q.tolist()]
D={k:[] for k in 'FGH'}
def P(k,id,obj,xyz,uv,sigma,split,why):D[k].append(dict(id=id,object_id=obj,kind='point',xyz=xyz,observed=uv,sigma_px=sigma,split=split,identification=why))
def L(k,id,obj,uv,sigma,split):D[k].append(dict(id=id,object_id=obj,kind='line',xyz=line(obj),observed=uv,sigma_px=sigma,split=split,identification='Same numbered mullion, centreline of visible narrow dark strip; sampled image endpoints constrain a line, NOT arbitrary 3D point correspondences. Model cross-section differs; sigma includes edge-to-axis uncertainty.'))
for id,b,uv,sp in [('tv_tl','bbox_2',[1096,582],'train'),('tv_tr','bbox_1',[1655,551],'train'),('tv_bl','bbox_3',[1108,886],'train'),('tv_br','bbox_0',[1683,877],'holdout')]:P('F',id,TV,pt(TV,b),uv,3,sp,'Outer black TV frame corner, unrounded bbox idealization; 3 px picking/bevel uncertainty.')
P('F','m3_top',M+'.003',top(M+'.003'),[590,277],12,'train','Inferred top centre of the same mullion cross-section at ceiling; not a visible exact vertex. 12 px cross-section ambiguity.')
P('F','m4_top',M+'.004',top(M+'.004'),[747,411],12,'holdout','Last window mullion top partially occluded by blind ends. 12 px identification uncertainty.')
L('F','m3_axis',M+'.003',[[586,430],[556,1070]],10,'train')
L('F','m4_axis',M+'.004',[[745,550],[735,1050]],10,'holdout')
P('G','tv_tl',TV,pt(TV,'bbox_2'),[1884,421],3,'train','Outer TV top-left corner; rest of TV is cropped or bed-occluded.')
P('G','m3_top',M+'.003',top(M+'.003'),[1312,179],12,'train','Top cross-section midpoint proxy, matched to mullion .003 via order between curtain and last window. 12 px ambiguity.')
P('G','m4_top',M+'.004',top(M+'.004'),[1481,286],12,'holdout','Last window mullion partly covered by blinds; 12 px identification ambiguity.')
L('G','m1_axis',M+'.001',[[408,10],[360,880]],10,'train')
L('G','m3_axis',M+'.003',[[1320,340],[1344,1015]],10,'train')
L('G','m2_axis',M+'.002',[[939,450],[940,930]],10,'holdout')
L('G','m4_axis',M+'.004',[[1487,425],[1513,970]],10,'holdout')
# A different point on an already fitted edge is NOT independent landmark evidence: retain solely as line-direction check.
D['G'].append(dict(id='tv_left_direction',object_id=TV,kind='line',xyz=[pt(TV,'bbox_2'),pt(TV,'bbox_3')],observed=[[1884,421],[1917,730]],sigma_px=4,split='direction_only',identification='Visible left TV edge. Bottom point is bed occlusion, NOT TV corner. This is not independent of fitted top-left corner.'))
L('H','m0_axis',M,[[82,150],[32,1050]],12,'holdout')
L('H','m1_axis',M+'.001',[[990,20],[992,790]],10,'holdout')
L('H','m2_axis',M+'.002',[[1530,100],[1546,850]],12,'holdout')
# Supplementary never-fitted diagnostics, added after first numerical fit: room-shell interior corner and forward rail upper edge (near depth).
for k,uv in [('F',[805,451]),('G',[1545,317])]:
 P(k,'shell_corner17','ROOM_SHELL__joined_solid__hidden_extents_inferred',[5.537500381469727,0.,2.714665412902832],uv,5,'holdout','Same visible window/TV-wall/ceiling three-surface junction; mesh vertex 17, interior corner, no inferred outer bbox corner.')
for k,uv in [('F',[[257,60],[670,1]]),('G',[[1016,47],[1136,1]])]:
 ob='Curtain rail • forward overhead beam'
 D[k].append(dict(id='rail_upper_edge',object_id=ob,kind='line',xyz=[pt(ob,'bbox_2'),pt(ob,'bbox_1')],observed=uv,sigma_px=10,split='holdout',identification='Upper edge of upper/left forward rail. Same beam ID by relative order; endpoints sample an edge, not exact 3D vertices. 10 px rail thickness/identity uncertainty. Entire rail object excluded from training.'))
(r/'observations.json').write_text(json.dumps({'resolution':[1920,1080],'annotation':'Manual visual picking at native source pixels; uncertainties are conservative assumptions, not empirically measured repeatability. No image registration. H has no well identified noncoplanar fixed point; kept unchanged.','observations':D},indent=2,ensure_ascii=False))
def init(k):
 c=j['cameras'][k];m=np.array(c['matrix_world']);R=m[:3,:3];R=R/np.linalg.norm(R,axis=0)
 return np.r_[Rotation.from_matrix(R).as_rotvec(),m[:3,3],np.log(c['lens']),0.,0.]
def proj(x,pts):
 R=Rotation.from_rotvec(x[:3]).as_matrix();v=(np.array(pts)-x[3:6])@R;f=np.exp(x[6])/36*1920
 return np.c_[960+x[7]+f*v[:,0]/(-v[:,2]),540+x[8]-f*v[:,1]/(-v[:,2])],-v[:,2]
def err(x,a):
 p=np.array(a['xyz']);p=p.reshape(-1,3);q,z=proj(x,p);uv=np.array(a['observed'])
 if a['kind']=='point':return (q[0]-uv)
 # Evaluate observed native pixel points against projected model line (no arbitrary point correspondence).
 v=q[1]-q[0];n=np.array([-v[1],v[0]])/np.linalg.norm(v);return (uv-q[0])@n
out={}
rng=np.random.default_rng(61011)
for k in 'FG':
 x0=init(k);obs=D[k];train=[a for a in obs if a['split']=='train'];out[k]={'original':x0.tolist(),'candidates':{}}
 for mode,n in [('pose6',6),('pose_focal7',7),('pose_focal_shift9',9)]:
  def unpack(y):x=x0.copy();x[:n]=y;return x
  def res(y,pert=None):
   x=unpack(y);e=np.concatenate([err(x,a)/a['sigma_px'] for a in (pert or train)])
   # Shift is physically meaningful lens shift, restricted by centre prior; not a screen warp.
   if n==9:e=np.r_[e,x[7:9]/16]
   return e
  lo=x0[:n]-np.r_[np.repeat(.45,3),np.repeat(1.5,3),.4,32,32][:n];hi=x0[:n]+np.r_[np.repeat(.45,3),np.repeat(1.5,3),.4,32,32][:n]
  fits=[]
  for i in range(8):
   seed=x0[:n] if i==0 else np.clip(x0[:n]+rng.normal(0,.05,n),lo+1e-6,hi-1e-6)
   sol=least_squares(res,seed,bounds=(lo,hi),max_nfev=3000,xtol=1e-11,ftol=1e-11,gtol=1e-11);fits.append(sol)
  sol=min(fits,key=lambda z:np.sum(z.fun*z.fun));x=unpack(sol.x)
  rawjac=least_squares(lambda y:np.concatenate([err(unpack(y),a)/a['sigma_px'] for a in train]),sol.x,max_nfev=1).jac
  ss=np.linalg.svd(rawjac,compute_uv=False)
  metrics=[]
  for a in obs:
   e0=err(x0,a);e=err(x,a);metrics.append({'id':a['id'],'kind':a['kind'],'split':a['split'],'original_errors_px':e0.tolist(),'candidate_errors_px':e.tolist(),'original_rms_px':float(np.sqrt(np.mean(e0**2))),'candidate_rms_px':float(np.sqrt(np.mean(e**2)))})
  noise=[]
  for it in range(30):
   pp=json.loads(json.dumps(train))
   for a in pp:a['observed']=(np.array(a['observed'])+rng.normal(0,a['sigma_px'],np.array(a['observed']).shape)).tolist()
   ssn=least_squares(lambda y:res(y,pp),sol.x,bounds=(lo,hi),max_nfev=1000);noise.append(unpack(ssn.x))
  noise=np.array(noise)
  out[k]['candidates'][mode]={'parameters':x.tolist(),'lens_mm':float(np.exp(x[6])),'principal_point_px':(x[7:9]+[960,540]).tolist(),'fit_cost':float(np.sum(sol.fun**2)),'data_jacobian_singular_values':ss.tolist(),'data_jacobian_rank':int(np.linalg.matrix_rank(rawjac)),'bound_hit':bool(np.any(np.abs(sol.x-lo)<1e-3)|np.any(np.abs(sol.x-hi)<1e-3)),'noise_30_parameter_std':noise.std(axis=0).tolist(),'noise_30_lens_range_mm':[float(np.exp(noise[:,6]).min()),float(np.exp(noise[:,6]).max())],'metrics':metrics}
  print(k,mode,'lens',round(np.exp(x[6]),2),'position',x[3:6].round(3),'rank',np.linalg.matrix_rank(rawjac),'cond',ss[0]/ss[-1],'hold',[(a['id'],round(a['original_rms_px'],1),round(a['candidate_rms_px'],1)) for a in metrics if a['split']!='train'])
out['H']={'original':init('H').tolist(),'decision':'UNCHANGED_UNIDENTIFIABLE: only three coplanar clipped vertical axes; no reliable unique 3D-to-2D point correspondences.'}
(r/'fit_results.json').write_text(json.dumps(out,indent=2))
