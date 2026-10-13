"""HISTORICAL INVALID H CALIBRATION: whole-convex-hull contour distance allowed wrong edge association. Retained for reproducibility only. See audit_H_upper_envelope.py and the authoritative corrected JSON.
Freeze J1 geometry, calibrate per-view nuisance cameras on disjoint fixed anchors.
B TV three corners only; H original left window line and unchanged sofa back envelope;
F TV three corners only. All target pillar/rail/bed/window3 observations stay holdout.
"""
from screen_joint_candidate import *
from scipy.optimize import least_squares
Q=json.load(open(R/'joint_candidate_screening.json'))['selected'];q=np.array(Q['parameters']);g=geometry(q)
AA={f['id']:f for f in ann['features']}

# Independent side-of-source hard-boundary measurements, not old invalid sofa arm samples.
H={'m0_axis':[[82,150],[32,1050]],'m1_axis':[[990,20],[992,790]],'m2_axis':[[1542,500],[1551,700]],'grey_right_axis':[[1801,300],[1814,500],[1827,700],[1840,900]],'pillar_grey_axis':[[1640,500]],'sofaL':[[882,804],[963,798],[1080,795],[1196,793]],'sofaR':[[1228,798],[1332,791],[1440,787],[1481,788]]}
B=C['observations']['B'];F={a['id']:a['observed'] for a in FP['architectural_observations']['F']};F['shell_corner']=F['shell_corner17'];F['bed_hold']=AA['F_bed_upper_left_visible']['source_xy'];F['rail_upper']=AA['F_rail_window_side_upper_edge']['source_xy'];F['rail2_upper']=AA['F_rail_room_side_upper_edge']['source_xy'];F['rail_left']=[254,67]
# Explicit source lines from this task.
B.update({'m2_axis':[[16,500],[3,600]],'grey_right_axis':[[307,500],[291,700],[274,900],[262,1050]],'rail2_upper':[[330,86],[1100,0]],'pillar_grey_axis':[[150,400],[115,800]]})

def holdcam(v):
 pos=np.array([bm[0]+g['bed_dx']+(bx[0]-bm[0])*v[3],bc[1]+g['bed_dy']+(v[4]-.5)*(bx[1]-bm[1])*g['bed_width_scale'],bx[2]+v[5]])
 return np.r_[v[:3],pos,v[6]]
def calibrate(v,k):
 c=holdcam(v);a={'B':B,'H':H,'F':F}[k];res=[]
 if k in ['B','F']:
  for n in ['tv_tl','tv_tr','tv_br'] if k=='B' else ['tv_tl','tv_tr','tv_bl']:res.extend((project(c,[P[n]])[0]-a[n])/4)
  # shared focal within same uninterrupted A/B/F scene segment
  res.append((v[6]-q[16])/.003)
 else:
  for n,x in [('m0_axis',-1.603616),('m1_axis',0)]:res.extend(line(c,xline(x,g['window_y']+.0027),a[n])/8)
  for ob,n in [(SOFAL,'sofaL'),(SOFAR,'sofaR')]:res.extend(contour(c,V[ob],a[n])/12)
 return np.array(res)
def held_metrics(c,k):
 a={'B':B,'H':H,'F':F}[k];e={};wy=g['window_y'];h=2.714665413;pj=1.521875;pr=pj+g['pillar_width'];front=wy-g['pillar_projection'];rx=pj+g['pillar_width']*g['rail_pillar_fraction'];rz=g['rail_height'];sep=g['rail_depth_separation']
 for n,x in [('m2_axis',1.5),('m3_axis',g['m3_x']),('m4_axis',4.994256)]:
  if n in a:e[n]=line(c,xline(x,wy+.0027),a[n])
 for n,x in [('m3_top',g['m3_x']),('m4_top',4.994256),('shell_corner',5.5375)]:
  if n in a:e[n]=project(c,[[x,wy,h]])[0]-a[n]
 if 'grey_right_axis' in a:e['grey_right_axis']=line(c,xline(pr+.59,front-.02),a['grey_right_axis'])
 if 'pillar_grey_axis' in a:e['pillar_grey_axis']=line(c,xline(pr,front),a['pillar_grey_axis'])
 for n,xx in [('rail_upper',rx),('rail2_upper',rx+sep)]:
  if n in a:e[n]=line(c,[[xx-.015,front,rz+.016875],[xx-.015,-3.3828,rz+.016875]],a[n])
 if 'rail_left' in a:e['rail_left']=project(c,[[rx-.015,front,rz+.016875]])[0]-a['rail_left']
 if 'bed_hold' in a:e['bed_hold']=contour(c,bed_transform(V[BED],g),a['bed_hold'])
 if k=='B':e['tv_bl']=project(c,[P['tv_bl']])[0]-a['tv_bl']
 if k=='F':e['tv_br']=project(c,[P['tv_br']])[0]-a['tv_br']
 return {n:{'rms_px':float(np.sqrt(np.mean(z*z))),'residual':z.tolist()} for n,z in e.items()}
out={'geometry_frozen':True,'geometry_file':'joint_candidate_screening.json','calibration_observations':{'B':{n:B[n] for n in ['tv_tl','tv_tr','tv_br']},'F':{n:F[n] for n in ['tv_tl','tv_tr','tv_bl']},'H':{n:H[n] for n in ['m0_axis','m1_axis','sofaL','sofaR']}},'geometry_target_points_used_for_calibration':False,'views':{}}
for k in ['B','H','F']:
 init=normcam(C['cameras']['B']) if k=='B' else normcam(J['cameras']['MATCH_H' if k=='H' else 'MATCH_F_Turning_Right'])
 st=np.r_[init[:3],.13,.4,.43,np.log(34)];low=np.r_[init[:3]-.45,.03,.08,.15,np.log(25)];high=np.r_[init[:3]+.45,.40,.92,.65,np.log(48)]
 runs=[]
 for foc in [30,40]:
  st[-1]=np.log(foc);sol=least_squares(lambda v:calibrate(v,k),st,bounds=(low,high),max_nfev=400,loss='soft_l1',ftol=1e-10,gtol=1e-10,xtol=1e-10);runs.append(sol)
 sol=min(runs,key=lambda x:x.cost);cam=holdcam(sol.x)
 out['views'][k]={'parameters':sol.x.tolist(),'camera':cam.tolist(),'cost':float(sol.cost),'calibration_residual_sigma':calibrate(sol.x,k).tolist(),'heldout':held_metrics(cam,k),'bound_parameters':[i for i,x in enumerate(sol.x) if min(abs(x-low[i]),abs(x-high[i]))<1e-3]}
print(json.dumps(out,ensure_ascii=False,indent=2));(R/'heldout_camera_validation_HISTORICAL_INVALID.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
