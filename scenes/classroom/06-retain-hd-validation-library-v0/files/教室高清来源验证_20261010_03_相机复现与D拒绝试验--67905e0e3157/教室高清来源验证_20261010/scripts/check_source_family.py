from PIL import Image
import json,numpy as np
from scipy.signal import correlate2d
from pathlib import Path
p=Path('classroom_hd_alignment_20261010');s=Path('xingtong_classroom_browser/hd_recapture/crops');checks=json.load(open(p/'qa/new_source_anchor_errors.json'));bycam={c['camera']['name'][-1]:c for c in checks}
rows=[('classroom_0919_front','02_其他角度对照.jpg',(12,75,492,345),'A'),('classroom_2123_key','02_其他角度对照.jpg',(12,390,492,660),'B'),('classroom_4284_wide','01_主要角度对照.jpg',(12,97,492,367),'C'),('classroom_5447_key','01_主要角度对照.jpg',(12,412,492,682),'D')];out=[]
for n,f,box,c in rows:
 old=np.array(Image.open('classroom_fullroom/input/baseline/'+f).crop(box).resize((1180,664)).convert('L'),dtype=float);new=np.array(Image.open(s/(n+'_video.png')).convert('L'),dtype=float);records=[]
 for a in bycam[c]['points']:
  x,y=a['source_px'];half=20;search=12
  if not(32<x<1148 and 32<y<632):continue
  t=old[y-half:y+half,x-half:x+half];big=new[y-half-search:y+half+search,x-half-search:x+half+search];t=t-t.mean();ones=np.ones(t.shape);su=correlate2d(big,ones,mode='valid');sq=correlate2d(big**2,ones,mode='valid');numer=correlate2d(big,t,mode='valid');den=np.sqrt(np.maximum(sq-su**2/t.size,1e-6)*(t*t).sum());score=numer/den;iy,ix=np.unravel_index(score.argmax(),score.shape);records.append({'label':a['label'],'offset_px':[int(ix-search),int(iy-search)],'normalized_correlation':float(score[iy,ix])})
 out.append({'new':n,'old_camera':c,'old_contact_sheet':f,'old_panel_box':box,'method':'Only crop old contact-sheet source panel and resize for diagnostic template matching; no modification to delivered source or render. ±12 px NCC search on static architectural patches.','patches':records})
(p/'qa/source_family.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
