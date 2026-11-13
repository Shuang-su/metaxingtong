#!/usr/bin/env python3
"""Fourth trial: clean neighboring original garment patches, no frame replacement."""
from pathlib import Path
from PIL import Image
from scipy.ndimage import distance_transform_edt
import numpy as np,json
from try_local_candidates import ROOT,mask_polygon,compare

parent=ROOT/'emotes/sunburst/agent-emotes/02-butterfly/versions/20261113-local-patch-review'
orig=Image.open(parent/'original-decoded/27.png').convert('RGB')
poly=[[580,492],[598,485],[618,489],[635,503],[634,516],[644,528],[638,542],[628,550],[606,553],[590,540],[580,522]]
mask=mask_polygon(orig.size,poly);allowed=np.array(mask)>0
alpha=np.minimum(distance_transform_edt(allowed)/3,1)*allowed
for n in [23,29]:
    donor=Image.open(parent/'original-decoded'/f'{n:02d}.png').convert('RGB')
    out=parent/f'v4-neighbor-donor-{n}';out.mkdir(exist_ok=False)
    # Same fixed-camera pixel coordinates; do not move heads, hands, or silhouettes.
    a=np.array(orig);d=np.array(donor)
    b=np.rint(a*(1-alpha[:,:,None])+d*alpha[:,:,None]).astype('uint8')
    cand=Image.fromarray(b);cand.save(out/'candidate.png');mask.save(out/'allowed-mask.png')
    assert np.array_equal(a[~allowed],b[~allowed])
    (out/'candidate.json').write_text(json.dumps({'frame':27,'donor_frame':n,
        'status':'requires_visual_review','method':'same-coordinate original-frame garment patch',
        'polygon':poly,'changed_pixels':int(np.any(a!=b,axis=-1).sum()),'pixels_changed_outside_mask':0},indent=2)+'\n')
    compare(orig,cand,mask,[550,465,680,565],out/'comparison.png')
