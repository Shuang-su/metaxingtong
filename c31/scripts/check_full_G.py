from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
from scipy.ndimage import gaussian_filter1d
R=Path(__file__).resolve().parents[2];P=R/'c31';f=P/'renders/G_C31_MATERIAL_RAW_1920x1080.png';a=np.asarray(Image.open(f).convert('RGB'),float).mean(2);out={'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'method':'Same source-defined columns and 5-column sigma1 gradient; signed extrema within region-observed boundary windows, not AABB projections','edges':{}}
for name,x,lo,hi,sign in [('inner_upper',1900,817,837,1),('inner_lower',1900,886,906,-1),('hole_upper',1700,814,834,-1),('hole_lower',1700,880,900,1)]:
 g=np.gradient(gaussian_filter1d(a[:,x-2:x+3].mean(1),1));y=int(lo+np.argmax(sign*g[lo:hi]));out['edges'][name]={'x':x,'y':y,'signed_gradient':float(g[y]),'search_interval':[lo,hi]}
(P/'full_G_pixel_check.json').write_text(json.dumps(out,indent=2));print(out)
