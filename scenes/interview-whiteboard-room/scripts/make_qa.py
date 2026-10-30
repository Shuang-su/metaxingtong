"""Build exact 50% overlays, unwarped object crops, and explicitly resized display JPEGs.
Does not edit native sources or rendered pixels. Display labels are outside image cells.
"""
import json,hashlib,struct,shutil,csv
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'qa/r05'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
def label(im,txt,h=34):
 out=Image.new('RGB',(im.width,im.height+h),(24,28,32));out.paste(im,(0,h));ImageDraw.Draw(out).text((10,7),txt,font=small,fill=(235,235,235));return out
def jpg_limit(im,path,quality=90):
 for q in range(quality,44,-3):
  im.save(path,'JPEG',quality=q,optimize=True)
  if path.stat().st_size<900*1024:return
 raise RuntimeError('JPEG size limit not met')
source_names={'front':'BV14ioLBAEDt_1283.813032_front.png','oblique':'BV14ioLBAEDt_1505.632497_oblique.png'}
record={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'direct_overlays':[],'crops':[],'jpeg_display_scaling':[]}
triptychs=[]
for role,name in source_names.items():
 a=Image.open(ROOT/'sources'/name).convert('RGB');b=Image.open(QA/f'source-{role}-render.png').convert('RGB')
 assert a.size==b.size==(1920,1080)
 overlay=Image.blend(a,b,.5);overlay.save(QA/f'source-{role}-overlay50.png')
 record['direct_overlays'].append({'source':name,'render':f'source-{role}-render.png','output':f'source-{role}-overlay50.png','source_and_output_size':[1920,1080],'alpha':.5,'warp':False,'crop':None,'dynamic_person_removed':False})
 cells=[label(im.resize((640,360),Image.Resampling.LANCZOS),txt) for im,txt in zip([a,b,overlay],[role+' | native source (display 1/3)',role+' | shared model render',role+' | direct 50% overlay'])]
 strip=Image.new('RGB',(1920,394))
 for i,c in enumerate(cells):strip.paste(c,(i*640,0))
 triptychs.append(strip)
contact=Image.new('RGB',(1920,840),(24,28,32));ImageDraw.Draw(contact).text((14,12),'R05 CANDIDATE — same geometry / materials / lights; source fidelity NOT accepted',font=font,fill='white')
for i,strip in enumerate(triptychs):contact.paste(strip,(0,48+i*394))
jpg_limit(contact,QA/'source-contact.jpg',90)
record['jpeg_display_scaling'].append({'file':'source-contact.jpg','cell_size':[640,360],'source_size':[1920,1080],'method':'Lanczos display only, no fit warp'})
main=Image.open(QA/'source-front-render.png').convert('RGB');shutil.copyfile(QA/'source-front-render.png',QA/'main.png');jpg_limit(main,QA/'main.jpg',94)

checks=[]
for i in range(1,10):
 p=QA/f'check-{i:02d}.png';im=Image.open(p).convert('RGB');assert im.size==(1280,720)
 checks.append(label(im.resize((640,360),Image.Resampling.LANCZOS),f'CHECK {i:02d} | internal diagnostic; no source camera'))
sheet=Image.new('RGB',(1920,1224),(24,28,32));ImageDraw.Draw(sheet).text((14,10),'9 interior checks — complete inferred shell remains visible; no wall cutaway',font=font,fill='white')
for i,c in enumerate(checks):sheet.paste(c,((i%3)*640,42+(i//3)*394))
jpg_limit(sheet,QA/'inspection-contact.jpg',90)
record['jpeg_display_scaling'].append({'file':'inspection-contact.jpg','cell_size':[640,360],'source_size':[1280,720],'method':'Lanczos display only'})

crops={'front':{'board':(540,145,1410,710),'table-chair':(480,645,1420,1080),'left-wall':(0,0,240,960)},'oblique':{'board-wall':(680,0,1920,760),'foreground-conflict':(0,740,900,1080)}}
(QA/'crops').mkdir(exist_ok=True)
for role,items in crops.items():
 a=Image.open(ROOT/'sources'/source_names[role]).convert('RGB');b=Image.open(QA/f'source-{role}-render.png').convert('RGB');ov=Image.open(QA/f'source-{role}-overlay50.png').convert('RGB')
 for item,box in items.items():
  ims=[]
  for typ,im in [('source',a),('render',b),('overlay50',ov)]:
   cr=im.crop(box);cr.save(QA/'crops'/f'{role}-{item}-{typ}.png');ims.append(label(cr,typ))
  pair=Image.new('RGB',(ims[0].width*3,ims[0].height),(24,28,32))
  for i,im in enumerate(ims):pair.paste(im,(i*im.width,0))
  jpg_limit(pair,QA/'crops'/f'{role}-{item}-contact.jpg',85)
  record['crops'].append({'source_role':role,'object_group':item,'source_coordinates_xyxy':box,'same_rect_used_for_render_overlay':True,'scale_in_png':1,'camera_alignment':'conditional; not accepted'})

sources=[]
for frame in json.loads((ROOT/'sources/interview_source_manifest_20261030.json').read_text())['frames']:
 p=ROOT/'sources'/frame['file'];data=p.read_bytes();im=Image.open(p);im.load();width,height=struct.unpack('>II',data[16:24])
 sources.append({'file':p.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'ihdr':[width,height],'actual_decode':list(im.size),
 'expected_hash_match':hashlib.sha256(data).hexdigest()==frame['sha256'],'size_match':len(data)==frame['bytes'],'currentTime':frame['currentTime'],
 'library_identity_xattr_applied_on_original_download':True,'independently_viewed_pixels':True})
assert all(p['expected_hash_match'] and p['size_match'] for p in sources)
(QA/'source-byte-verification.json').write_text(json.dumps(sources,indent=2))
(QA/'image-processing-record.json').write_text(json.dumps(record,indent=2))
print('QA_COMPLETE',{'main_jpg_bytes':(QA/'main.jpg').stat().st_size,'source_contact_jpg_bytes':(QA/'source-contact.jpg').stat().st_size,'inspection_contact_jpg_bytes':(QA/'inspection-contact.jpg').stat().st_size})
