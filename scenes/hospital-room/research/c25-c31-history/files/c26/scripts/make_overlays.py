from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[2];P=R/'c26/review_renders'
sources={'H':'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','G':'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png'}
d=[]
for k,n in sources.items():
 a=R/'inputs'/n;b=P/(k+'_C26_WHITE_RAW_1920x1080.png')
 x=np.array(Image.open(a).convert('RGB'));y=np.array(Image.open(b).convert('RGB'));assert x.shape==y.shape==(1080,1920,3)
 z=((x.astype('uint16')+y.astype('uint16'))//2).astype('uint8');out=P/(k+'_C26_WHITE_direct50_1920x1080.png');Image.fromarray(z).save(out);assert np.array_equal(np.array(Image.open(out)),z)
 d.append({'view':k,'source':n,'source_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'render':b.name,'render_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'overlay':out.name,'overlay_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'formula':'floor((source+render)/2)','registration_warp_resize_or_mask':False})
(P/'direct50_manifest.json').write_text(json.dumps(d,indent=2)+'\n')
