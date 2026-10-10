from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];P=R.parent
shutil.copy2(P/'castle_hall_fullroom/source_supplements/20261010_transition/hall_empty_boundary_1729_core.png',R/'references/hall_empty_boundary_1729_core.png')
shutil.copy2(P/'castle_hall_fullroom/source_supplements/20261010_transition/hall_empty_boundary_1729.json',R/'references/hall_empty_boundary_1729.json')
# Contact sheet only; not an alignment overlay.
files=[R/'references/hall_empty_boundary_1729_core.png',R/'references/hall_A_2712_paused_core.png',P/'castle_hall_fullroom/restored/references/Match_C_crop.png',P/'castle_hall_fullroom/renders/FullRoom_Match_A_clean.png']
labels=['NEW HD 1729.566778 | empty hall | no warp','NEW HD 2712.991552 | old A neighbourhood','OLD C 4424 approx | low-detail | occluded','UNCHANGED BASELINE A | approximate old camera']
im=Image.new('RGB',(1180*2,704*2),(20,25,30));d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
for i,(p,l) in enumerate(zip(files,labels)):
 x=i%2*1180;y=i//2*704;pic=Image.open(p).convert('RGB');pic.thumbnail((1180,664));im.paste(pic,(x,y+40));d.text((x+12,y+8),l,font=font,fill='white')
im.save(R/'qa/initial_coverage_contact.jpg',quality=93)
