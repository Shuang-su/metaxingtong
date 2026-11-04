from pathlib import Path
from PIL import Image, ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'renders'/'R06';rows=[];manifest=[]
for tag,source in [('a15_f110','key-a15-frame110.png'),('a16_f027','key-a16-frame027.png'),('a16_f107','key-a16-frame107.png')]:
 src=Image.open(ROOT/'sources'/source).convert('RGB');assert src.size==(320,176)
 mats=[]
 for mode in ['material','white']:
  r=Image.open(out/f'SRC_{tag}_{mode}.png').convert('RGB');assert r.size==src.size
  over=Image.blend(src,r,.5);path=out/f'OVERLAY_{tag}_{mode}_direct50_320x176.png';over.save(path)
  manifest.append(dict(source=source,render=f'SRC_{tag}_{mode}.png',overlay=path.name,dimensions=list(src.size),alpha=.5,registration='NONE',warp='NONE',resampling='NONE',actor_removed=False,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  if mode=='material':mats=[src,r,over]
 row=Image.new('RGB',(960,201),(24,27,32));d=ImageDraw.Draw(row)
 for i,(im,lbl) in enumerate(zip(mats,['GIF SOURCE 320x176','R06 MATERIAL 320x176','DIRECT 50% / NO WARP'])):row.paste(im,(i*320,25));d.text((i*320+6,7),tag+' '+lbl,fill='white')
 rows.append(row)
contact=Image.new('RGB',(960,len(rows)*201),(24,27,32))
for i,row in enumerate(rows):contact.paste(row,(0,201*i))
contact.save(out/'SOURCE_MATERIAL_DIRECT50_contact.png')
# Exact same pixel windows, no independent local registration.
rois=[('central_frame',(94,49,224,137)),('disc',(192,108,242,147)),('gifts',(241,118,273,148)),('upper_arc',(0,0,320,64)),('left_pier',(68,45,98,141)),('right_pier',(227,45,251,145)),('left_side_screen',(9,52,73,144)),('right_side_screen',(250,49,317,146))]
src=Image.open(ROOT/'sources/key-a16-frame027.png').convert('RGB');r=Image.open(out/'SRC_a16_f027_material.png').convert('RGB');ov=Image.blend(src,r,.5);rp=out/'object_crops';rp.mkdir(exist_ok=True);cropmeta=[]
for name,box in rois:
 for role,im in [('source',src),('render',r),('direct50',ov)]:im.crop(box).save(rp/(name+'_'+role+'.png'))
 cropmeta.append(dict(group=name,source='key-a16-frame027.png',box_xyxy=list(box),display_scaling='none',camera='SRC_a16_f027 estimated',status='Conditional group comparison; not instance acceptance'))
(ROOT/'qa/R06_direct_overlay_manifest.json').write_text(json.dumps(manifest,indent=2));(ROOT/'qa/R06_object_crop_manifest.json').write_text(json.dumps(cropmeta,indent=2))
