"""HISTORICAL REJECTED J1 SCREENING. Physical blind/fold overlap invalidates this family result; H validation method was subsequently corrected. No source pixels transformed."""
import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
R=Path(__file__).parent; D=R/'recovery'; J=json.load(open(D/'frozen_d_world_geometry.json'));O=J['objects'];C=json.load(open(D/'camera_candidates.json'));ann=json.load(open(D/'annotations_native_1920x1080.json'));FP=json.load(open(D/'fit_problem.json'))
BED='Bed • observed endboard, consistent width';MAT='Bed • mattress and sheet'; SOFAL='Sofa • reclined back cushion 1';SOFAR='Sofa • reclined back cushion 2'
V={n:np.array(o['vertices']) for n,o in O.items()}; bm=V[MAT].min(0);bx=V[MAT].max(0);bc=(bm+bx)/2
A=C['observations']['A'];A.update({'m2_axis':[[75,500],[49,700],[23,900]],'pillar_grey_axis':[[201,400],[162,800]],'grey_right_axis':[[349,500],[332,700],[315,900],[303,1050]],'rail2_left':[370,124], 'rail2_upper':[[370,121],[1150,28]]})
G={a['id']:a['observed'] for a in FP['architectural_observations']['G']};G['shell_corner']=G['shell_corner17'];G['m2_axis']=[[936,500],[936,900]];G.update({'rail_left':[1017,51],'rail2_left':[1140,55], 'rail_upper':[[1015,46],[1139,0]],'rail2_upper':[[1137,49],[1290,0]],'pillar_grey_axis':[[1028,200],[1028,800]],'grey_right_axis':[[1151,100],[1162,500],[1171,900],[1174,1050]]})
for f in ann['features']:
 if f['id']=='G_bed_upper_visible':G['bed_train']=f['source_xy']
obs={'A':A,'G':G}
# G source rigid TV anchors and sofa valid back silhouette prevent room-only overfit.
P={k:np.array(v) for k,v in C['point_geometry'].items()}

def normcam(c):
 m=np.array(c['matrix_world']);r=m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0);return np.r_[Rotation.from_matrix(r).as_rotvec(),m[:3,3],np.log(c['lens_mm'])]
baseA=normcam(C['cameras']['A']);baseG=normcam(J['cameras']['MATCH_G_Sofa_And_Bed'])
# 10 shared geometry parameters. Bed has rigid x/y move and width only; length remains unchanged.
gnames=['window_y','m3_x','pillar_width','pillar_projection','rail_depth_separation','rail_height','rail_pillar_fraction','bed_dx','bed_dy','bed_width_scale']
g0=np.array([0,3.576422,.30,.12,.38,2.69,.5,-.75,0,.78]);gl=np.array([-.4,2.4,.16,.025,.18,2.48,.0,-1.25,-.4,.55]);gh=np.array([.4,4.1,.55,.28,.8,2.71,1.,-.2,.4,1.0])
# camera pose parameters rotvec 3, eye longitudinal fraction .08..30, lateral fraction .2..8, head support height above mattress .15..55, focal.
# This anatomical envelope is a declared hypothesis; no exact pillow position is measured.
cam0=np.r_[baseA[:3],.13,.36,.43,np.log(33),baseG[:3],.13,.36,.43,np.log(33)]
cl=np.r_[baseA[:3]-.25,.06,.12,.15,np.log(25),baseG[:3]-.25,.06,.12,.15,np.log(25)]
ch=np.r_[baseA[:3]+.25,.32,.88,.60,np.log(45),baseG[:3]+.25,.32,.88,.60,np.log(45)]
q0=np.r_[g0,cam0];lo=np.r_[gl,cl];hi=np.r_[gh,ch]

def geometry(q):return dict(zip(gnames,q[:10]))
def bed_transform(v,g):
 v=v.copy();v[:,0]+=g['bed_dx'];v[:,1]=bc[1]+(v[:,1]-bc[1])*g['bed_width_scale']+g['bed_dy'];return v

def camera(q,k):
 g=geometry(q);i=10+(0 if k=='A' else 7);v=q[i:i+7];pos=np.array([bm[0]+g['bed_dx']+(bx[0]-bm[0])*v[3],bc[1]+g['bed_dy']+(v[4]-.5)*(bx[1]-bm[1])*g['bed_width_scale'],bx[2]+v[5]])
 return np.r_[v[:3],pos,v[6]]
def project(cam,p):
 qq=(np.asarray(p)-cam[3:6])@Rotation.from_rotvec(cam[:3]).as_matrix();f=np.exp(cam[6])/36*1920
 return np.c_[960-f*qq[:,0]/qq[:,2],540+f*qq[:,1]/qq[:,2]]
def line(cam,xyz,uv):
 p=project(cam,xyz);d=p[1]-p[0];normal=np.array([-d[1],d[0]])/np.linalg.norm(d);return (np.array(uv)-p[0])@normal

def contour(cam,verts,uv):
 p=project(cam,verts);poly=p[ConvexHull(p).vertices];a=poly;b=np.roll(poly,-1,axis=0);v=b-a;u=np.array(uv);t=np.clip(((u[:,None]-a)*v).sum(2)/(v*v).sum(1),0,1);return np.sqrt((((u[:,None]-(a+t[:,:,None]*v))**2).sum(2)).min(1))
def xline(x,y):return [[x,y,.35],[x,y,2.5]]
def terms(q,k):
 g=geometry(q);c=camera(q,k);a=obs[k];wy=g['window_y'];h=2.714665413;pj=1.521875;pr=pj+g['pillar_width'];front=wy-g['pillar_projection'];rx=pj+g['pillar_width']*g['rail_pillar_fraction'];rz=g['rail_height'];sep=g['rail_depth_separation'];e={}
 for n in ['tv_tl','tv_tr','tv_br'] if k=='A' else ['tv_tl']:e[n]=(project(c,[P[n]])[0]-a[n],4,'TV')
 if k=='G':e['tv_left_direction']=(line(c,[P['tv_tl'],P['tv_bl']],a['tv_left_direction']),5,'TV')
 e['m3_top']=(project(c,[[g['m3_x'],wy,h]])[0]-a['m3_top'],12,'window')
 e['shell_corner']=(project(c,[[5.5375,wy,h]])[0]-a['shell_corner'],7,'corner')
 for n,x in [('m1_axis',0),('m2_axis',1.5),('m3_axis',g['m3_x'])]:
  if n in a:e[n]=(line(c,xline(x,wy+.0027),a[n]),8,'window')
 # Beige-to-grey transition is soft shading/occlusion, not a verified corner; excluded.
 # The folds are conditional curtain; align far silhouette, not all fold shading.
 e['grey_right_axis']=(line(c,xline(pr+.59,front-.02),a['grey_right_axis']),15,'drape')
 e['rail_left']=(project(c,[[rx-.015,front,rz+.016875]])[0]-a['rail_left'],9,'rail')
 # rail2 visible start is a curtain-occlusion boundary, not a known endpoint; excluded from point fit.
 e['rail_upper']=(line(c,[[rx-.015,front,rz+.016875],[rx-.015,-3.3828,rz+.016875]],a['rail_upper']),6,'rail')
 e['rail2_upper']=(line(c,[[rx+sep-.015,front,rz+.016875],[rx+sep-.015,-3.3828,rz+.016875]],a['rail2_upper']),6,'rail')
 e['bed_upper']=(contour(c,bed_transform(V[BED],g),a['bed_train']),8,'bed')
 if k=='G':
  for n,ob,uv in [('sofa_back_left',SOFAL,[[227,894],[309,885],[422,879],[528,875],[588,877]]),('sofa_back_right',SOFAR,[[802,868],[839,864],[868,866],[879,870]])]:e[n]=(contour(c,V[ob],uv),12,'sofa')
 return e

def residual(q):
 res=[]
 for k in obs:
  tt=terms(q,k);counts={g:sum(1 for _,_,z in tt.values() if z==g) for _,_,g in tt.values()}
  for e,s,g in tt.values():res.extend(e/s/np.sqrt(len(e)*counts[g]))
 ca=camera(q,'A');cg=camera(q,'G')
 res.extend((ca[3:6]-cg[3:6])/[.25,.3,.3]*.25)
 # prevent poorly observed geometry and focal freedom from serving as arbitrary point cheats
 res.extend((q[:10]-g0)/(gh-gl)*.22)
 res.extend([(ca[6]-cg[6])/.12*.25])
 return np.array(res)

if __name__=='__main__':
 runs=[]
 for f in [28,34,40]:
  st=q0.copy();st[16]=st[23]=np.log(f)
  sol=least_squares(residual,st,bounds=(lo,hi),loss='soft_l1',max_nfev=600,ftol=1e-9,xtol=1e-9,gtol=1e-9)
  ms={k:{n:{'rms_px':float(np.sqrt(np.mean(e**2))),'residual':e.tolist(),'sigma':s,'group':g} for n,(e,s,g) in terms(sol.x,k).items()} for k in obs}
  ss=np.linalg.svd(sol.jac,compute_uv=False)
  runs.append({'focal_start':f,'cost':float(sol.cost),'parameters':sol.x.tolist(),'geometry':geometry(sol.x),'cameras':{k:camera(sol.x,k).tolist() for k in obs},'metrics':ms,'bound_names':[gnames[i] if i<10 else f'camera_parameter_{i}' for i,x in enumerate(sol.x) if min(abs(x-lo[i]),abs(x-hi[i]))<1e-3],'jacobian_singular_values':ss.tolist()})
  print(json.dumps(runs[-1],ensure_ascii=False),flush=True)
 best=min(runs,key=lambda x:x['cost']);out={'status':'SCREENING_NOT_ACCEPTED','method':'A/G shared geometry fit; B/H/F not used to optimize geometry; 10 bounded structural parameters; 7 pose nuisance parameters per fit view; source pixels unmodified','geometry_parameter_names':gnames,'bounds_lower':lo.tolist(),'bounds_upper':hi.tolist(),'observations':obs,'selected':best,'runs':runs,'units':'D scene units, not measured meters','bed_length_unchanged':float(bx[0]-bm[0]),'source_audit_revision':'2026-10-13 independent native-pixel review; soft beige/grey boundary excluded from fit; hard silhouettes corrected', 'source_semantics':'patient lying on bed; unseen head support allowed within stated height envelope, never exact recovered pillow','limitations':['Camera pose and room depth are not externally calibrated.','Bed endpoint identification and hidden head support are conditional hypotheses.','D furniture retained for all full-scene checks.']}
 (R/'joint_candidate_screening_HISTORICAL_SCREENING.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
