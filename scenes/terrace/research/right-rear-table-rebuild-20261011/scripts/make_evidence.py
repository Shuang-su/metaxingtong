from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,json,hashlib
P=Path(__file__).resolve().parent;D=P/'delivery';R=D/'renders'/'main'
src=next((P/'inputs').glob('开放*/terrace/frames/*main*.png'));old=next((P/'inputs').glob('露台_主*/renders/main/render_oidn.png'));oldraw=next((P/'inputs').glob('露台_主*/renders/main/render_raw.png'))
for s,n in [(src,'source_native_1920x1080.png'),(old,'old_main_normal.png'),(oldraw,'old_main_raw.png')]:shutil.copy2(s,D/n)
new=R/'render_oidn.png';raw=R/'render_raw.png';shutil.copy2(new,D/'new_main_normal.png')
a,b,c=[Image.open(f).convert('RGB') for f in [src,old,new]];assert a.size==b.size==c.size==(1920,1080)
Image.blend(a,Image.open(raw).convert('RGB'),.5).save(D/'source_new_fullframe_50percent.png')
Image.blend(b,c,.5).save(D/'old_new_fullframe_50percent.png')
box=(1430,580,1650,845);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',24)
panel=Image.new('RGB',(1320,635),'#f2f1ed');draw=ImageDraw.Draw(panel)
for i,(im,label) in enumerate([(a,'原生源图'),(b,'修改前：固定旧模型'),(c,'修改后：新重建候选')]):
 crop=im.crop(box).resize((440,530),Image.Resampling.NEAREST);panel.paste(crop,(440*i,48));draw.text((440*i+12,10),label,font=font,fill='black')
draw.text((12,590),'同源相机 / 同区域裁切放大；没有配准或改机位；杯与植物仍待改',font=font,fill='black');panel.save(D/'source_old_new_table_comparison.png')
for im,label in [(a,'source'),(b,'old'),(c,'new')]:im.crop(box).save(D/(label+'_table_native_crop.png'))
validation={'source_native_size':[1920,1080],'crop_box_xyxy':box,'crop_is_display_enlargement_only':True,'new_camera_equals_old_camera':None,'fullframe_overlay':'direct PIL Image.blend source/new raw, alpha .5; no alignment, resizing, warping, masking or hidden geometry','old_new_overlay':'direct Image.blend old/new normal .5','source_table_furniture_evidence':'green frame BV1g64y1P7VV @ 5586.011739','autumn_frame':'table cropped out; no second furniture validation'}
oldmeta=json.loads(next((P/'inputs').glob('露台_主*/renders/main/camera_render_manifest.json')).read_text());newmeta=json.loads((R/'camera_render_manifest.json').read_text());validation['new_camera_equals_old_camera']=all(oldmeta[k]==newmeta[k] for k in ['camera_name','camera_location','camera_rotation_euler','camera_matrix_world','lens_mm','sensor_width_mm','sensor_fit','shift_x','shift_y','render_resolution']);assert validation['new_camera_equals_old_camera']
(D/'evidence_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2))
