from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1]; O=R/'c32_cabinet_diagnosis'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
entries=[
 {'id':'658','path':'inputs/hospital_658.052095_native.png','seconds':658.052095,'camera_status':'No calibrated camera in this audit; source correspondence only','crop_xyxy':[0,720,115,1035], 'features':[{'id':'counter','box_xyxy':[0,732,43,793],'observation':'White projecting slab with rounded outer corner; left side clipped by native frame'},{'id':'upper_pull','box_xyxy':[23,853,57,882],'observation':'Small external U-shaped pull, with bright outer connector and two bars visible'},{'id':'lower_pull','box_xyxy':[6,893,51,926],'observation':'Second external U-shaped pull at a lower level; bright outer connector, bars and cast shadow'}]},
 {'id':'H','path':'inputs/hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','seconds':1101.728114,'camera_status':'Existing conditional C10_H camera; no refit performed','crop_xyxy':[0,770,115,1080], 'features':[{'id':'counter','box_xyxy':[0,790,20,845],'observation':'White slab outer corner partly visible at native left boundary'},{'id':'upper_pull','box_xyxy':[0,906,21,928],'observation':'Upper bright protruding pull portion; its left attachment is frame-clipped'},{'id':'lower_pull','box_xyxy':[0,947,34,981],'observation':'Lower bright protruding pull portion; left portion frame-clipped'}]}
]
colors={'counter':(255,200,40),'upper_pull':(255,80,90),'lower_pull':(70,210,255)}
for e in entries:
 p=R/e['path'];im=Image.open(p).convert('RGB');e['sha256']=sha(p);e['native_dimensions']=list(im.size);e['pixel_annotation_method']='Manual approximate feature envelopes; not fitted corners or calibrated measurements; boundary tolerance roughly 2-4 native pixels.'
 crop=im.crop(e['crop_xyxy']);crop.save(O/(e['id']+'_cabinet_native_crop.png'))
 ann=im.copy();draw=ImageDraw.Draw(ann)
 for f in e['features']:draw.rectangle(f['box_xyxy'],outline=colors[f['id']],width=1)
 ann.crop(e['crop_xyxy']).save(O/(e['id']+'_cabinet_annotated_native1x.png'))
 ann.crop(e['crop_xyxy']).resize((345,3*crop.height),Image.Resampling.NEAREST).save(O/(e['id']+'_cabinet_annotated_inspection3x.png'))
inv=[]
for p in sorted((R/'inputs').glob('*.png')):
 if 'native' in p.name:inv.append({'path':str(p.relative_to(R)),'sha256':sha(p),'dimensions':list(Image.open(p).size)})
D={'source_url':'https://www.bilibili.com/video/BV1GqXMByE1s/','source_frames':entries,'input_native_frame_inventory':inv,'negative_source_coverage':[{'id':'872.246724','finding':'Window/sofa/character view; no visible target cabinet. Not a calibrated fitting target.'},{'id':'G_1116.180816','finding':'Bed/window view; target cabinet is outside native image.'},{'id':'N642','finding':'Window/right-turn view; target cabinet is outside native image.'},{'id':'665.501733','finding':'Downward window/sofa view; no target cabinet local contour.'},{'id':'650.811153','finding':'Window/sofa view; no target cabinet local contour.'},{'id':'1103.087901','finding':'Window/sofa view; target cabinet not visibly exposed.'},{'id':'1801.322818 and 1804.861415','finding':'Headwall/bed view; no target cabinet; these do not supply second calibrated cabinet contour.'}],'feature_scope':'The repeated local white slab and two pull levels support a matching cabinet assembly near the native left border. The project name right-rear is not a screen-side label. The correspondence to the two named model objects remains a semantic hypothesis, not a recovered full object pose.','two_source_limit':'H and 658 are two native source frames from one video, not two independently calibrated camera observations. Partial repeated shapes establish visible feature identity; they do not establish an unchanged world pose across the time gap or recover full dimensions.'}
(O/'source_evidence.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
board=Image.new('RGB',(1135,1120),(245,245,242));dr=ImageDraw.Draw(board)
dr.text((20,15),'C32 CABINET AUDIT | NATIVE SOURCE EVIDENCE | NO MODEL EDIT / NO NEW RENDER',fill=(15,15,15),font=font)
cols=[('Source 658 | uncalibrated','658_cabinet_annotated_inspection3x.png','Native ROI x=0:115, y=720:1035'),('Source H | conditional camera','H_cabinet_annotated_inspection3x.png','Native ROI x=0:115, y=770:1080'),('Existing C29 H render','H_C29_cabinet_inspection3x.png','Same H ROI. Model cabinet is offscreen.')]
for i,(title,filename,subtitle) in enumerate(cols):
 x=20+375*i;dr.text((x,50),title,fill=(15,15,15),font=font);dr.text((x,77),subtitle,fill=(50,50,50),font=small);board.paste(Image.open(O/filename),(x,105))
dr.text((20,1068),'Yellow: slab. Red/cyan: two pull levels. Boxes are observations, not precision landmarks.',fill=(20,20,20),font=font)
dr.text((20,1094),'Nearest-neighbor 3x inspection only. Native crops and original hashes are retained separately.',fill=(55,55,55),font=small)
board.save(O/'two_source_cabinet_evidence.png')
print(json.dumps({'sources':[(e['id'],e['sha256']) for e in entries],'board':str(O/'two_source_cabinet_evidence.png')},indent=2))
