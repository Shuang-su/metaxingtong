from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
p=Path('classroom_motion_validation_20261010');font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17);fits=json.load(open(p/'qa/camera_only_fits.json'));rows=[];manifest=[]
for f in fits:
 n=f['name'];src=p/'source'/(n+'_video.png');ren=p/'renders'/(n+'.png')
 if not ren.exists():continue
 a=Image.open(src).convert('RGB');b=Image.open(ren).convert('RGB');assert a.size==b.size==(1180,664);ov=Image.blend(a,b,.5);ov.save(p/'overlays'/(n+'_50percent.png'));row=Image.new('RGB',(1770,360),'#202020');d=ImageDraw.Draw(row)
 for j,(im,label) in enumerate([(a,'新增实际播放帧'),(b,'固定模型，相机匹配'),(ov,'直接50%叠图')]):row.paste(im.resize((590,332)),(590*j,28));d.text((590*j+5,3),n+'｜'+label,font=font,fill='white')
 rows.append(row);manifest.append({'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'render':str(ren),'render_sha256':hashlib.sha256(ren.read_bytes()).hexdigest(),'overlay':str(p/'overlays'/(n+'_50percent.png')),'operation':'Exact1180x664 direct50% blend; no resize/warp/registration applied to individual overlay.'})
 diag=a.copy();dr=ImageDraw.Draw(diag)
 for q in f['points']:
  x,y=q['source_px'];u,v=q['projected_px'];color='cyan' if q['role']=='fit' else 'lime';dr.ellipse((x-4,y-4,x+4,y+4),outline=color,width=2);dr.line((x,y,u,v),fill='yellow',width=2);dr.ellipse((u-4,v-4,u+4,v+4),outline='red',width=2)
 dr.text((6,5),f"青色拟合/绿色保留点，红色模型：RMS {f['fit_rms_px']:.2f}/{f['holdout_rms_px']:.2f}px",font=font,fill='yellow',stroke_width=1,stroke_fill='black');diag.save(p/'qa'/(n+'_anchors.png'))
if rows:
 sheet=Image.new('RGB',(1770,len(rows)*360));[sheet.paste(r,(0,i*360)) for i,r in enumerate(rows)];sheet.save(p/'正片连续来源追加验证_四帧直接叠图.jpg',quality=94)
(p/'qa/overlay_provenance.json').write_text(json.dumps(manifest,indent=2))
