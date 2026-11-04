from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1];Q=R/'qa/r04';pairs=[('92.142973','SOURCE_092142973_SIDE'),('100.762992','SOURCE_100762992_TOP'),('108.755584','SOURCE_108755584_OBLIQUE'),('6.585758','AUX_006585758_REAR')];sheet=Image.new('RGB',(1536,1216),(24,27,30));d=ImageDraw.Draw(sheet);rows=[]
for i,(t,c) in enumerate(pairs):
 a=Image.open(R/'sources'/f'lakeleaf-native-{t}.png').convert('RGB');b=Image.open(R/'renders/r04/source'/f'{c}.png').convert('RGB');assert a.size==b.size==(3840,2160);ov=Image.blend(a,b,.5);p=Q/(c+'-overlay50.png');ov.save(p);rows.append({'time':t,'camera':c,'size':list(a.size),'operation':'direct full-size RGB 50% blend, no warp or resize','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'role':'auxiliary only, not fourth independent validation' if i==3 else 'source hypothesis; failed source agreement'})
 for j,(im,label) in enumerate([(a,'SOURCE'),(b,'R04 FAILED CANDIDATE'),(ov,'50%')]):sheet.paste(im.resize((512,288),Image.Resampling.LANCZOS),(j*512,304*i+16));d.text((j*512+4,304*i+2),t+'s '+label,fill='white')
sheet.save(Q/'r04-failed-source-comparisons.jpg',quality=92);(Q/'r04-failed-source-comparisons.json').write_text(json.dumps({'source_accepted':False,'phase':'R04 material sources only; later checks/main/white stopped before execution after tip defect; repaired R05 must rerender','rows':rows},indent=2)+'\n')
