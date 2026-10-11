from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];V=R/'review_r03';den=V/'denoised';F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22);sm=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17);rows=[]
def pair(k,source,render,scale=1,status='来源匹配候选，仍有残差'):
 if not render.exists():return
 ren=Image.open(render).convert('RGB');ref=Image.open(source).convert('RGB')
 if ref.size!=ren.size:ref=ref.resize(ren.size,Image.Resampling.LANCZOS)
 overlay=Image.blend(ref,ren,.5);overlay.save(V/f'{k}_overlay_50percent.png');w,h=ren.size;cv=Image.new('RGB',(w*3,h+78),(24,26,29));d=ImageDraw.Draw(cv)
 for i,(im,t) in enumerate([(ref,'来源'),(ren,'冻结共享模型'),(overlay,'直接50%叠图，无warp')]):cv.paste(im,(i*w,50));d.text((i*w+10,27),t,font=sm,fill='white')
 d.text((10,3),k+' | '+status,font=F,fill='white');d.text((10,h+53),'人物/水印不建模；透视、遮挡、轮廓残差未掩盖',font=sm,fill=(210,210,210));cv.save(V/f'{k}_comparison.jpg',quality=92,subsampling=0)
 rows.append({'view':k,'source':str(source.relative_to(R)),'render':str(render.relative_to(R)),'source_uniform_scale':scale,'render_pixels':list(ren.size),'operation':'direct 0.5 RGB blend on same-sized images; no warp','status':status,'overlay_sha256':hashlib.sha256((V/f'{k}_overlay_50percent.png').read_bytes()).hexdigest()})
for k in ['A','B','D']:pair('HD_'+k,R/'references'/f'{k}_content.png',den/f'material_HD_{k}_100.png')
for k in ['F','H','I','J']:
 status='结构诊断，相机/全场残差未解'
 if k=='F':status+='；来源为表演灯态，本模型固定暖光'
 pair('HD_'+k,R/'references'/f'{k}_content.png',den/f'material_HD_{k}_50.png',.5,status)
for k,ref,cam in [('A','train_015_918.jpg','MATCH_A_15m19_right_booth'),('B','train_2711.jpg','MATCH_B_45m12_left_booth'),('D','train_838.jpg','MATCH_D_13m59_wide')]:
 src=R/'references'/f'legacy_{k}_content.png';Image.open(R.parent/'xingtong_train/original/review/references'/ref).crop((0,26,1188,694)).save(src);pair('legacy_'+k,src,den/f'material_{cam}_50.png',.5,'旧来源/原相机回归；共享几何、材质及固定暖光已改变')
for kind in ['material','white']:
 p=den/f'{kind}_INSPECT_01_forward_aisle_100.png'
 if p.exists():shutil.copy2(p,V/f'normal_main_{kind}.png')
(V/'comparison_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('REVIEWS',len(rows))
