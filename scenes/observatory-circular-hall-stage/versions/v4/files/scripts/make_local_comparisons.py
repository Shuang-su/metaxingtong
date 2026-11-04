from PIL import Image,ImageDraw
import pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parents[1];out=P/'renders/R06-local';out.mkdir(exist_ok=True);rows=[]
for num,name,rect in [(13,'SOURCE_13_high',(280,300,850,660)),(14,'SOURCE_14_front',(180,0,1010,580)),(15,'SOURCE_15_exterior',(350,240,1010,671)),(21,'SOURCE_21_high',(300,240,940,671))]:
 fs=[P/'sources/report'/f'{num}.png',P/'renders/R06'/f'material_{name}.png',P/'renders/R06-comparisons'/f'material_{name}_direct50.png'];w=rect[2]-rect[0];h=rect[3]-rect[1];im=Image.new('RGB',(3*w,h+28),'#333');d=ImageDraw.Draw(im)
 for i,(f,label) in enumerate(zip(fs,['ARTICLE CROP (not native)','MODEL / NOT ACCEPTED','DIRECT 50% / FAILED'])):
  im.paste(Image.open(f).convert('RGB').crop(rect),(i*w,28));d.text((i*w+4,6),label,fill='white')
 f=out/f'{num}-material-local-failed.png';im.save(f);rows.append({'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'crop_xyxy_original_pixels':rect,'inputs':[{'path':str(q.relative_to(P)),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in fs],'resample':False,'added_label_height':28,'new_angle':False,'result':'FAILED grouped-object diagnostic'})
(P/'qa/R06-local-records.json').write_text(json.dumps(rows,indent=2))
