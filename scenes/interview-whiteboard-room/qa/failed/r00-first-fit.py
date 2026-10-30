"""Fit manually labelled static source anchors. No character scale, no image warp.
All coordinates in arbitrary model units (whiteboard outer width fixed at 2.06).
Two source cameras share geometry. Weak occluded second baseline remains conditional.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
def projection(points, c):
    x,y,z,yaw,pitch,roll,f=c
    forward=np.array([np.sin(yaw)*np.cos(pitch),np.cos(yaw)*np.cos(pitch),np.sin(pitch)])
    right=np.array([np.cos(yaw),-np.sin(yaw),0.])
    up=np.cross(right,forward)
    r=right*np.cos(roll)+up*np.sin(roll)
    u=-right*np.sin(roll)+up*np.cos(roll)
    p=np.array(points)-[x,y,z]
    d=p@forward
    return np.stack([960+f*(p@r)/d,540-f*(p@u)/d],axis=1)

# Front anchors: frame corner rectangle excludes radius, table top, skirting corners.
front_uv=np.array([[573,167],[1365,167],[573,595],[1365,595],
                   [530,713],[1352,713],[489,754],[1407,754],
                   [160,852],[1757,852],[113,875]],float)
labels=['board TL','board TR','board BL','board BR','table rear L','table rear R',
        'table front L','table front R','left rear skirting','right rear skirting','left return skirting']
def geometry(g):
    height,bottom,table_width,table_depth,table_y,table_z,wall_y,wall_half,return_y=g
    return [[-1.03,0,bottom+height],[1.03,0,bottom+height],[-1.03,0,bottom],[1.03,0,bottom],
            [-table_width/2,table_y+table_depth/2,table_z],[table_width/2,table_y+table_depth/2,table_z],
            [-table_width/2,table_y-table_depth/2,table_z],[table_width/2,table_y-table_depth/2,table_z],
            [-wall_half,wall_y,.14],[wall_half,wall_y,.14],[-wall_half,return_y,.14]]
g0=np.array([1.12,1.19,2.16,.68,-.70,.80,.55,2.2,-.05])
c0=np.array([0,-6.,1.4,0,-.05,0,2400])
def residual(v):
    c,g=v[:7],v[7:]
    # regularization records assumptions, not physical measurement.
    priors=(g-g0)/[.08,.20,.22,.2,.3,.10,.30,.3,.35]
    return np.r_[(projection(geometry(g),c)-front_uv).ravel(),priors*2,[c[0]*5,c[3]*50,c[5]*50]]
lo=[-.3,-15,.6,-.1,-.4,-.03,600, .9,.9,1.7,.3,-1.5,.65,.1,1.8,-.5]
hi=[.3,-3,2.5,.1,.2,.03,6000, 1.4,1.5,2.6,1.3,-.2,1.,1.4,2.8,.4]
res=least_squares(residual,np.r_[c0,g0],bounds=(lo,hi),max_nfev=10000)
c,g=res.x[:7],res.x[7:]
world=geometry(g)
front_pred=projection(world,c)

# Oblique only has part of left frame and static wall corner, no top/right corners.
# Board left mid/lower and wall/skirt edges provide some parallax, with uncertain picks.
bottom=g[1]; wh=g[7]; wy=g[6]; ry=g[8]
ob_world=[[-1.03,0,bottom],[-1.065,0,bottom-.145],[-1.03,0,bottom+.9],
          [-wh,wy,.14],[-wh,ry,.14],[-1.065,0,1.70]]
ob_uv=np.array([[821,578],[811,683],[822,-310],[437,908],[270,960],[804,241]],float)
ob_weight=np.array([1,1,0,1,1,.4]) # off-screen top not used; pivot uncertainty lower weight
def ob_res(cam):
    r=((projection(ob_world,cam)-ob_uv)*ob_weight[:,None]).ravel()
    return np.r_[r,[(cam[5])*200,(cam[2]-c[2])*15]]
ob0=[-1.2,-3.,1.4,.20,-.04,0,2300]
ob=least_squares(ob_res,ob0,bounds=([-4,-10,.8,-.7,-.4,-.04,700],[1,-1,2.2,.7,.4,.04,5500]),max_nfev=10000)
result={'units':'arbitrary model units; outer board width=2.06; no character scale',
        'geometry_parameter_names':['board_height','board_bottom','table_width','table_depth','table_y','table_z','wall_y','wall_half','return_y'],
        'geometry':dict(zip(['board_height','board_bottom','table_width','table_depth','table_y','table_z','wall_y','wall_half','return_y'],g.tolist())),
        'camera_parameter_names':['x','y','z','yaw_rad','pitch_rad','roll_rad','focal_pixels'],
        'front':c.tolist(),'oblique':ob.x.tolist(),
        'front_anchors':[{'id':lab,'world':pt,'source_px':uv.tolist(),'predicted_px':pred.tolist(),'error_px':float(np.linalg.norm(uv-pred))} for lab,pt,uv,pred in zip(labels,world,front_uv,front_pred)],
        'oblique_anchors':[{'world':pt,'source_px':uv.tolist(),'predicted_px':pred.tolist(),'weight':float(w),'error_px':float(np.linalg.norm(uv-pred))} for pt,uv,pred,w in zip(ob_world,ob_uv,projection(ob_world,ob.x),ob_weight)],
        'limitations':['manual anchors, rounded corner centers approximate','regularized and underdetermined; not metric reconstruction','oblique lacks sufficient nonoccluded objects; viewpoint conditional','no image warping; projection only; dynamic character excluded from fit']}
(ROOT/'docs/camera-fit.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
