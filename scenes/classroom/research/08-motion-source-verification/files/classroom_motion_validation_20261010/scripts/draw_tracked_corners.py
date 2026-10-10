from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,numpy as np
from scipy.spatial.transform import Rotation
p=Path('classroom_motion_validation_20261010');q=p/'tracked_desks_white';j=json.load(open(q/'qa/two_rectangle_fits.json'));cams={c['name']:c for c in j['cameras']};f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19);rows=[]
for n in ['F_path_073','F_path_076','F_path_080']:
 im=Image.open(p/'source'/(n+'_video.png')).convert('RGB');d=ImageDraw.Draw(im);c=cams[n]
 for desk,color,label in zip(j['desks'],['cyan','orange'],['A书叠杯桌','B纸张杯桌']):
  X=np.array(desk['world_corners_Q0_to_Q3']);v=(X-c['location'])@Rotation.from_euler('xyz',c['rotation_xyz']).as_matrix();ff=c['lens_mm']/36*1180;uv=np.c_[590+ff*v[:,0]/-v[:,2],332-ff*v[:,1]/-v[:,2]];pts=[tuple(x) for x in uv];d.line(pts+[pts[0]],fill=color,width=3)
  for r in desk['points']:
   if r['frame']==n:
    x,y=r['source_px'];d.ellipse((x-5,y-5,x+5,y+5),outline='lime',width=3);u,w=r['projected_px'];d.line((x,y,u,w),fill='red',width=2)
  valid=[x for x in pts if 0<x[0]<1180 and 30<x[1]<640]
  if valid:d.text((valid[0][0],valid[0][1]-24),label,font=f,fill=color,stroke_width=1,stroke_fill='black')
 d.text((5,5),n+' 同一模板/固定两桌：线为模型投影，绿圈为实见角点',font=f,fill='white',stroke_width=2,stroke_fill='black');im.save(q/'qa'/(n+'_corner_projection.png'));rows.append(im)
out=Image.new('RGB',(1180,664*3));[out.paste(im,(0,i*664)) for i,im in enumerate(rows)];out.save(q/'三帧同桌角点_共享投影验证.jpg',quality=95)
