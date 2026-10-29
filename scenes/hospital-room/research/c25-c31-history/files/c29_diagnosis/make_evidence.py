from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
r=Path(__file__).resolve().parents[1];d=r/'c29_diagnosis'
views=[('H','hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png',(1600,250,1800,350),300,(1638,1775)),('G','hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png',(1000,250,1170,350),300,(1036,1118)),('N642','BV1GqXMByE1s_642.617525_right_turn_native.png',(1260,130,1435,230),180,(1300,1388))]
board=Image.new('RGB',(800,700),'#efefef');draw=ImageDraw.Draw(board);stats={}
for row,(k,stem,box,y,interval) in enumerate(views):
 stats[k]={}
 for col,(typ,p) in enumerate([('source',r/'inputs'/stem),('C28',r/f'c28/renders/{k}_C28_MATERIAL_RAW_1920x1080.png')]):
  im=Image.open(p);a=np.asarray(im).astype(float);x0,x1=interval
  v=gaussian_filter1d(a[y-5:y+6,x0:x1].mean((0,2)),1.5);pk,_=find_peaks(v,prominence=3,distance=7);xs=[int(i+x0) for i in pk];steps=np.diff(xs)
  stats[k][typ]={'sample_y':y,'x_interval':interval,'photometric_ridge_maxima_x':xs,'median_interior_spacing_px':float(np.median(steps))}
  crop=im.crop(box);dd=ImageDraw.Draw(crop)
  for x in xs:
   dd.line((x-box[0],20,x-box[0],80),fill='#ff3156',width=1);dd.text((x-box[0]-9,4),str(x),fill='yellow')
  board.paste(crop,(col*400,row*190+30));draw.text((col*400,row*190+10),f'{k} {typ}, 1:1 pixels; y={y} +/-5',fill='black')
# Separate top contour evidence, source pixel labels. Five visible pleat tips, not a guaranteed global count.
for k,stem,box,points in [('G','inputs/hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png',(990,0,1180,130),[(1015,76),(1035,65),(1055,57),(1078,43),(1098,31)]),('1801','c26/new_evidence/frame_1801.323.png',(100,30,290,150),[(122,76),(149,71),(176,69),(204,64),(231,59)])]:
 im=Image.open(r/stem).crop(box);dd=ImageDraw.Draw(im)
 for i,(x,y) in enumerate(points,1):
  xx,yy=x-box[0],y-box[1];dd.ellipse((xx-3,yy-3,xx+3,yy+3),outline='yellow',width=1);dd.text((xx-5,yy+8),str(i),fill='yellow')
 im.save(d/f'{k}_top_tips_annotated_1x.png')
 stats[k+'_top']={'visible_tip_xy_approx':points,'uncertainty_px':3,'interpretation':'five visible front-fold tips; right closure face and partially hidden back returns are not extra counted folds; total hidden pleat count not established'}
board.save(d/'H_G_N642_ridge_spacing_1x.png');(d/'pixel_evidence.json').write_text(json.dumps(stats,indent=2))
