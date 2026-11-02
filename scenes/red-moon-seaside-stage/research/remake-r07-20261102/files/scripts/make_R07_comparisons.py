from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parents[1];OUT=D/'renders/final-R07';pairs={'SOURCE_P1_45':'P1_t45.013436','SOURCE_P2_32':'P2_t32.024562','SOURCE_P1_15':'P1_t15.116586'};records=[]
for cam,suf in pairs.items():
 source=D/f'sources/BV1DZ4y1U71V_{suf}_native.png';im=Image.open(source).convert('RGB')
 for mode in['material','white']:
  r=OUT/f'R07_{cam}_{mode}.png';rend=Image.open(r).convert('RGB');assert rend.size==im.size;target=OUT/f'R07_{cam}_{mode}_DIRECT50.png';Image.blend(im,rend,.5).save(target)
  records.append({'source':str(source.relative_to(D)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'render':str(r.relative_to(D)),'render_sha256':hashlib.sha256(r.read_bytes()).hexdigest(),'direct50':str(target.relative_to(D)),'overlay_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'wh':list(im.size),'method':'direct Image.blend(sourceRGB,renderRGB,0.5) at identical native source dimensions; NO crop, translation, warp or interpolation'})
(OUT/'native-comparison-manifest.json').write_text(json.dumps(records,indent=2))
sheet=Image.new('RGB',(1600,860),'#222');draw=ImageDraw.Draw(sheet)
for i in range(8):
 im=Image.open(OUT/f'R07_CHECK_{i:02d}_material.png').convert('RGB');im.thumbnail((400,400));x,y=(i%4)*400,(i//4)*430;sheet.paste(im,(x,y+30));draw.text((x+8,y+8),f'CHECK {i:02d} / internal geometry, NOT source',fill='white')
sheet.save(OUT/'R07_EIGHT_CHECKS_display.jpg',quality=93)
for mode in['material','white']:
 sheet=Image.new('RGB',(1200,720),'#222');draw=ImageDraw.Draw(sheet)
 for i,cam in enumerate(pairs):
  im=Image.open(OUT/f'R07_{cam}_{mode}_DIRECT50.png').convert('RGB');im.thumbnail((600,338));x,y=(i%2)*600,(i//2)*360;sheet.paste(im,(x,y+22));draw.text((x+8,y+5),f'{cam} {mode} direct50 / DISPLAY RESIZE',fill='white')
 sheet.save(OUT/f'R07_three_{mode}_direct50_display.jpg',quality=93)
