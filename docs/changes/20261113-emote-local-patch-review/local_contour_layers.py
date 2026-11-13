#!/usr/bin/env python3
"""Reversible local garment contour artwork; never a full-frame redraw.

New cloth boundaries are explicitly authored hypotheses, not recovered source
pixels. Every fill/stroke is stored on a transparent layer with an exact mask.
"""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
import numpy as np,json,hashlib
from try_local_candidates import ROOT,mask_polygon,compare

def bezier(start,segments,steps=24):
    points=[start];p=np.array(start,float)
    for c1,c2,end in segments:
        c1,c2,e=map(lambda x:np.array(x,float),(c1,c2,end))
        for t in np.linspace(0,1,steps+1)[1:]:points.append(tuple((1-t)**3*p+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*e))
        p=e
    return points

def build_knee_layer(original,narrow=False):
    a=np.array(original);h,w=a.shape[:2]
    poly=[[478,558],[500,552],[536,554],[557,568],[568,591],[568,618],[569,639],[549,643],[522,639],[498,637],[479,631],[468,617],[467,591]]
    if narrow:
        poly=[[477,584],[488,573],[505,568],[530,569],[550,578],[564,593],[568,618],[569,639],[549,643],[522,639],[498,637],[479,631],[468,617],[467,598]]
    allowed=np.array(mask_polygon(original.size,poly))>0
    # Keep the other resting hand, including its outline, unchanged.
    allowed[:,568:]=False
    hem=bezier((470,612),[
      ((474,614),(478,621),(483,619)),
      ((490,615),(494,621),(499,623)),
      ((507,626),(510,619),(516,621)),
      ((523,625),(527,627),(534,625)),
      ((542,623),(548,626),(552,631)),
      ((557,635),(561,631),(567,636))])
    S=4
    def scaled(points):return [(round(x*S),round(y*S)) for x,y in points]
    # Below the new skirt boundary, borrow existing dark leggings, not skin.
    yy,xx=np.indices((h,w));under=a[np.clip(yy+15,0,h-1),xx]
    canvas=Image.fromarray(under).resize((w*S,h*S),Image.Resampling.NEAREST)
    dr=ImageDraw.Draw(canvas)
    cloth=[(464,547),(566,547),(570,638)]+list(reversed(hem))+[(464,612)]
    dr.polygon(scaled(cloth),fill=(246,236,230))
    # A separate gray fold joins the already visible diagonal skirt shading.
    fold=bezier((475,564),[((482,565),(493,558),(507,555)),((503,574),(495,599),(479,614))])
    dr.polygon(scaled(fold+[(469,613),(466,593)]),fill=(171,157,145))
    fold_line=bezier((506,557),[((501,574),(496,592),(489,606))])
    dr.line(scaled(fold_line),fill=(193,178,165),width=round(2.5*S),joint='curve')
    # Crisp local hem follows neighboring lace peaks; no rectangular patch edge.
    dr.line(scaled(hem),fill=(40,26,27),width=round(3.4*S),joint='curve')
    dr.line(scaled([(x,y-2.4) for x,y in hem]),fill=(251,245,239),width=round(1.2*S),joint='curve')
    paint=np.array(canvas.resize((w,h),Image.Resampling.LANCZOS))
    # Subtle existing fabric-color variation, capped at 3 levels, keeps the new
    # panel from being a flat digital sticker without importing foreign shapes.
    texture=a[545:568,524:548].astype(float)
    texture=texture-np.median(texture.reshape(-1,3),axis=0)
    texture=np.clip(texture,-3,3)
    variations=texture[yy%texture.shape[0],xx%texture.shape[1]]
    cream=np.max(np.abs(paint.astype(int)-np.array([246,236,230])),axis=-1)<10
    paint=np.rint(paint.astype(float)+variations*cream[:,:,None]).clip(0,255).astype('uint8')
    alpha=np.minimum(distance_transform_edt(allowed)/2.0,1)*allowed
    rgba=np.dstack([paint,np.rint(alpha*255).astype('uint8')])
    return Image.fromarray(rgba),Image.fromarray(allowed.astype('uint8')*255),{'allowed_polygon':poly,'protected_other_hand_x_min':568,'authored_hem_polyline':hem,'new_artwork':'Cream skirt panel, gray fold, and curved hem; same-frame leggings pixels below hem.'}

def main():
    p=ROOT/'emotes/sunburst/agent-emotes/03-awake/versions/20261113-local-patch-review'
    out=p/'v6-contour-and-motion'/'prototype-17';out.mkdir(parents=True,exist_ok=False)
    original=Image.open(p/'original-decoded/17.png').convert('RGB')
    shoulder=Image.open(p/'v5-donor-assessment/shoulder-trial-refit/candidate-frame17.png').convert('RGB')
    layer,mask,details=build_knee_layer(original)
    candidate=Image.alpha_composite(shoulder.convert('RGBA'),layer).convert('RGB')
    shoulder_mask=Image.open(p/'v5-donor-assessment/shoulder-trial-refit/allowed-mask.png')
    union=Image.fromarray(np.maximum(np.array(mask),np.array(shoulder_mask)))
    a=np.array(original);b=np.array(candidate);allowed=np.array(union)>0
    assert np.array_equal(a[~allowed],b[~allowed])
    candidate.save(out/'candidate-frame17.png');layer.save(out/'knee-layer.png');mask.save(out/'knee-mask.png');union.save(out/'combined-mask.png')
    compare(original,candidate,union,[435,530,590,655],out/'knee-comparison-3x.png')
    (out/'construction.json').write_text(json.dumps({'status':'candidate_for_review','frame':17,'method':'Accepted-in-general v5 shoulder base plus reversible authored local skirt contours',**details,
        'changed_pixels':int(np.any(a!=b,axis=-1).sum()),'outside_mask_changed_pixels':0,'original_rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'candidate_rgb_sha256':hashlib.sha256(b.tobytes()).hexdigest(),'not_historical_ground_truth':True},indent=2)+'\n')

if __name__=='__main__':main()
