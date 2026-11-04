from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,datetime
R=Path(__file__).resolve().parents[1];Q=R/'qa/r05'
rows=[('92.142973','SOURCE_092142973_SIDE','primary'),('100.762992','SOURCE_100762992_TOP','primary'),('108.755584','SOURCE_108755584_OBLIQUE','partial primary'),('6.585758','AUX_006585758_REAR','auxiliary only')]
report={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_accepted':False,'role':'White geometry diagnostic, not colour/lighting reproduction. Same camera and geometry as material candidate.','overlays':[]};sheet=Image.new('RGB',(1536,1216),(24,27,30));d=ImageDraw.Draw(sheet)
for i,(t,c,role) in enumerate(rows):
 src=R/'sources'/f'lakeleaf-native-{t}.png';rnd=R/'renders/r05/white-source'/f'{c}.png';a=Image.open(src).convert('RGB');b=Image.open(rnd).convert('RGB');assert a.size==b.size==(3840,2160);ov=Image.blend(a,b,.5);out=Q/(c+'-white-overlay50.png');ov.save(out)
 report['overlays'].append({'source':str(src.relative_to(R)),'white_render':str(rnd.relative_to(R)),'overlay':str(out.relative_to(R)),'role':role,'size':list(a.size),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'white_render_sha256':hashlib.sha256(rnd.read_bytes()).hexdigest(),'overlay_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operation':'Direct Image.blend(source RGB, white render RGB, 0.5); no warp/crop/rescale','calibration':'Unsolved conditional approximation'})
 for j,(im,label) in enumerate([(a,'SOURCE'),(b,'WHITE'),(ov,'DIRECT 50%')]):sheet.paste(im.resize((512,288),Image.Resampling.LANCZOS),(j*512,i*304+16));d.text((j*512+5,i*304+2),t+'s '+label+(' AUX' if i==3 else ''),fill='white')
sheet.save(Q/'source-white-overlay-contact.jpg',quality=92)
files=sorted((R/'renders/r05/white-checks').glob('*.png'));assert len(files)==8;sheet=Image.new('RGB',(1600,1896),(24,27,30));d=ImageDraw.Draw(sheet)
for i,p in enumerate(files):
 im=Image.open(p).convert('RGB');assert im.size==(1280,720);x=(i%2)*800;y=(i//2)*474;sheet.paste(im.resize((800,450),Image.Resampling.LANCZOS),(x,y+24));d.text((x+10,y+5),p.stem+' | shared white geometry inspection; not source',fill='white')
sheet.save(Q/'eight-white-inspection-views-contact.jpg',quality=91)
(Q/'white-comparison-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('White source suite complete: 4 native-size renders + direct overlays + 8 inspection views.')
