from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib,zipfile
R=Path('/workspace/scratch/fa58bfcf0425/dark_cell_v1');F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(n):return ImageFont.truetype(F,n)
def panel(ims,labels,out):
 w=1180;h=710;dst=Image.new('RGB',(w*2,h*((len(ims)+1)//2)),(24,28,34));d=ImageDraw.Draw(dst)
 for i,(im,label) in enumerate(zip(ims,labels)):
  x=(i%2)*w;y=(i//2)*h;d.text((x+14,y+8),label,font=font(22),fill='white');dst.paste(im,(x,y+46))
 dst.save(out,quality=91)
for frame,stem,view in [('932','bars_932s52','01_来源932正面'),('3626','bars_reverse_3626s48','13_3626关系未证实')]:
 src=Image.open(R/'references'/f'{stem}_crop.png').convert('RGB');mat=Image.open(R/'renders'/f'{view}_textured_clean.png').convert('RGB');white=Image.open(R/'renders'/f'{view}_white_clean.png').convert('RGB');assert src.size==mat.size==white.size==(1180,664)
 overlay=Image.blend(src,mat,.5);overlay.save(R/'qa'/f'{frame}秒_50%直接叠图.png');white_overlay=Image.blend(src,white,.5);white_overlay.save(R/'qa'/f'{frame}秒_白模50%直接叠图.png')
 panel([src,mat,white,overlay,white_overlay],[f'{frame}秒来源原比例裁切／无变形','同一固定几何／材质版','同机位／白模','源＋材质50%直接叠图／残差保留','源＋白模50%直接叠图／残差保留'],R/'qa'/f'{frame}秒_来源材质白模与叠图.jpg')
views=json.load(open(R/'qa/build_facts.json'))['views'];ims=[];labels=[]
for v in views:
 p=R/'renders'/f'{v}_textured_clean.png';im=Image.open(p).convert('RGB');ims.append(im);labels.append(v+('（仅诊断删去前右墙与顶）' if v.startswith('12') else ''))
ims.append(Image.open(R/'renders/08_门铰链近景_white_clean.png').convert('RGB'));labels.append('08_门铰链近景（同机位白模补充）')
# Smaller labeled sheet, each image retains source proportions.
out=Image.new('RGB',(1200,395*((len(ims)+1)//2)),(24,28,34));d=ImageDraw.Draw(out)
for i,(im,l) in enumerate(zip(ims,labels)):
 x=(i%2)*600;y=(i//2)*395;d.text((x+10,y+12),l,font=font(20),fill='white');im=im.resize((590,332));out.paste(im,(x+5,y+48))
out.save(R/'qa/中文全视角联系表.jpg',quality=91)
rows=[]
for p in sorted((R/'models').glob('*')):
 if p.suffix not in ['.blend','.glb']:continue
 rows.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'qa/MODEL_FREEZE.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
