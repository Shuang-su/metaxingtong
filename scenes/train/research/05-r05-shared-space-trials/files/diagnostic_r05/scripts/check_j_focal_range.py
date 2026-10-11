exec(open(__file__.replace('check_j_focal_range.py','fit_j_empty.py')).read().split('out={}')[0].replace('f=24*1180/36','f=F*1180/36'))
rows=[]
for F in [18,24,30,36]:
 x0=[.2,-.9,1.5,1.57,0,1.57,1.71,1.08];lo=[-1,-2,.7,1.2,-.2,1.3,1.45,.8];hi=[1.4,0,2.2,1.95,.2,1.85,2.15,1.45]
 ss=least_squares(lambda x:residual(x,True),x0,bounds=(lo,hi),loss='soft_l1',f_scale=2,max_nfev=2000);cam=ss.x[:6];top,bottom=ss.x[6:];rack=project(cam,[[-1.068,-.9,1.925]])[0];rows.append({'focal_gauge':F,'window_top':top,'window_bottom':bottom,'ratio':1.232/(top-bottom),'rack_holdout_prediction':rack.tolist(),'observed_rack_y_approx':123,'camera':cam.tolist()})
(R/'analysis/J_focal_sensitivity.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
