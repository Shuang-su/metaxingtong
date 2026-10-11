from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];Q=R/'qa';D=R/'inputs/motion_right_to_front_verified';F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';font=lambda n:ImageFont.truetype(F,n)
def header(im,title,sub=''):
 c=Image.new('RGB',(im.width,im.height+85),'#161c28');c.paste(im,(0,85));d=ImageDraw.Draw(c);d.text((18,10),title,font=font(25),fill='white');d.text((18,49),sub,font=font(17),fill='#c0cad8');return c
# Fixed identity drawing, no image transforms other than thumbnail contact sheet.
names=['hall_A_2712_paused_core.png','hall_B_4509_paused_core.png','hall_right_arch_4528_paused_core.png','hall_right_arch_4529_natural_ui_clear_core.png']; xs=[[209,302,873,982,1140],[350,412,769,841,995],[None,None,148,278,486],[None,None,322,428,610]];labels=['左中柱L1','左后柱L2','右后柱R1','右中柱R2','右前柱R3'];colors=['#55ffff','#99ff88','#ffee77','#ff8888','#cc99ff'];can=Image.new('RGB',(2360,1418),'#161c28')
for j,(name,pos) in enumerate(zip(names,xs)):
 im=Image.open(R/'inputs'/name).convert('RGB');d=ImageDraw.Draw(im)
 for x,l,col in zip(pos,labels,colors):
  if x is None:continue
  d.line((x,140,x,325),fill=col,width=3);d.text((max(3,min(x-45,1070)),330),l,font=font(17),fill=col)
 d.rectangle((0,600,1180,664),fill='#161c28');d.text((15,608),name,font=font(18),fill='white');d.text((15,634),'线是粗身份标识，不是柱轴亚像素观测；不赋旧模型Y序号',font=font(17),fill='#c0cad8');can.paste(im,((j%2)*1180,(j//2)*709))
can=header(can,'柱列身份核验：A左209 → B左350，不能配到B左225','R1/R2/R3依次从后墙灯向前；A最前列被边缘裁切。未经模型几何拟合。');can.save(Q/'column_identity_review.jpg',quality=93,subsampling=0)
# Floors: all lines within individual source; no cross-frame tile identity.
lines=[[(107,580),(321,446),(934,446),(1119,539)],[(157,620),(396,472),(850,472),(990,533)],[(40,440),(191,512),(650,442),(1099,518)],[(157,436),(335,587),(748,450),(1046,511)]];can=Image.new('RGB',(2360,1418),'#161c28')
for j,(name,line) in enumerate(zip(names,lines)):
 im=Image.open(R/'inputs'/name).convert('RGB');d=ImageDraw.Draw(im)
 for a,b in [line[:2],line[2:]]:
  d.line((*a,*b),fill='#44ffcc',width=3)
  for x,y in [a,b]:d.ellipse((x-8,y-5,x+8,y+5),outline='#ffe066',width=2)
 d.rectangle((0,0,1180,44),fill='#161c28');d.text((12,9),f'{name}: 单帧同方向中心链，非正交标定/跨帧匹配',font=font(18),fill='white');can.paste(im,((j%2)*1180,(j//2)*709))
header(can,'地面方向条件不足：仅一组主方向较稳','A/B另一组近乎平行；右斜图第二长缝尚未可靠确认。不能用假定正交自动求焦距。').save(Q/'floor_direction_review.jpg',quality=93,subsampling=0)
# Focal profile chart deliberately in px at fixed principal point.
p=json.loads((Q/'pair_2713_4509_motion_diagnostic.json').read_text())['rotation_zoom']['focal_profile'];p=[q for q in p if q['f1_pixels']>=800];can=Image.new('RGB',(1180,664),'#161c28');d=ImageDraw.Draw(can);d.text((24,20),'2713→4509：同后墙地标允许多组焦距解',font=font(28),fill='white');d.text((24,66),'固定主点(590,332)；仅旋转+两焦距；26个灯具局部特征不等于26个独立深度',font=font(20),fill='#c0cad8');x0,y0=100,570;w,h=970,390;d.line((x0,y0,x0+w,y0),fill='white',width=2);d.line((x0,y0,x0,y0-h),fill='white',width=2)
for val in [0,.2,.4,.6,.8,1.]:
 y=y0-val*h;d.line((x0,y,x0+w,y),fill='#354357');d.text((35,y-10),str(val),font=font(18),fill='white')
for key,col in [('training_median_px','#55eecc'),('training_p90_px','#ffaa66')]:
 pts=[(x0+(q['f1_pixels']-800)/1550*w,y0-q[key]*h)for q in p];d.line(pts,fill=col,width=4)
 for (x,y),q in zip(pts,p):d.ellipse((x-5,y-5,x+5,y+5),fill=col)
for q in p:
 x=x0+(q['f1_pixels']-800)/1550*w;d.text((x-26,580),str(q['f1_pixels']),font=font(18),fill='white')
d.text((385,619),'源图焦距 f1，像素单位（不是相机验收）',font=font(21),fill='white');d.text((125,125),'绿色=中位误差；橙色=P90；误差单位px',font=font(20),fill='white');can.save(Q/'focal_profile_rear_wall.png')
# 042/049 annotated fixed source coordinates, common plane transfer point predictions only.
pair=json.loads((Q/'plane_transfer_diagnostic.json').read_text())['pairs'][2];rp=json.loads((Q/'continuous_motion_refined_diagnostic.json').read_text())['pairs'][2];t=json.loads((Q/'continuous_architecture_tracks.json').read_text());can=Image.new('RGB',(2360,664))
for j,i in enumerate([42,49]):
 im=Image.open(D/f'{i:03}.jpg').crop((0,27,1180,691)).convert('RGB');d=ImageDraw.Draw(im)
 for q in pair['predictions']:
  xy=q['source_xy']if j==0 else q['target_xy'];x,y=xy;co='#44eebb' if q['group'] in pair['training_groups'] else '#ffe066';d.ellipse((x-3,y-3,x+3,y+3),outline=co,width=2)
  if q['id'] in [54,55,56,25]:d.text((x-30,y+8),f"ID {q['id']}",font=font(18),fill='white')
  if j==1 and q['id']==54:
   u,v=q['arch_plane_prediction'];d.line((x,y,u,v),fill='#ff4444',width=4);d.rectangle((u-5,v-5,u+5,v+5),outline='#ff4444',width=2);d.text((815,500),'近柱方台角：拱面预测残差26.1px',font=font(20),fill='white')
 can.paste(im,(j*1180,0))
header(can,'连续042→049：拱面局部吻合不能替代完整深度验证','原图未warp；绿色=拱面拟合点，黄色=其它深度点；近柱角单独留出。截图时刻见JSON前后区间。').save(Q/'continuous_parallax_042_049.jpg',quality=95,subsampling=0)
# Direct 50% unaligned source-source overlay, diagnostic only, unlike model overlays.
a=Image.open(D/'042.jpg').crop((0,27,1180,691)).convert('RGB');b=Image.open(D/'049.jpg').crop((0,27,1180,691)).convert('RGB');Image.blend(a,b,.5).save(Q/'source_042_049_direct50.png')
# High-res selected originals/crops for downstream checks.
for i in [35,42,49]:
 Image.open(D/f'{i:03}.jpg').crop((0,27,1180,691)).save(Q/f'selected_{i:03}_core.png')
print('diagnostic figures done')
