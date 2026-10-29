from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
R=Path(__file__).resolve().parents[2];P=R/'c30b';names={'G':'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','N642':'BV1GqXMByE1s_642.617525_right_turn_native.png','H':'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','665':'BV1GqXMByE1s_665.501733_downward_native.png'}
b=Image.new('RGB',(1440,1370),'white');d=ImageDraw.Draw(b);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);d.text((12,10),'C30B conditional bed deck: actual fixed-camera region renders, shown at 50% size',fill='black',font=font)
for i,k in enumerate(['G','N642','H','665']):
 box=[1000,650,1920,1080] if k in ['G','N642'] else [1250,750,1920,1080] if k=='H' else [1200,500,1920,1080];src=Image.open(R/'inputs'/names[k]).convert('RGB');old=Image.open(P/'region_tests/665_C29_REGION_ONLY.png' if k=='665' else R/'c29/renders'/(k+'_C29_MATERIAL_RAW_1920x1080.png')).convert('RGB');new=Image.open(P/'region_tests'/(k+'_C30B_REGION_ONLY.png')).convert('RGB');y=55+i*310
 for j,(lab,im) in enumerate([('Native reference',src),('Before C29',old),('After C30B conditional',new)]):
  d.text((12+j*480,y),k+' '+lab,fill='black',font=font);crop=im.crop(box);crop=crop.resize((crop.width//2,crop.height//2));b.paste(crop,(12+j*480,y+25))
d.text((12,1340),'Conservative lower rise avoids prior recess cutoff; visible bed edge still substantially too low.',fill='black',font=font);b.save(P/'C30B_four_view_region_comparison.png')
