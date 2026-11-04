from pathlib import Path
import json,hashlib,subprocess
p=Path(__file__).resolve().parent;s=p.parent/'source-newscene-20261104'
regions={'2966.475632': {'people':[[606,337,740,580],[762,289,917,538],[820,395,976,685],[999,300,1129,551],[1114,357,1280,609]],'effects':[[786,367,1004,659]],'fog':[]},'2988.177427':{'people':[[625,550,756,798],[742,548,870,809],[873,552,1009,790],[983,553,1118,790],[811,452,916,755]],'effects':[[797,448,972,709]],'fog':[[0,250,1919,510],[1510,280,1919,900]]},'2992.479275':{'people':[[800,500,925,601]],'effects':[[790,491,944,601]],'fog':[[230,80,710,550],[1060,0,1470,490],[1480,190,1919,1000]]}}
for t,ro in regions.items():
 src=s/f'forest-native-{t}.png';cap=json.loads(src.with_suffix('.json').read_text());ex=[]
 for cls,key in [(1,'people'),(2,'effects'),(3,'fog')]:
  for b in ro[key]:ex.append({'shape':'rectangle','points':b,'class':cls,'description':{1:'Conservative moving-performer ROI; includes background, not segmentation',2:'Character luminous wing/effects, not static geometry',3:'Conservative volumetric fog/light caution; includes obscured background; not solid surface'}[cls]})
 m={'BV':'BV1ic12BMEk6','url':'https://www.bilibili.com/video/BV1ic12BMEk6/','uploader':'星瞳_Official','time_seconds':float(t),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'capture_record':cap,'quality':'1080P 高码率, official highest offered; no4K','exclusions':ex,'scene_cautions':['Floating flower island visible in low/wide views, no actual stem/pillar contact observed','Screen overlap with ground vegetation is NOT support or contact','Dark inverted root/soil cone detail unresolved; monocular depth cannot fill hidden surfaces','Unknown animation translation/rotation, cannot numerically infer from selected frames','Volumetric light/fog and thin foliage alpha boundaries can fail'],'dark_rgb_max_threshold':25}
 meta=p/'provenance'/f'forest-{t}-metadata.json';meta.write_text(json.dumps(m,ensure_ascii=False,indent=2))
 with (p/'provenance'/f'forest-{t}.log').open('w') as log:subprocess.run([str(p/'venv/bin/python'),str(p/'run_depth_frame.py'),'--source',str(src),'--metadata',str(meta),'--out',str(p/f'forest-{t}')],stdout=log,stderr=subprocess.STDOUT,check=True)
 print(t,'complete',flush=True)
