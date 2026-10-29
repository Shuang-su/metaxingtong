from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
R=Path(__file__).resolve().parents[2];P=R/'c29';out={};board=Image.new('RGB',(1240,710),'#eeeeee');draw=ImageDraw.Draw(board);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
spec=[('H','hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png',(1600,200,1820,400),300,(1638,1775)),('G','hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png',(990,200,1190,400),300,(1036,1118)),('N642','BV1GqXMByE1s_642.617525_right_turn_native.png',(1240,80,1470,280),180,(1300,1388))]
for row,(k,f,box,y,interval) in enumerate(spec):
 out[k]={}
 paths=[('source',R/'inputs'/f),('C28',R/'c28/renders'/(k+'_C28_MATERIAL_RAW_1920x1080.png')),('C29_5',P/'region_tests'/(k+'_C29_5fold_REGION_ONLY.png')),('C29_6',P/'region_tests'/(k+'_C29_6fold_REGION_ONLY.png'))]
 for col,(tag,p) in enumerate(paths):
  if not p.exists():continue
  im=Image.open(p).convert('RGB');a=np.array(im,float);x0,x1=interval;prof=gaussian_filter1d(a[y-5:y+6,x0:x1].mean((0,2)),1.5);peaks,_=find_peaks(prof,prominence=3,distance=7);xs=[int(i+x0) for i in peaks];steps=np.diff(xs)
  out[k][tag]={'photometric_ridges':xs,'spacing_sequence_px':steps.tolist(),'median_spacing_px':float(np.median(steps)) if len(steps) else None,'sample_y':y,'x_interval':interval,'method':'same fixed Gaussian sigma1.5, prominence3, min-distance7; brightness peaks are not 3D vertex correspondences'}
  crop=im.crop(box);d=ImageDraw.Draw(crop)
  for x in xs:d.line((x-box[0],y-box[1]-25,x-box[0],y-box[1]+25),fill='red',width=1)
  board.paste(crop,(col*310+10,row*230+30));draw.text((col*310+10,row*230+5),k+' '+tag+' native crop',font=font,fill='black')
(P/'region_photometric_metrics.json').write_text(json.dumps(out,indent=2));board.save(P/'C29_region_hypotheses_comparison.png');print(json.dumps(out,indent=2))
