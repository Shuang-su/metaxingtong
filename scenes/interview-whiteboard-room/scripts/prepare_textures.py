"""Source-grounded whiteboard plane and explicitly inferred procedural wood.
This is UV texture preparation requested for reconstruction, not a replacement source image.
"""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'sources/BV14ioLBAEDt_1283.813032_front.png'
# Four sheet-inner corners. Rounded corner border excluded, no human in this quad.
quad=np.array([[582,177],[1354,178],[1353,586],[582,585]],float)
w,h=772,409
out=np.array([[0,0],[w-1,0],[w-1,h-1],[0,h-1]],float)
A=[];b=[]
for (x,y),(u,v) in zip(out,quad):
    A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
    b.extend([u,v])
coeff=np.linalg.solve(np.array(A),np.array(b))
Image.open(src).transform((w,h),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC).save(ROOT/'textures/whiteboard-source-plane.png')
rng=np.random.default_rng(20261030)
n=gaussian_filter(rng.normal(size=(256,1024)),sigma=(.8,45))
n=n/(n.std()+1e-8)
y,x=np.mgrid[:256,:1024]
grain=.045*n+.016*np.sin(y*.65+np.sin(x*.008)*1.8)
col=np.array([.57,.42,.27])+grain[:,:,None]*np.array([1,.85,.7])
Image.fromarray(np.uint8(np.clip(col,0,1)*255)).save(ROOT/'textures/wood-inferred.png')
record={'source':src.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'sheet_quad_pixels_TL_TR_BR_BL':quad.tolist(),'output_size':[w,h],
 'method':'Pillow inverse projective mapping solved from 4 sheet corners; bicubic; texture UV only, never source/render overlay warp',
 'inverse_perspective_coefficients':coeff.tolist(),
 'occlusion':'No character pixels in selected frontal sheet quad. Oblique source not used as texture.',
 'missing_regions':'Rounded perimeter/corner chips outside quad and reverse face not observed. No invented text in unseen parts; reverse is plain inferred board.',
 'photometric_limit':'Source shading/compression remain baked in plane; not measured diffuse albedo. Wood grain is a deterministic inferred material, not source extraction.'}
(ROOT/'textures/provenance.json').write_text(json.dumps(record,indent=2))
print('Prepared source board texture and inferred wood texture.')
