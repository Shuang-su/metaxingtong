from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
R=Path(__file__).resolve().parents[2];P=R/'c29';out={'frozen_roi':[1725,245,1860,256],'method':'mean RGB and 11 rows; Gaussian sigma1.5; prominence3; distance7','scope':'Previously viewed 665, excluded from current candidate selection; no parameter refitting','results':{}};board=Image.new('RGB',(900,630),'white');d=ImageDraw.Draw(board)
for i,(tag,f) in enumerate([('source',R/'inputs/BV1GqXMByE1s_665.501733_downward_native.png'),('C28',P/'validation665/665_C28_REGION_ONLY.png'),('C29',P/'validation665/665_C29_REGION_ONLY.png')]):
 im=Image.open(f).convert('RGB');a=np.asarray(im,float);v=gaussian_filter1d(a[245:256,1725:1860].mean((0,2)),1.5);pk,_=find_peaks(v,prominence=3,distance=7);xs=(pk+1725).tolist();g=np.diff(xs).tolist();out['results'][tag]={'file':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'peaks_x':xs,'gaps_px':g,'median_gap_px':float(np.median(g))};board.paste(im.crop((1640,0,1920,560)),(i*300+10,35));d.text((i*300+10,10),tag,fill='black');d.line((i*300+95,285,i*300+230,285),fill='red',width=1)
ref=out['results']['source']['median_gap_px']
for k in ['C28','C29']:out['results'][k]['absolute_median_gap_error_px']=abs(out['results'][k]['median_gap_px']-ref)
d.text((10,605),'Fixed ROI red line; 665 was not used for current curtain selection. Region renders only.',fill='black');board.save(P/'C29_665_frozen_parameter_check.png');(P/'validation665_metrics.json').write_text(json.dumps(out,indent=2));print(out)
