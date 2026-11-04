from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parent;s=p.parent/'observatory-candidate-20261104/sources';man=json.loads((s/'source-manifest.json').read_text())
# Polygons in800x450 visual inspection display, mapped to1192x671 original screenshot.
regions={13:[(2,[(0,270),(215,175),(620,176),(800,300),(800,450),(0,450)]),(3,[(174,0),(303,0),(303,151),(174,151)]),(1,[(365,162),(438,162),(438,307),(365,307)])],14:[(2,[(0,334),(800,334),(800,450),(0,450)]),(3,[(295,0),(507,0),(507,90),(295,90)]),(4,[(80,44),(652,44),(652,242),(490,292),(463,423),(290,423),(296,294),(104,310)]),(1,[(344,119),(464,119),(464,433),(344,433)])],15:[(3,[(0,0),(800,0),(800,324),(665,324),(665,228),(570,228),(450,188),(343,237),(284,251),(239,293),(0,341)]),(4,[(0,327),(240,327),(240,450),(0,450)])]}
labels={1:'Performer/occluded background, conservative incomplete ROI',2:'Reflective floor/light reflections; do not infer geometry from reflections',3:'Starfield/planets/backdrop or opening background; not metric surfaces',4:'Luminous wings/beams/composited effects or glowing landscape; not solid geometry'}
for idx,rs in regions.items():
 m=next(x.copy() for x in man if x['index']==idx);m.update(path=str(s/'report'/f'{idx:02}.png'),output_name=f'report-image-{idx}',exclusions=[{'class':cls,'description':labels[cls],'points':[[round(x*1192/800),round(y*671/450)] for x,y in pts]} for cls,pts in rs]);f=p/'provenance'/f'{idx}-metadata.json';f.write_text(json.dumps(m,ensure_ascii=False,indent=2))
 with (p/'provenance'/f'{idx}-inference.log').open('w') as log:subprocess.run([str(p/'venv/bin/python'),str(p/'run_depth.py'),'--metadata',str(f)],stdout=log,stderr=subprocess.STDOUT,check=True)
 print(idx,'complete',flush=True)
