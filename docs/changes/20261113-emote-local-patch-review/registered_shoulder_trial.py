#!/usr/bin/env python3
"""Register clean adjacent collar pixels onto F17; knee remains unresolved."""
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,distance_transform_edt
import numpy as np,json,hashlib,sys
from try_local_candidates import ROOT,mask_polygon,compare

parent=ROOT/'emotes/sunburst/agent-emotes/03-awake/versions/20261113-local-patch-review'
refit='--refit-boundary' in sys.argv
out=parent/'v5-donor-assessment'/('shoulder-trial-refit' if refit else 'shoulder-trial');out.mkdir(exist_ok=False)
target=Image.open(parent/'original-decoded/17.png').convert('RGB')
donor=Image.open(parent/'original-decoded/28.png').convert('RGB')
source=np.array([[257,459],[308,477],[249,524]],float)
dest=np.array([[272,480],[309,504],[250,521]],float)
transform=np.linalg.solve(np.c_[dest,np.ones(3)],source)
yy,xx=np.indices((768,768),dtype=float);coordinates=np.stack([xx,yy,np.ones_like(xx)],-1)@transform
a=np.array(target);d=np.array(donor)
registered=np.stack([map_coordinates(d[:,:,c].astype(float),[coordinates[:,:,1],coordinates[:,:,0]],order=1,mode='nearest') for c in range(3)],-1)
poly=[[251,511],[256,494],[267,483],[279,477],[292,484],[302,493],[307,498],[309,506],[307,512],[291,514],[279,508],[265,508]]
if refit:poly=[[248,516],[253,495],[267,483],[279,477],[292,484],[302,493],[306,498],[309,503],[317,508],[319,517],[304,521],[288,514],[272,509],[257,512]]
mask=mask_polygon(target.size,poly)
# Restore all pixels of the real reach, including its left-most fingertips;
# the only allowed shoulder edit is below y477 and to the left of x310.
protection=Image.new('L',target.size);pd=ImageDraw.Draw(protection)
pd.rectangle((285,425,507,476),fill=255);pd.rectangle((310,425,507,544),fill=255)
if refit:
    protection=Image.new('L',target.size);pd=ImageDraw.Draw(protection)
    pd.rectangle((285,425,507,476),fill=255);pd.rectangle((310,425,507,504),fill=255);pd.rectangle((321,505,507,544),fill=255)
allowed=(np.array(mask)>0)&(np.array(protection)==0)
alpha=np.minimum(distance_transform_edt(allowed)/2,1)*allowed
b=np.rint(a*(1-alpha[:,:,None])+registered*alpha[:,:,None]).clip(0,255).astype('uint8')
changed=np.any(a!=b,axis=-1);assert not np.any(changed&~allowed)
candidate=Image.fromarray(b);mask=Image.fromarray(allowed.astype('uint8')*255)
candidate.save(out/'candidate-frame17.png');mask.save(out/'allowed-mask.png');protection.save(out/'protected-reach.png')
compare(target,candidate,mask,[240,470,325,535],out/'comparison-3x.png')
(out/'registration.json').write_text(json.dumps({'status':'pending_static_review_not_accepted',
    'target_frame':17,'donor_frame':28,'donor_source':'strip-2 cell4',
    'source_points':source.tolist(),'target_points':dest.tolist(),'inverse_affine_coefficients':transform.tolist(),
    'polygon':poly,'changed_pixels':int(changed.sum()),'outside_mask_changed_pixels':0,
    'correct_reaching_region_changed_pixels':int((changed&(np.array(protection)>0)).sum()),
    'candidate_rgb_sha256':hashlib.sha256(b.tobytes()).hexdigest(),
    'unresolved':'Redundant knee hand/sleeve still present; no whole-frame acceptance.',
    'expanded_to_other_frames':False,'browser_playback':'not_attempted'},indent=2)+'\n')
