"""Reproduce the internal-tool-only composition trial, NOT an official API result."""
from pathlib import Path
from PIL import Image
import numpy as np
import cv2 as cv
import json
HERE=Path(__file__).resolve().parent

def main():
    a=np.array(Image.open(HERE/'sources/original-17.png').convert('RGB'))
    strip=Image.open(HERE/'sources/api-keys-no-mascot.png').convert('RGB');cell=strip.height
    edited=np.array(strip.crop((cell,0,cell*2,cell)).resize((768,768),Image.Resampling.LANCZOS))
    sift=cv.SIFT_create(nfeatures=3000);region=np.zeros((768,768),np.uint8);region[30:530,:]=255;region[:330,560:]=0
    k1,d1=sift.detectAndCompute(cv.cvtColor(edited,cv.COLOR_RGB2GRAY),region);k2,d2=sift.detectAndCompute(cv.cvtColor(a,cv.COLOR_RGB2GRAY),region)
    good=[m for m,n in cv.BFMatcher().knnMatch(d1,d2,k=2) if m.distance<.75*n.distance]
    pts=np.float32([k1[m.queryIdx].pt for m in good]);target=np.float32([k2[m.trainIdx].pt for m in good])
    matrix,inliers=cv.estimateAffinePartial2D(pts,target,method=cv.RANSAC,ransacReprojThreshold=4)
    assert matrix is not None and inliers.sum()>=10
    warped=cv.warpAffine(edited,matrix,(768,768),flags=cv.INTER_LINEAR,borderValue=(255,255,255))
    mask=Image.open(HERE/'sources/mask-17-1024.png').getchannel('A').resize((768,768),Image.Resampling.NEAREST)
    head=Image.open(HERE/'sources/mask-17-mascot-removal-1024.png').getchannel('A').resize((768,768),Image.Resampling.NEAREST)
    edit=np.maximum(255-np.array(mask),255-np.array(head))
    result=Image.composite(Image.fromarray(warped),Image.fromarray(a),Image.fromarray(edit));result.save(HERE/'internal-frame17-composite.png')
    protected=edit==0;assert np.array_equal(np.array(result)[protected],a[protected])
    sheet=Image.new('RGB',(1536,768),'white');sheet.paste(Image.fromarray(a),(0,0));sheet.paste(result,(768,0));sheet.save(HERE/'internal-frame17-comparison.jpg',quality=94)
    report=dict(status='internal_tool_preview_only_NOT_official_Images_API',matched_features=len(good),registration_inliers=int(inliers.sum()),matrix=matrix.tolist(),changed_protected_pixels=0,edited_pixels=int((edit>0).sum()))
    (HERE/'internal-frame17-registration.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
