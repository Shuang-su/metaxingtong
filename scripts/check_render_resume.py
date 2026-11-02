from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parents[1];result=[];valid=[]
for kind,names in [('material',['MAIN','SRC_front','SRC_oblique']+[f'CHECK{i:02d}'for i in range(1,9)]),('white',['MAIN','SRC_front','SRC_oblique'])]:
 for n in names:
  fn=f'R02_delivery_{kind}_{n}.png';p=D/'renders'/fn;expect=(640,360)if n.startswith('CHECK')else(1920,1080)
  try:
   im=Image.open(p);im.verify();im=Image.open(p);im.load();assert im.size==expect;sha=hashlib.sha256(p.read_bytes()).hexdigest();valid.append(fn);result.append({'file':fn,'valid':True,'size':im.size,'sha256':sha})
  except Exception as e:result.append({'file':fn,'valid':False,'error':str(e)})
(D/'qa/valid_delivery_pngs.txt').write_text('\n'.join(valid));(D/'qa/render_completion.json').write_text(json.dumps(result,indent=2));print(len(valid),'of',len(result),'valid')
