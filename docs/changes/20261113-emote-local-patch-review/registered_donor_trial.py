#!/usr/bin/env python3
"""New trial: landmark-registered neighboring cloth, distinct from v4 fixed paste.

Only clothing coordinates are warped. Original face, body silhouette, both valid
hands and every pixel outside the explicit mask remain fixed. No network/API.
"""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import map_coordinates,distance_transform_edt,label
import numpy as np,json,hashlib,sys
from try_local_candidates import ROOT,mask_polygon,compare

def main():
    parent=ROOT/'emotes/sunburst/agent-emotes/02-butterfly/versions/20261113-local-patch-review'
    band='--refit-right-band' in sys.argv
    refit='--refit-stripe' in sys.argv or band
    out=parent/'v5-registered-donor'/('trial-23-right-band' if band else 'trial-23-refit' if refit else 'trial-23');out.mkdir(parents=True,exist_ok=False)
    target=Image.open(parent/'original-decoded/27.png').convert('RGB')
    donor=Image.open(parent/'original-decoded/23.png').convert('RGB')
    sx=[530,548,565,580,590];tx=[568,586,605,624,642]
    source_rows=[[480]*5,[505,505,504,509,508],[543,544,539,535,536],[555,556,550,546,548]]
    target_rows=[[475,475,477,481,488],[511,511,509,505,500],[546,545,542,538,535],[557,555,552,548,546]]
    if refit: target_rows[2]=[545,542,539,536,534]
    source_points=np.array([(x,source_rows[row][col]) for row in range(4) for col,x in enumerate(sx)],float)
    target_points=np.array([(x,target_rows[row][col]) for row in range(4) for col,x in enumerate(tx)],float)
    yy,xx=np.indices((768,768),dtype=float)
    coords=LinearNDInterpolator(target_points,source_points)(xx,yy)
    valid=np.isfinite(coords).all(-1);coords[~valid]=0
    pixels=np.array(donor)
    warped=np.stack([map_coordinates(pixels[:,:,c].astype(float),[coords[:,:,1],coords[:,:,0]],order=1,mode='nearest') for c in range(3)],-1)
    poly=[[574,480],[592,480],[612,485],[625,493],[636,505],[633,515],[641,527],[637,540],[626,549],[607,553],[590,545],[579,529],[572,511]]
    allowed=np.array(mask_polygon(target.size,poly))>0
    # Hand/cuff boundaries manually reviewed at 12x; preserve the real palm and
    # its outline, excluding the distinct left-side redundant thumb.
    right_hand=[[638,484],[664,481],[680,493],[712,492],[716,518],[700,536],[671,540],[649,535],[643,532],[638,528],[635,523],[633,519],[636,511],[631,504],[633,496]]
    if band:
        right_hand=[[638,484],[664,481],[680,493],[712,492],[716,518],[700,536],[671,535],[649,535],[643,532],[638,528],[635,523],[633,519],[636,511],[631,504],[633,496]]
    protection=mask_polygon(target.size,right_hand)
    ImageDraw.Draw(protection).rectangle((460,473,527,539),fill=255)
    protected=np.array(protection)>0
    allowed&=valid&~protected
    alpha=np.minimum(distance_transform_edt(allowed)/2,1)*allowed
    a=np.array(target);b=np.rint(a*(1-alpha[:,:,None])+warped*alpha[:,:,None]).clip(0,255).astype('uint8')
    band_details=None
    if band:
        # Independently protect the connected real palm's skin and a 3px outline.
        roi=np.zeros((768,768),bool);roi[475:542,633:723]=True
        r,g,bl=[a[:,:,c].astype(int) for c in range(3)]
        skin=roi&(r>170)&(r-g>3)&(r-bl>6)
        labels,_=label(skin);component=labels==labels[514,670]
        assert labels[514,670]!=0
        actual_palm=distance_transform_edt(~component)<=3
        protected|=actual_palm
        protection=Image.fromarray(protected.astype('uint8')*255)
        b[protected]=a[protected];allowed&=~protected
        dsx=[580,590,610,631,640];dtx=[628,642,655,670,678]
        srows=[[529,529,534,531,533],[535,536,543,540,538],[546,548,555,554,548]]
        trows=[[530,531,535,535,536],[538,536,540,541,540],[548,548,554,552,547]]
        sp=np.array([(x,srows[row][c]) for row in range(3) for c,x in enumerate(dsx)],float)
        tp=np.array([(x,trows[row][c]) for row in range(3) for c,x in enumerate(dtx)],float)
        cc=LinearNDInterpolator(tp,sp)(xx,yy);vv=np.isfinite(cc).all(-1);cc[~vv]=0
        lower=np.stack([map_coordinates(pixels[:,:,c].astype(float),[cc[:,:,1],cc[:,:,0]],order=1,mode='nearest') for c in range(3)],-1)
        lower_poly=[[628,533],[637,530],[646,534],[656,535],[677,537],[677,543],[667,548],[653,550],[644,546],[630,545]]
        lower_allowed=(np.array(mask_polygon(target.size,lower_poly))>0)&vv&~protected
        la=np.minimum(distance_transform_edt(lower_allowed)/2,1)*lower_allowed
        b=np.rint(b*(1-la[:,:,None])+lower*la[:,:,None]).clip(0,255).astype('uint8')
        allowed|=lower_allowed
        band_details={'source_points':sp.tolist(),'target_points':tp.tolist(),'polygon':lower_poly,
                      'actual_palm_skin_seed':[670,514],'actual_palm_outline_protection_px':3}
    changed=np.any(a!=b,axis=-1)
    assert not np.any(changed&~allowed) and not np.any(changed&protected)
    mask=Image.fromarray(allowed.astype('uint8')*255);candidate=Image.fromarray(b)
    target.save(out/'original-frame27.png');candidate.save(out/'candidate-frame27.png')
    mask.save(out/'allowed-mask.png');protection.save(out/'protected-hands.png')
    sample=Image.fromarray(np.rint(warped).clip(0,255).astype('uint8'));sample.save(out/'registered-donor-layer.png')
    compare(target,candidate,mask,[550,470,690,562],out/'comparison-3x.png')
    native=Image.new('RGB',(768*2,768+25),'#eee');d=ImageDraw.Draw(native)
    native.paste(target,(0,25));native.paste(candidate,(768,25));d.text((4,4),'ORIGINAL 27 / 768px',fill='black');d.text((772,4),'REGISTERED CANDIDATE / NOT ACCEPTED',fill='black');native.save(out/'comparison-native.png')
    report={'status':'pending_static_review_not_accepted','target_frame':27,'donor_frame':23,
      'method':'piecewise affine inverse map through 20 garment landmarks, bilinear donor sampling, 2px inward feather',
      'source_points':source_points.tolist(),'target_points':target_points.tolist(),
      'source_landmark_rows':['upper_cloth','blouse_hem','white_skirt_stripe','lower_skirt_edge'],
      'target_landmarks_hidden_by_extra_hand':'inferred between observed left/right edges; not observed clean ground truth',
      'requested_polygon':poly,'protected_right_hand_polygon':right_hand,
      'changed_pixels':int(changed.sum()),'allowed_pixels':int(allowed.sum()),
      'outside_mask_changed_pixels':0,'correct_hand_region_changed_pixels':0,
      'target_rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest(),
      'donor_rgb_sha256':hashlib.sha256(pixels.tobytes()).hexdigest(),
      'candidate_rgb_sha256':hashlib.sha256(b.tobytes()).hexdigest(),
      'expansion_to_other_frames':False,'browser_playback':'not_attempted_previous_policy_block_remains'}
    report['stripe_landmark_refinement']=refit
    report['right_stripe_registration']=band_details
    (out/'registration.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'candidate':str(out/'candidate-frame27.png'),'changed_pixels':int(changed.sum())}))

if __name__=='__main__':main()
