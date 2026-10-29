from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
R=Path(__file__).resolve().parents[2];P=R/'c29';spec=[('H','hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png',300,(1638,1775)),('G','hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png',300,(1036,1118)),('N642','BV1GqXMByE1s_642.617525_right_turn_native.png',180,(1300,1388))];out={}
for k,f,y,interval in spec:
 out[k]={}
 for tag,path in [('source',R/'inputs'/f),('C28',R/'c28/renders'/(k+'_C28_MATERIAL_RAW_1920x1080.png')),('C29',P/'renders'/(k+'_C29_MATERIAL_RAW_1920x1080.png'))]:
  if not path.exists():continue
  a=np.array(Image.open(path).convert('RGB'),float);x0,x1=interval;v=gaussian_filter1d(a[y-5:y+6,x0:x1].mean((0,2)),1.5);p,_=find_peaks(v,prominence=3,distance=7);xs=(p+x0).tolist();d=np.diff(xs).tolist();out[k][tag]={'file':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sample_y':y,'interval':interval,'peaks_x':xs,'spacing_px':d,'median_spacing_px':float(np.median(d)),'scope':'photometric internal fold frequency, not calibrated 3D feature correspondences'}
(P/'final_photometric_metrics.json').write_text(json.dumps(out,indent=2));print({k:{t:v['median_spacing_px'] for t,v in a.items()} for k,a in out.items()})
