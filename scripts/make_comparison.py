from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,sys
R=Path(__file__).resolve().parents[1];variant=sys.argv[1];O=R/variant/'review_renders'
sources={'H':'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','G':'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','665':'BV1GqXMByE1s_665.501733_downward_native.png'}
D=[]
for k,n in sources.items():
 a=R/'inputs'/n;b=O/(k+'_C25_RAW_1920x1080.png');s=np.array(Image.open(a).convert('RGB'));v=np.array(Image.open(b).convert('RGB'));assert s.shape==v.shape==(1080,1920,3);q=((s.astype('uint16')+v.astype('uint16'))//2).astype('uint8');out=O/(k+'_C25_direct50_1920x1080.png');Image.fromarray(q).save(out);assert np.array_equal(np.array(Image.open(out)),q);D.append({'view':k,'source':n,'source_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'direct50':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'equation':'floor((native source RGB + actual full-scene RAW RGB)/2)','no_registration_resize_warp_mask_or_visibility_override':True})
json.dump(D,open(O/'direct50_manifest.json','w'),indent=2)
# Native1:1 crops only, no resampling. Source / frozenC23 / C25 / direct50.
board=Image.new('RGB',(2200,1120),'white');dr=ImageDraw.Draw(board);font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';F=ImageFont.truetype(font,18);S=ImageFont.truetype(font,15)
dr.text((20,12),'C25 '+variant+': structural hypothesis, NOT ACCEPTED. C23 remains conditional.',font=F,fill=(150,20,20));dr.text((20,42),'Native1:1 crops | same complete scene + fixed H/G/665 cameras | no warp or per-view hiding',font=S,fill='black')
boxes={'H':(380,830,920,1080),'G':(0,940,200,1080),'665':(260,550,520,980)};ys={'H':100,'G':430,'665':650}
for k,box in boxes.items():
 y=ys[k];dr.text((20,y-28),k+' native crop '+str(box),font=S,fill='black')
 base=R/'inputs'/(k+'_C23_RAW_1920x1080.png') if k=='H' else R/'inputs/review_renders'/(k+'_C23_RAW_1920x1080.png')
 paths=[R/'inputs'/sources[k],base,O/(k+'_C25_RAW_1920x1080.png'),O/(k+'_C25_direct50_1920x1080.png')]
 for i,(label,p) in enumerate(zip(['Native source','C23 baseline: conditional','C25 '+variant+': unaccepted','C25 direct50'],paths)):
  x=20+i*545;dr.text((x,y),label,font=S,fill='black');board.paste(Image.open(p).convert('RGB').crop(box),(x,y+26))
board.save(O/'C25_native_before_after_sheet.png');json.dump({'crops':boxes,'scale':1,'resampled':False,'label':variant},open(O/'comparison_manifest.json','w'),indent=2)
