"""Fit a camera-only pure-rotation hypothesis from static background point correspondences.
No render or source image is warped or registered; output is a Blender camera matrix.
Furniture and foreground are excluded from match region.
"""
import cv2,numpy as np,json
from pathlib import Path
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path(__file__).parent;D=json.load(open(R/'D_scene_meshes.json'));base=D['cameras']['MATCH_H'];M=np.array(base['matrix']);Q=M[:3,:3]/np.linalg.norm(M[:3,:3],axis=0);f=1920*base['lens']/36
paths=[R.parent/'hospital_anchor_preparation_20261014/restored/hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png',R.parent/'hospital_empty_frame_annotation_20261014/source_views/BV1GqXMByE1s_640.406589_empty_hospital_native.png']
ims=[cv2.imread(str(p),0) for p in paths];mask=np.zeros(ims[0].shape,np.uint8);mask[100:735,275:1520]=255
sift=cv2.SIFT_create(nfeatures=6000);k=[];desc=[]
for im in ims:a,b=sift.detectAndCompute(im,mask);k.append(a);desc.append(b)
matches=cv2.BFMatcher().knnMatch(*desc,k=2);pairs=[(m.queryIdx,m.trainIdx) for m,n in matches if m.distance<.65*n.distance];a=np.array([k[0][i].pt for i,j in pairs]);b=np.array([k[1][j].pt for i,j in pairs]);hom,valid=cv2.findHomography(a,b,cv2.RANSAC,2);a=a[valid.ravel()==1];b=b[valid.ravel()==1]
rays=np.c_[(a[:,0]-960)/f,-(a[:,1]-540)/f,-np.ones(len(a))];world=rays@Q.T

def mat(q):return Rotation.from_rotvec(q[:3]).as_matrix()@Q

def pred(q):
 p=world@mat(q);ff=f*np.exp(q[3]);return np.c_[960+ff*p[:,0]/-p[:,2],540-ff*p[:,1]/-p[:,2]]
sol=least_squares(lambda q:(pred(q)-b).ravel(),np.zeros(4),bounds=([-0.15]*3+[-.1],[.15]*3+[.1]),loss='soft_l1',f_scale=1,max_nfev=1000)
cc=dict(base);mm=M.copy();mm[:3,:3]=mat(sol.x);cc['matrix']=mm.tolist();cc['lens']=base['lens']*np.exp(sol.x[3]);errs=np.linalg.norm(pred(sol.x)-b,axis=1)
res={'status':'CONDITIONAL_CAMERA_ONLY_NOT_METRIC_CALIBRATION','camera':cc,'matched_points_H':a.tolist(),'matched_points_N640':b.tolist(),'fit_parameters':sol.x.tolist(),'match_count':len(a),'residual_px':{'median':float(np.median(errs)),'p95':float(np.quantile(errs,.95)),'max':float(errs.max())},'source_region':[275,100,1520,735],'source_camera_inherited':'D MATCH_H','assumptions':['Same static background and window','Pure rotation plus focal ratio; fixed inherited H eye position, not a proved patient eye','Far background fit cannot establish depth translation or bed position'],'image_warp_applied':False,'furniture_used':False}
(R/'N640_relative_camera.json').write_text(json.dumps(res,indent=2));print(res['match_count'],res['fit_parameters'],res['residual_px'])
