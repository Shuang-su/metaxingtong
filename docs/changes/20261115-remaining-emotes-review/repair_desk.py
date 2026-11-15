#!/usr/bin/env python3
"""Reversible 11-count desk repair, using existing F49 pixels only. No API."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageSequence, ImageDraw
from scipy.ndimage import binary_dilation, distance_transform_edt

DOC = Path(__file__).resolve().parent
ROOT = DOC.parents[2]
ORIGINAL = DOC / 'source-originals/11-count/master.gif'

def load():
    im = Image.open(ORIGINAL)
    frames, times = [], []
    for f in ImageSequence.Iterator(im):
        frames.append(f.convert('RGB')); times.append(f.info['duration'])
    return frames, times

def plate(frames):
    # Preserve the actual donor desk, fill only its old foreground silhouettes
    # with another unoccupied same-row strip from that same original frame.
    p = frames[48].copy()
    donor = p.crop((28, 688, 110, 732))
    for x0, x1 in [(110, 490), (515, 733)]:
        p.paste(donor.resize((x1-x0,44), Image.Resampling.BILINEAR), (x0,688))
    return p

def foreground(im, variant='r1'):
    a = np.asarray(im); keep = np.zeros(a.shape[:2], bool)
    keep[:688] = True
    # Both hands and the entire moving pendulum lie above this line. Preserve
    # the arm and metronome silhouettes down to their own original dark edge.
    for left,right,bottom in [(110,495,710),(512,735,728)]:
        dark = a[680:bottom,left:right].min(axis=2) < 120
        for k in range(right-left):
            yy = np.flatnonzero(dark[:,k])
            # r0 also mistook a faint isolated desk line for a foreground
            # silhouette. r1 requires contact with the object above the desk.
            connected = variant == 'r0' or dark[:8,k].any()
            if len(yy) and connected: keep[:680+int(yy[-1])+1,left+k] = True
    return binary_dilation(keep, iterations=1)

def quantize(before, after, mask):
    p = before.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
    assert p.convert('RGB').tobytes() == before.tobytes()
    q = after.quantize(palette=p, dither=Image.Dither.NONE)
    p.paste(q,(0,0),Image.fromarray(mask.astype('uint8')*255))
    return p

def repair(im, donor, variant='r1'):
    a=np.asarray(im); b=np.asarray(donor); protect=foreground(im,variant)
    allowed=np.zeros(a.shape[:2],bool);allowed[688:756,8:760]=True
    allowed &= ~protect
    alpha=np.clip(distance_transform_edt(allowed)/2,0,1)
    painted=np.rint(a*(1-alpha[:,:,None])+b*alpha[:,:,None]).astype('uint8')
    p=quantize(im,Image.fromarray(painted),allowed)
    changed=np.any(np.asarray(p.convert('RGB'))!=a,axis=2)
    assert not np.any(changed & protect)
    assert not np.any(changed & ~allowed)
    return p,allowed,protect,alpha

def prototype():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--variant',default='r1',choices=['r0','r1']);args=ap.parse_args()
    variant=args.variant
    fs,ts=load();donor=plate(fs);out=DOC/('prototype-'+variant);out.mkdir(exist_ok=True)
    donor.save(out/'desk-plate-F49.png')
    n=54;p,mask,protect,alpha=repair(fs[n-1],donor,variant)
    p.convert('RGB').save(out/'candidate-54.png')
    for label,arr in [('allowed-mask',mask*255),('protected-mask',protect*255),('alpha',alpha*255)]:
        Image.fromarray(arr.astype('uint8')).save(out/(label+'-54.png'))
    c=Image.new('RGB',(768,3*140),'#eee');d=ImageDraw.Draw(c)
    for j,(label,im) in enumerate([('original F54',fs[53]),('original donor F49',fs[48]),('candidate '+variant+' F54',p.convert('RGB'))]):
        d.text((4,j*140+2),label,fill='black');c.paste(im.crop((0,650,768,768)),(0,j*140+20))
    c.save(out/'native-comparison-54.png')
    (out/'parameters.json').write_text(json.dumps({'affected_prototype_frame':54,'donor_frame':49,'desk_region':[8,688,760,756],'foreground_boxes':[[110,680,495,710],[512,680,735,728]],'dark_threshold':120,'silhouette_dilation_px':1,'inward_feather_px':2,'status':'pending visual review'},indent=2)+'\n')

if __name__=='__main__': prototype()
