from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from scipy.ndimage import gaussian_filter1d
R=Path(__file__).resolve().parents[1];D=R/'c30_diagnosis'
specs=[('H','hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png',(1350,980,1920,1080),[(1500,1045,1080),(1700,1010,1060),(1850,990,1040)],4),('665','BV1GqXMByE1s_665.501733_downward_native.png',(1150,740,1920,1050),[(1300,890,930),(1600,820,865),(1850,765,805)],3)]
out={'role':'Frozen original-image observations for posterior check only of predetermined +0.1354234 model-unit height trial; never use for fitting or candidate selection','frozen_at_utc':'2026-10-19T12:29:00Z','identity':'visible bedding/sheet outer contour, not certified bare-mattress mechanical edge','candidate_images_seen':False,'views':{}}
for k,f,box,windows,unc in specs:
 p=R/'inputs'/f;im=Image.open(p).convert('RGB');a=np.asarray(im,float);crop=im.crop(box);draw=ImageDraw.Draw(crop);points=[]
 for x,lo,hi in windows:
  profile=gaussian_filter1d(a[lo:hi,x-1:x+2].mean((1,2)),1);y=int(lo+np.argmax(np.diff(profile)));points.append({'pixel_xy':[x,y],'uncertainty_y_px':unc,'uncertainty_x_px':1,'vertical_search_half_open':[lo,hi]});xx=x-box[0];yy=y-box[1];draw.ellipse((xx-3,yy-3,xx+3,yy+3),outline='red',width=1);draw.line((xx,yy-unc,xx,yy+unc),fill='cyan',width=1);draw.text((xx-28,min(yy+9,crop.height-13)),f'{x},{y}',fill='red')
 crop.save(D/f'{k}_frozen_bedding_edge_native1x.png');out['views'][k]={'source':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'native_dimensions':list(im.size),'crop_xyxy':box,'points':points,'visibility':'all selected points are clear of people, source edge is a cloth silhouette with small nonrigid contour variations; source-only manual ROI inspection followed by maximum positive vertical gradient','edge_locator':'3-pixel horizontal RGB mean, vertical Gaussian sigma1, max positive difference within preselected window','limitations':'source contour may be sheet overhang; H has a narrow visible strip; 665 center-left is person-occluded but selected right side is clear'}
(D/'H_665_frozen_source_observations.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
