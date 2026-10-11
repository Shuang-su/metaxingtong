from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
p=Path('classroom_motion_validation_20261010');q=p/'six_bay_candidate';h=Path('classroom_hd_alignment_20261010');(q/'overlays').mkdir(exist_ok=True);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17);rows=[];manifest=[]
for n in ['SOURCE_A','SOURCE_B','SOURCE_C','SOURCE_4298','SOURCE_4300','SOURCE_4310','MOTION_F_path_059','MOTION_F_path_073','MOTION_F_path_076','MOTION_F_path_080']:
 src=None
 if n in ['SOURCE_A','SOURCE_B','SOURCE_C']:
  k={'SOURCE_A':'classroom_0919_front','SOURCE_B':'classroom_2123_key','SOURCE_C':'classroom_4284_wide'}[n];old=h/'renders'/(k+'.png');src=h/'source'/(k+'_video.png')
 elif n.startswith('MOTION_'):
  k=n[7:];old=p/'renders'/(k+'.png');src=p/'source'/(k+'_video.png')
 else:old=q/'baseline_renders'/(n+'.png')
 new=q/'renders'/(n+'.png')
 if not old.exists() or not new.exists():continue
 a=Image.open(old).convert('RGB');b=Image.open(new).convert('RGB');row=Image.new('RGB',(1770,360),'#202020');d=ImageDraw.Draw(row)
 if src:
  source=Image.open(src).convert('RGB');assert source.size==b.size==(1180,664);overlay=q/'overlays'/(n+'_sixbay_direct50.png');Image.blend(source,b,.5).save(overlay);first=(source,'真实来源')
 else:first=(Image.blend(a,b,.5),'新旧直接50%叠图（无来源新增）')
 for j,(im,label) in enumerate([first,(a,'冻结十格'),(b,'六格共享候选')]):row.paste(im.resize((590,332)),(590*j,28));d.text((590*j+3,3),n+'｜'+label,font=font,fill='white')
 rows.append(row);manifest.append({'camera':n,'baseline':str(old),'candidate':str(new),'source':str(src) if src else None,'baseline_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'note':'Same1180x664; review contact sheet only downsized. Direct overlays unwarped fullsize. B camera translated with bay identity; other cameras identical. Sample counts differ for some baselines.'})
sheet=Image.new('RGB',(1770,360*len(rows)));[sheet.paste(r,(0,360*i)) for i,r in enumerate(rows)];sheet.save(q/'六格共享候选_十机位新旧对照.jpg',quality=92);(q/'qa/regression_manifest.json').write_text(json.dumps(manifest,indent=2))
