"""Broad bed-footprint camera feasibility test, no geometry changes.
Not a recovered pillow position. Bounds are deliberately permissive diagnostics.
"""
from pathlib import Path
R=Path(__file__).parent
exec((R/'fit_frozen_cameras.py').read_text().split('# Shared-focal camera pair;')[0])
old=json.load(open(R/'camera_candidates.json'))
v=np.array(O['Bed • mattress and sheet']['vertices']);mins=v.min(0);maxs=v.max(0)
# Allow the entire negative-X half of actual mattress, full width, and a generous above-mattress range.
# This is weaker than a proper lying-patient constraint, to avoid claiming an exact head/pillow position.
poslo=np.array([mins[0]+.01,mins[1]+.01,maxs[2]+.05]);poshi=np.array([(mins[0]+maxs[0])/2,maxs[1]-.01,maxs[2]+1.0])
q0=np.array(old['selected']['parameters']);lo=np.r_[base[:3]-.5,poslo,base[:3]-.5,poslo,np.log(15)];hi=np.r_[base[:3]+.5,poshi,base[:3]+.5,poshi,np.log(60)]
unpack=lambda q:{k:np.r_[q[i*6:i*6+6],q[12]] for i,k in enumerate(views)}
def fun(q):
 xs=unpack(q);return np.r_[residual(xs['A'],'A',1,False),residual(xs['B'],'B',1,False),(xs['A'][3:6]-xs['B'][3:6])/.30*.2]
runs=[]
for f in [20,30,40,50]:
 st=np.clip(q0,lo+1e-4,hi-1e-4);st[12]=np.log(f)
 sol=least_squares(fun,st,bounds=(lo,hi),loss='soft_l1',max_nfev=1000,ftol=1e-10,xtol=1e-10,gtol=1e-10);xs=unpack(sol.x)
 runs.append({'initial_focal_mm':f,'cost':float(sol.cost),'parameters':sol.x.tolist(),'bound_parameters':[i for i in range(13) if min(abs(sol.x[i]-lo[i]),abs(sol.x[i]-hi[i]))<1e-3],'views':{k:{'metrics':metrics(x,k),'camera_parameters':x.tolist()} for k,x in xs.items()}})
 print(f,sol.cost,np.exp(sol.x[12]),sol.x[3:6],sol.x[9:12],flush=True)
sel=min(runs,key=lambda r:r['cost']);xs=unpack(np.array(sel['parameters']));cams={}
for k,x in xs.items():
 m=np.eye(4);m[:3,:3]=Rotation.from_rotvec(x[:3]).as_matrix();m[:3,3]=x[3:6];cams[k]={'matrix_world':m.tolist(),'lens_mm':float(np.exp(x[6])),'sensor_width_mm':36,'sensor_fit':'HORIZONTAL','shift_x':0,'shift_y':0,'location':x[3:6].tolist(),'rotation_euler_xyz_rad':Rotation.from_matrix(m[:3,:3]).as_euler('xyz').tolist()}
checks={}
for k,c in {**{k:old['cameras'][k] for k in old['cameras']},'old_F':J['cameras']['MATCH_F_Turning_Right'],'old_G':J['cameras']['MATCH_G_Sofa_And_Bed'],'old_H':J['cameras']['MATCH_H']}.items():
 p=np.array(c['matrix_world'])[:3,3];checks[k]={'position':p.tolist(),'inside_mattress_xy':bool((p[:2]>=mins[:2]).all() and (p[:2]<=maxs[:2]).all()),'negative_X_distance_outside_mattress':float(max(0,mins[0]-p[0])),'height_above_mattress_top':float(p[2]-maxs[2])}
out={'status':'unaccepted broad bed-footprint stress test, not a calibrated lying-eye camera','user_semantics':'The first-person camera is the patient lying on the hospital bed; female role is a nurse/doctor (user supplied, pending audio/subtitle verification).','frozen_blend_sha256':J['source_sha256'],'semantic_audit_of_free_camera_and_D':checks,'mattress_min':mins.tolist(),'mattress_max':maxs.tolist(),'bounds':{'position_min':poslo.tolist(),'position_max':poshi.tolist(),'definition':'Actual mattress negative-X half, full mattress width, 0.05 to 1.0 D scene unit above mattress. These broad bounds are a feasibility test, not physical measurements or validated lying anatomy.'},'selected':sel,'cameras':cams,'runs':runs,'limits':['No geometry/material changes.','Broad permissible region includes poses not anatomically lying; passing would still require a proper pillow/head frame.','Bound saturation or residuals are diagnostics conditional on D and correspondences, not proof of true scene dimensions.']}
(R/'patient_camera_constraint.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('SELECTED',json.dumps(cams));print('METRICS',json.dumps(sel['views']))
