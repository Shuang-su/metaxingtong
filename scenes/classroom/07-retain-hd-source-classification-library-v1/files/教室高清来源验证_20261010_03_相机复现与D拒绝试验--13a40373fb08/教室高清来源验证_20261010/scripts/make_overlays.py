from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib,shutil
fontcn=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
titles={'classroom_0919_front':'A 正面 919.323秒','classroom_2123_key':'B 窗侧 2123.125秒','classroom_4284_wide':'C 广角 4284.478秒','classroom_5447_key':'D 斜向 5447.186秒','classroom_motion_4282':'E 近正面 4282.104秒'}
p=Path('classroom_hd_alignment_20261010');src=Path('xingtong_classroom_browser/hd_recapture');man=json.load(open(src/'manifest.json'));rows=[];links=[]
for m in man:
 n=m['name'];s=src/m['crop_filename'];r=p/'renders'/f'{n}.png';im=Image.open(s).convert('RGB');rr=Image.open(r).convert('RGB');assert im.size==rr.size==(1180,664);assert hashlib.sha256(s.read_bytes()).hexdigest()==m['crop_sha256'];shutil.copy2(s,p/'source'/s.name)
 ov=Image.blend(im,rr,.5);ov.save(p/'overlays'/f'{n}_50percent.png');row=Image.new('RGB',(1770,356),'#202020');d=ImageDraw.Draw(row)
 for j,(a,label) in enumerate([(im,'新高清来源'),(rr,'固定共享模型'),(ov,'直接50%叠图')]):row.paste(a.resize((590,332)),(j*590,24));d.text((j*590+8,5),titles[n]+'｜'+label,fill='white',font=fontcn)
 rows.append(row);links.append({'name':n,'time':m['capture_time_bracket_seconds'],'source_url':m['source_url'],'source_sha256':m['crop_sha256'],'render':str(r),'render_sha256':hashlib.sha256(r.read_bytes()).hexdigest(),'overlay':str(p/'overlays'/f'{n}_50percent.png'),'operation':'PIL.Image.blend(unmodified native1180x664 reference, same-resolution render,0.5); no crop, resize, perspective warp or alignment applied'})
sheet=Image.new('RGB',(1770,len(rows)*356));[sheet.paste(row,(0,i*356)) for i,row in enumerate(rows)];sheet.save(p/'五张高清补帧_直接叠图总览.jpg',quality=94);(p/'qa/overlay_provenance.json').write_text(json.dumps(links,ensure_ascii=False,indent=2));shutil.copy2(src/'manifest.json',p/'source/capture_manifest.json')
# Source-only count annotation uses observed wood/apron segments, no row or cross-view identity assumption.
segments=[((5,328),(148,328)),((65,353),(197,353)),((115,396),(252,395)),((5,638),(247,585)),((267,335),(378,337)),((369,362),(488,365)),((256,477),(559,491)),((544,637),(617,627)),((538,341),(624,343)),((658,417),(780,420)),((839,350),(962,351)),((782,378),(906,380)),((1010,424),(1068,430)),((865,505),(940,515))]
im=Image.open(src/'crops/classroom_5447_key_video.png').convert('RGB');d=ImageDraw.Draw(im)
for i,(a,b) in enumerate(segments,1):d.line([a,b],fill='#00ff30',width=3);d.text((a[0]+3,a[1]-15),f'D{i:02}',fill='#ffff00',font=fontcn)
d.text((5,8),'至少14个独立木面/围板；不强行对应桌行；右侧不确定碎片未计入',fill='yellow',font=fontcn);im.save(p/'qa/D_new_source_14_units.png');(p/'qa/D_new_source_14_units.json').write_text(json.dumps({'segments':segments,'count_lower_bound':14,'excluded':'Far right sliver D15? remains uncertain; not counted. Player overlay masks parts of foreground D04/D08; wood surface/apron remains visible.','cross_view_identity':'Not assumed.'},indent=2))
