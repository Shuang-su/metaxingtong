from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib,zipfile,shutil,os
R=Path('/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom');F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(sz):return ImageFont.truetype(F,sz)
def sheet(files,out,cols=3,thumb=(480,360),title='完整几何检查'):
 rows=(len(files)+cols-1)//cols;im=Image.new('RGB',(cols*thumb[0],70+rows*(thumb[1]+42)), '#1c2530');d=ImageDraw.Draw(im);d.text((20,15),title,font=font(25),fill='white')
 for i,p in enumerate(files):
  src=Image.open(p).convert('RGB');src.thumbnail(thumb);x=(i%cols)*thumb[0];y=70+(i//cols)*(thumb[1]+42);im.paste(src,(x,y));d.text((x+8,y+thumb[1]+5),p.stem,font=font(18),fill='white')
 im.save(out,quality=90)
files=sorted(R.joinpath('renders').glob('[0-9]*材质.png'))+list(R.joinpath('renders').glob('11_*.png'))
sheet(files,R/'qa/检查视角总览.jpg',title='海边吧台：统一几何的普通检查视角与诊断剖切')
rows=[]
for typ,stem in [('A','bar_22min_before'),('B','bar_22min_later_static')]:
 src=Image.open('/workspace/scratch/fa58bfcf0425/bar_room_source/verified_collection/'+stem+'_exact_crop.png').convert('RGB')
 for variant in ['材质','白模']:
  render=Image.open(R/'renders'/('源图_'+typ+'_透视近似_'+variant+'.png')).convert('RGB');assert render.size==src.size
  overlay=Image.blend(src,render,.5);overlay.save(R/'qa'/('源图_'+typ+'_'+variant+'_50%直接叠图.png'))
  pane=Image.new('RGB',(1180*3,730),'#1c2530');pane.paste(src,(0,55));pane.paste(render,(1180,55));pane.paste(overlay,(2360,55));d=ImageDraw.Draw(pane)
  for i,label in enumerate(['源图：未缩放1180×663','统一模型：'+variant,'50%直接叠图：无图像形变']):d.text((i*1180+15,10),typ+' / '+label,font=font(28),fill='white')
  pane.save(R/'qa'/('源图_'+typ+'_'+variant+'_三联对比.jpg'),quality=92);rows.append(R/'qa'/('源图_'+typ+'_'+variant+'_三联对比.jpg'))
sheet(rows,R/'qa/A_B_材质白模对比总览.jpg',cols=1,thumb=(1770,365),title='A/B独立静态源图；相机近似，布置变化不伪装成多角度约束')
