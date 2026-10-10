from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib,csv
p=Path('classroom_motion_validation_20261010');q=p/'tracked_desks_white';(q/'overlays').mkdir(exist_ok=True);f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17);out=Image.new('RGB',(1770,786),'#202020');d=ImageDraw.Draw(out);manifest=[]
for i,n in enumerate(['F_path_073','F_path_080']):
 src=p/'source'/(n+'_video.png');ren=q/'renders'/(n+'.png');a=Image.open(src).convert('RGB');b=Image.open(ren).convert('RGB');assert a.size==b.size==(1180,664);v=Image.blend(a,b,.5);ov=q/'overlays'/(n+'_direct50.png');v.save(ov)
 for k,(im,title) in enumerate([(a,'真实连续来源'),(b,'几何研究：仅两桌，桌腿示意'),(v,'直接50%叠图，其他可见桌未建')]):out.paste(im.resize((590,332)),(590*k,393*i+53));d.text((590*k+3,393*i+5),n+'｜'+title,font=f,fill='white');d.text((590*k+3,393*i+27),'未通过整屋验收，不表示教室只有两桌',font=f,fill='#ffcf66')
 manifest.append({'frame':n,'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'render':str(ren),'render_sha256':hashlib.sha256(ren.read_bytes()).hexdigest(),'overlay':str(ov),'overlay_sha256':hashlib.sha256(ov.read_bytes()).hexdigest(),'operation':'1180x664 source and physical render direct50% blend, no warp/resize. Contact sheet only resized.'})
out.save(q/'两张可追踪桌_共享白模直接对照.jpg',quality=94);(q/'qa/overlay_provenance.json').write_text(json.dumps(manifest,indent=2))
fits=json.load(open(p/'qa/camera_only_fits.json'));diag=json.load(open(p/'desk_identity_highview/camera_static_point_diagnostics.json'))['shared_focal_joint_bundle']['regularized'];rect=json.load(open(q/'qa/two_rectangle_fits.json'));rows=[]
for c in diag['cameras']:
 n=c['name'];base=next(x for x in fits if x['name']==n);rows.append([n,'建筑及固定家具拟合',sum(x['role']=='fit' for x in base['points']),c['new_fit_anchor_rms_px']]);rows.append([n,'建筑及固定家具独立留出',sum(x['role']=='holdout' for x in base['points']),c['new_holdout_rms_px']]);rows.append([n,'四静物共同拟合',4,c['static_feature_rms_px']])
 for desk in rect['desks']:
  pts=[r for r in desk['points'] if r['frame']==n]
  if pts:rows.append([n,desk['source_id']+'实见桌角拟合',len(pts),(sum(r['error_px']**2 for r in pts)/len(pts))**.5])
with open(q/'qa/拟合与留出点残差.csv','w',newline='',encoding='utf-8-sig') as h:
 w=csv.writer(h);w.writerow(['来源帧','角色','点数','RMS像素']);w.writerows(rows)
