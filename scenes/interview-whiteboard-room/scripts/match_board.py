"""Static source feature correspondences only. Homography never applied to QA images.
Dependency: OpenCV installed in /tmp/interview-vision-deps for this execution.
"""
import sys,json
sys.path.insert(0,'/tmp/interview-vision-deps')
import cv2,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
a=cv2.imread(str(ROOT/'textures/whiteboard-source-plane.png'),0)
b=cv2.imread(str(ROOT/'sources/BV14ioLBAEDt_1505.632497_oblique.png'),0)
# Only source board pixels, excluding human body and far background.
mask=np.zeros(b.shape,np.uint8)
mask[:560,1410:]=255
mask[:100,840:]=255
mask[30:180,840:920]=255
det=cv2.SIFT_create(nfeatures=9000,contrastThreshold=.008,edgeThreshold=12)
ka,da=det.detectAndCompute(a,None);kb,db=det.detectAndCompute(b,mask)
knn=cv2.BFMatcher().knnMatch(da,db,k=2)
good=[m for m,n in knn if m.distance<.72*n.distance]
pa=np.float32([ka[m.queryIdx].pt for m in good]);pb=np.float32([kb[m.trainIdx].pt for m in good])
H,inliers=cv2.findHomography(pa,pb,cv2.RANSAC,3)
assert H is not None and inliers.sum()>12,'Insufficient static board matches'
corners=np.float32([[0,0],[a.shape[1]-1,0],[a.shape[1]-1,a.shape[0]-1],[0,a.shape[0]-1]])
mapped=cv2.perspectiveTransform(corners[:,None,:],H)[:,0,:]
rows=[{'texture_xy':p.tolist(),'oblique_xy':q.tolist()} for p,q,i in zip(pa,pb,inliers.ravel()) if i]
record={'method':'SIFT ratio0.72 + RANSAC3px, only static board polygons; projective extrapolation for fitting, no warped QA',
 'texture_size':[a.shape[1],a.shape[0]],'good_matches':len(good),'inlier_count':int(inliers.sum()),'homography_texture_to_oblique':H.tolist(),
 'mapped_sheet_corners':mapped.tolist(),'inlier_matches':rows,'limits':'Occluded corners extrapolated, matches on same planar object do not resolve whole room depth.'}
(ROOT/'docs/board-feature-matches.json').write_text(json.dumps(record,indent=2))
vis=cv2.drawMatches(a,ka,b,kb,good,None,matchesMask=inliers.ravel().tolist(),flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
cv2.imwrite(str(ROOT/'qa/r01/board-feature-correspondences.jpg'),vis,[cv2.IMWRITE_JPEG_QUALITY,85])
print(json.dumps({k:v for k,v in record.items() if k!='inlier_matches'},indent=2))
