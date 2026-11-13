#!/usr/bin/env python3
"""Second, explicitly unaccepted trial using only narrow cloth donor regions."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import map_coordinates,distance_transform_edt
import json,hashlib
from try_local_candidates import ROOT,mask_polygon,compare

def apply(im,points,sx,sy,feather=2):
    a=np.array(im);mask=mask_polygon(im.size,points);allowed=np.array(mask)>0
    donor=np.stack([map_coordinates(a[:,:,c].astype(float),[sy,sx],order=1,mode='nearest') for c in range(3)],axis=-1)
    alpha=np.minimum(distance_transform_edt(allowed)/feather,1)*allowed
    b=np.rint(a*(1-alpha[:,:,None])+donor*alpha[:,:,None]).clip(0,255).astype('uint8')
    assert np.array_equal(a[~allowed],b[~allowed])
    return Image.fromarray(b),mask

def save(name,n,candidate,mask,params,crop):
    parent=ROOT/'emotes/sunburst/agent-emotes'/name/'versions/20261113-local-patch-review'
    out=parent/'v2-cloth-mapping'/f'{n:02d}';out.mkdir(parents=True,exist_ok=False)
    original=Image.open(parent/'original-decoded'/f'{n:02d}.png').convert('RGB')
    candidate.save(out/'candidate.png');mask.save(out/'allowed-mask.png')
    a=np.array(original);b=np.array(candidate);allowed=np.array(mask)>0;changed=np.any(a!=b,axis=-1)
    assert not np.any(changed&~allowed)
    params.update({'frame':n,'status':'requires_visual_review','changed_pixels':int(changed.sum()),
        'pixels_changed_outside_mask':0,'protected_pixels':int((~allowed).sum()),
        'original_rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'candidate_rgb_sha256':hashlib.sha256(b.tobytes()).hexdigest()})
    (out/'candidate.json').write_text(json.dumps(params,indent=2)+'\n')
    compare(original,candidate,mask,crop,out/'comparison.png')

def main():
    yy,xx=np.indices((768,768),dtype=float)
    for n in [24,25,26,27,28]:
        p=ROOT/'emotes/sunburst/agent-emotes/02-butterfly/versions/20261113-local-patch-review/original-decoded'/f'{n:02d}.png'
        im=Image.open(p).convert('RGB')
        # Same-frame, narrow pure-cloth columns, avoiding the valid hand at the left hip.
        points=[[575,475],[593,475],[614,482],[627,491],[638,504],[634,516],[644,527],[639,537],[629,548],[605,552],[589,541],[577,521],[570,500]]
        sx=540+(xx-570)*.24
        sy=yy+(xx-570)*.075
        result,mask=apply(im,points,sx,sy)
        save('02-butterfly',n,result,mask,{'method':'same-frame affine cloth sampling','polygon':points,
           'donor_mapping':'sx=540+0.24*(x-570); sy=y+0.075*(x-570)','protected':'All pixels outside mask; both valid hands outside mask'},[550,465,680,565])
    p=ROOT/'emotes/sunburst/agent-emotes/03-awake/versions/20261113-local-patch-review/original-decoded/17.png'
    im=Image.open(p).convert('RGB')
    points=[[478,568],[512,563],[546,568],[563,582],[570,608],[568,627],[551,640],[512,637],[487,629],[473,613],[471,591]]
    # Map only cream/gray skirt above the cuff. No skin, hair, cuffs or hand donor.
    sx=504+(xx-478)*.4;sy=548+(yy-563)*.19
    result,mask=apply(im,points,sx,sy)
    save('03-awake',17,result,mask,{'method':'same-frame affine dress sampling, knee only',
       'polygon':points,'donor_mapping':'sx=504+0.4*(x-478); sy=548+0.19*(y-563)',
       'limitation':'Shoulder defect intentionally unmodified in this trial; whole-frame acceptance impossible.'},[440,530,585,655])

if __name__=='__main__':main()
