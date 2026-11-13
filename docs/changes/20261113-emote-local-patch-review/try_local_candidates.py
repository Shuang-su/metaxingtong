#!/usr/bin/env python3
"""Reversible, local donor-pixel experiments. Never overwrites originals.

These candidates are NOT accepted. Each run has a distinct output directory.
Only polygons in the configuration may change. All coordinates use decoded
768x768 master GIF pixels. Feathering is strictly inward, never beyond a mask.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt
import numpy as np
import json,hashlib

ROOT=Path(__file__).resolve().parents[3]
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)

def mask_polygon(size,points):
    mask=Image.new('L',size);ImageDraw.Draw(mask).polygon(points,fill=255)
    return mask

def clone_shift(im,points,offset,feather=2.0):
    mask=mask_polygon(im.size,points)
    a=np.array(im);allowed=np.array(mask)>0
    alpha=np.minimum(distance_transform_edt(allowed)/feather,1.0)*allowed
    yy,xx=np.indices(allowed.shape)
    dx,dy=offset
    donor=a[np.clip(yy-dy,0,a.shape[0]-1),np.clip(xx-dx,0,a.shape[1]-1)]
    result=np.rint(a*(1-alpha[...,None])+donor*alpha[...,None]).astype('uint8')
    assert np.array_equal(result[~allowed],a[~allowed])
    return Image.fromarray(result),mask

def compare(original,candidate,mask,box,path):
    views=[original,candidate,Image.composite(Image.new('RGB',original.size,'#ff0044'),original,mask.point(lambda p:int(p*.35)))]
    w,h=(box[2]-box[0])*3,(box[3]-box[1])*3
    out=Image.new('RGB',(w*3,h+30),'#eee');d=ImageDraw.Draw(out)
    for i,(label,im) in enumerate(zip(['ORIGINAL','CANDIDATE - NOT ACCEPTED','ALLOWED CHANGE MASK'],views)):
        out.paste(im.crop(box).resize((w,h),Image.Resampling.NEAREST),(i*w,30))
        d.text((i*w+5,5),label,fill='black',font=FONT)
    out.save(path)

def main():
    configs=[{
       'emote':'02-butterfly','frame':27,'candidate':'v1-clone-offset',
       'polygons':[[[574,479],[592,477],[612,483],[627,491],[638,504],[634,516],[644,527],[636,540],[628,550],[605,554],[589,541],[577,521],[571,501]]],
       'offsets':[[70,-6]],'crop':[550,465,680,565],
       'intent':'Replace redundant cuff/hand with nearby same-frame blouse/skirt pixels; keep both correct hands.'
    },{
       'emote':'03-awake','frame':17,'candidate':'v1-clone-offset',
       'polygons':[[[483,567],[520,563],[552,572],[564,596],[563,625],[548,637],[508,637],[482,624],[475,601]],
                   [[258,506],[263,494],[274,485],[290,483],[303,491],[310,503],[305,512],[276,513]]],
       'offsets':[[46,37],[0,-47]],'crop':[240,470,580,650],
       'intent':'Trial donor cloth over redundant knee cuff/hand and donor navy over shoulder fingers; preserve actual reaching hand.'
    }]
    for c in configs:
       out=ROOT/'emotes/sunburst/agent-emotes'/c['emote']/'versions/20261113-local-patch-review'/c['candidate']
       out.mkdir(parents=True,exist_ok=False)
       source=out.parent/'original-decoded'/f"{c['frame']:02d}.png"
       orig=Image.open(source).convert('RGB');cand=orig.copy();union=Image.new('L',orig.size)
       for pts,offset in zip(c['polygons'],c['offsets']):
           # Donor sampling always uses the unmodified original.
           layer,mask=clone_shift(orig,pts,offset)
           cand.paste(layer,(0,0),mask)
           union=Image.fromarray(np.maximum(np.array(union),np.array(mask)))
       cand.save(out/'candidate.png');union.save(out/'allowed-mask.png')
       a=np.array(orig);b=np.array(cand);changed=np.any(a!=b,axis=2);allowed=np.array(union)>0
       assert not np.any(changed&~allowed)
       c.update({'status':'requires_visual_review','source_png_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
           'changed_pixels':int(changed.sum()),'pixels_changed_outside_mask':0,
           'protected_pixels':int((~allowed).sum()),'candidate_rgb_sha256':hashlib.sha256(b.tobytes()).hexdigest()})
       (out/'candidate.json').write_text(json.dumps(c,indent=2)+'\n')
       compare(orig,cand,union,c['crop'],out/'comparison.png')
       print(c['emote'],c['candidate'],c['changed_pixels'])

if __name__=='__main__':main()
