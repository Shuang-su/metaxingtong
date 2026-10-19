from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
r=Path(__file__).resolve().parents[1];p=r/'inputs/BV1GqXMByE1s_665.501733_downward_native.png';im=Image.open(p).convert('RGB');a=np.asarray(im,float);x0,x1=1725,1860;y=250
v=gaussian_filter1d(a[y-5:y+6,x0:x1].mean((0,2)),1.5);pk,_=find_peaks(v,prominence=3,distance=7);xs=(pk+x0).tolist();steps=np.diff(xs).tolist()
data={'source':str(p.relative_to(r)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_dimensions':list(im.size),'view':'665.501733 downward native','role':'post-freeze source observation only; not used to select or fit C29 parameters','fixed_roi':{'x_half_open':[x0,x1],'y_inclusive':[245,255],'sample_y':250},'algorithm':{'channel_reduction':'arithmetic mean of RGB then mean of 11 image rows','gaussian_sigma_px':1.5,'find_peaks_prominence':3,'find_peaks_min_distance_px':7},'photometric_ridges_x':xs,'spacing_sequence_px':steps,'median_spacing_px':float(np.median(steps)),'visibility':'ROI is above sofa and to right of person, with no visible person/bed/sofa occlusion; interior only, excludes left column-side transition and right broad terminal return face. Curtain top and bottom are out of this ROI.','limitations':['brightness maxima are not certified 3D fold-vertex correspondences','only one horizontal strip and one fixed view','no scale, camera or total fold-count calibration','no fitting or parameter updates allowed from this check'],'predeclared_window_sensitivity_check':{'x_half_open':[1710,1875],'result':'same four peak coordinates; inspection only, not used to choose a more favorable candidate result'}}
(r/'c29_diagnosis/665_source_observation.json').write_text(json.dumps(data,indent=2))
box=(1680,180,1910,330);crop=im.crop(box);d=ImageDraw.Draw(crop);d.rectangle((x0-box[0],245-box[1],x1-1-box[0],255-box[1]),outline='cyan',width=1)
for i,x in enumerate(xs):
 d.line((x-box[0],225-box[1],x-box[0],280-box[1]),fill='red',width=1);d.text((x-box[0]-12,200-box[1]),str(x),fill='yellow')
crop.save(r/'c29_diagnosis/665_source_annotated_1x.png');print(data)
