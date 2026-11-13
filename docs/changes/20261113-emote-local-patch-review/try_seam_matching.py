#!/usr/bin/env python3
"""Third local trial: cloth donor gradients with boundary-matched colors.

Poisson blending here is local deterministic pixel processing, not generation.
Source anatomy, motion, face, silhouette, and all pixels outside masks are fixed.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
import json,hashlib
from try_local_candidates import ROOT,mask_polygon,compare

def poisson(original,donor,mask):
    a=np.array(original,dtype=float);allowed=np.array(mask)>0
    ys,xs=np.nonzero(allowed);N=len(xs);index=np.full(allowed.shape,-1,dtype=int);index[ys,xs]=np.arange(N)
    matrix=lil_matrix((N,N));b=np.zeros((N,3));matrix.setdiag(4)
    for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
        yn,xn=ys+dy,xs+dx
        b+=donor[ys,xs]-donor[yn,xn]
        neighbor=index[yn,xn];inside=neighbor>=0
        rows=np.nonzero(inside)[0];matrix[rows,neighbor[inside]]=-1
        b[~inside]+=a[yn[~inside],xn[~inside]]
    solved=spsolve(matrix.tocsr(),b)
    result=a.copy();result[ys,xs]=solved
    return Image.fromarray(np.rint(result).clip(0,255).astype('uint8'))

def main():
    yy,xx=np.indices((768,768),dtype=float)
    for n in [24,25,26,27,28]:
        parent=ROOT/'emotes/sunburst/agent-emotes/02-butterfly/versions/20261113-local-patch-review'
        out=parent/'v3-seam-matching'/f'{n:02d}';out.mkdir(parents=True,exist_ok=False)
        orig=Image.open(parent/'original-decoded'/f'{n:02d}.png').convert('RGB');a=np.array(orig)
        # Extend only through the damaged right skirt detail; stop under the actual palm.
        poly=[[572,475],[594,475],[614,482],[627,491],[638,504],[634,516],
              [644,527],[655,532],[671,532],[678,540],[670,550],[653,555],
              [636,550],[627,550],[605,554],[589,544],[577,524],[570,500]]
        mask=mask_polygon(orig.size,poly)
        sx=540+(xx-570)*.18;sy=yy+(xx-580)*.14
        donor=np.stack([map_coordinates(a[:,:,c].astype(float),[sy,sx],order=1,mode='nearest') for c in range(3)],-1)
        cand=poisson(orig,donor,mask)
        cand.save(out/'candidate.png');mask.save(out/'allowed-mask.png')
        b=np.array(cand);allowed=np.array(mask)>0;changed=np.any(a!=b,axis=-1)
        assert not np.any(changed&~allowed)
        (out/'candidate.json').write_text(json.dumps({'frame':n,'status':'requires_visual_review',
            'method':'same-frame affine cloth gradients; sparse Poisson boundary matching',
            'donor_mapping':'sx=540+0.18*(x-570); sy=y+0.14*(x-580)',
            'polygon':poly,'changed_pixels':int(changed.sum()),'pixels_changed_outside_mask':0,
            'protected_pixels':int((~allowed).sum()),'original_rgb_sha256':hashlib.sha256(a.tobytes()).hexdigest(),
            'candidate_rgb_sha256':hashlib.sha256(b.tobytes()).hexdigest()},indent=2)+'\n')
        compare(orig,cand,mask,[550,465,695,565],out/'comparison.png')

if __name__=='__main__':main()
