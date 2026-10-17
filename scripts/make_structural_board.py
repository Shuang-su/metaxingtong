from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'v2b/review_renders';board=Image.new('RGB',(2200,750),'white');d=ImageDraw.Draw(board);font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';F=ImageFont.truetype(font,20);S=ImageFont.truetype(font,16)
d.text((20,12),'C25 structural comparison: visible side-band change, source acceptance still incomplete',font=F,fill=(135,20,20));d.text((20,45),'H: native1:1 crops. Same full scene, fixed camera, unchanged lighting/materials. No warps.',font=S,fill='black')
box=(380,830,920,1080);paths=[R/'inputs/hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png',R/'inputs/H_C23_RAW_1920x1080.png',R/'v1/review_renders/H_C25_RAW_1920x1080.png',O/'H_C25_RAW_1920x1080.png'];labels=['H native source','C23: inherited slab, conditional','C25 v1: capped upper sweep, unaccepted','C25 v2b: convex ribbon, unaccepted']
for i,(p,label) in enumerate(zip(paths,labels)):
 x=20+545*i;d.text((x,83),label,font=S,fill='black');board.paste(Image.open(p).convert('RGB').crop(box),(x,110))
d.text((20,390),'Additional native source crops below: semantic comparison ONLY. Different uncalibrated cameras and times.',font=F,fill=(135,20,20));d.text((20,420),'No matched-camera overlay is claimed for 650 / 658 / 1103. 1103 is not the H1101 frame.',font=S,fill='black')
for i,name in enumerate(['650','658','1103']):
 x=20+i*600;p=R/'source_review'/(name+'_native_crop.png');d.text((x,458),name+' source, native1:1 pixels',font=S,fill='black');board.paste(Image.open(p).convert('RGB'),(x,486))
board.save(O/'C25_structural_H_and_new_sources.png');json.dump({'matched_H_crop':box,'H_files':[str(p) for p in paths],'additional_sources':['650','658','1103'],'source_camera_alignment_claimed':False,'resampling':False,'sha256':hashlib.sha256((O/'C25_structural_H_and_new_sources.png').read_bytes()).hexdigest()},open(O/'structural_board_manifest.json','w'),indent=2)
