from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
from pathlib import Path
p=Path('classroom_hd_alignment_20261010');font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for base in [p,p/'rejected_shift']:
 im=Image.open(base/'qa/D_desktop_ids.png').convert('RGB');arr=np.array(im);colors,cnt=np.unique(arr.reshape(-1,3),axis=0,return_counts=True);vis=json.load(open(base/'qa/D_desktop_visibility.json'));d=ImageDraw.Draw(im)
 for n,count in vis['pixel_counts'].items():
  if count<=20:continue
  matches=np.where(cnt==count)[0]
  if len(matches)!=1:continue
  color=colors[matches[0]];ys,xs=np.where((arr==color).all(2));xm=max(50,min(1120,int(np.median(xs))));ym=int(np.median(ys));label=n.replace(' rounded oak desktop','').replace('V4 ','');d.text((xm,ym),label,fill='white',font=font,stroke_width=2,stroke_fill='black',anchor='mm')
 d.text((10,10),f"学生桌总数{vis['total_student_desktops']}，当前视角可见{vis['visible_over_20px']}",fill='white',font=font)
 im.save(base/'qa/D_desktop_ids_labeled.png')
imgs=[Image.open(p/'qa/D_new_source_14_units.png').convert('RGB'),Image.open(p/'qa/D_desktop_ids_labeled.png').convert('RGB'),Image.open(p/'rejected_shift/qa/D_desktop_ids_labeled.png').convert('RGB')];sheet=Image.new('RGB',(1180,3*692),'#202020');d=ImageDraw.Draw(sheet)
for i,(im,label) in enumerate(zip(imgs,['新高清来源：至少14个独立木面/围板；D编号不等于模型桌ID','主模型未改：总20桌，可见12桌；另8桌完整投影在画面左侧之外','拒绝的共享前移试验：虽可见14桌，但新增仅110/477像素碎片，C视角明显退步'])):
 d.text((10,i*692+5),label,fill='white',font=font);sheet.paste(im,(0,i*692+28))
sheet.save(p/'D数量冲突_来源与投影ID.jpg',quality=94)
# Landmarks are a separate diagnostic; the five delivered overlays remain unannotated direct blends.
checks=json.load(open(p/'qa/new_source_anchor_errors.json'));names={'A':'classroom_0919_front','B':'classroom_2123_key','C':'classroom_4284_wide','D':'classroom_5447_key'}
for c in checks:
 n=names[c['camera']['name'][-1]];im=Image.open(p/'source'/f'{n}_video.png').convert('RGB');d=ImageDraw.Draw(im)
 for v in c['points']:
  x,y=v['source_px'];u,w=v['projected_px'];d.ellipse((x-4,y-4,x+4,y+4),outline='cyan',width=2);d.line((x,y,u,w),fill='yellow',width=2);d.ellipse((u-4,w-4,u+4,w+4),outline='red',width=2)
 d.text((10,10),f"青色：来源；红色：模型。抽查锚点RMS {c['rms_px']:.2f}px，不是全幅误差",font=font,fill='yellow',stroke_width=1,stroke_fill='black');im.save(p/'qa'/f'{n}_anchors.png')
# Direct C/D images of rejected candidate, no registration.
for cam,n in [('C','classroom_4284_wide'),('D','classroom_5447_key')]:
 src=Image.open(p/'source'/f'{n}_video.png').convert('RGB');a=Image.open(p/'renders'/f'{n}.png').convert('RGB');b=Image.open(p/'rejected_shift'/f'{cam}_normal_material.png').convert('RGB');sheet=Image.new('RGB',(1180,3*692),'#202020');d=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate([(src,'新高清来源'),(Image.blend(src,a,.5),'主模型未改：直接50%叠图'),(Image.blend(src,b,.5),'拒绝的共享前移：直接50%叠图')]):d.text((10,i*692+5),label,font=font,fill='white');sheet.paste(im,(0,i*692+28))
 sheet.save(p/'rejected_shift'/f'{cam}_source_baseline_rejected.jpg',quality=94)
