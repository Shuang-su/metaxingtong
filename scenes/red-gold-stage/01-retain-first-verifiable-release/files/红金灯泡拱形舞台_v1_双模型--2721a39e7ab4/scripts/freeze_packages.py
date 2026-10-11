from pathlib import Path
import json,zipfile,hashlib
R=Path('/workspace/scratch/fa58bfcf0425/red_gold_stage_v1');D=R/'delivery';D.mkdir(exist_ok=True)
model_files=list((R/'models').glob('*.blend'))+list((R/'models').glob('*.glb'))+list((R/'scripts').glob('*.py'))+[R/'README_红金拱形舞台.txt',R/'qa/build_facts.json',R/'qa/camera_full_bounds.json']
review_files=list((R/'source').glob('*'))+list((R/'renders').glob('*.jpg'))+[p for p in (R/'qa').glob('*') if p.suffix in ['.json','.jpg','.html','.txt'] or p.name=='源图_材质_50%直接叠图.png']+[R/'红金舞台_核验报告.html',R/'README_红金拱形舞台.txt']
review_files += [R/'renders/源图匹配_材质.png',R/'renders/源图匹配_白模.png',R/'renders/明确剖切_X0_诊断.png']
review_files += [p for p in (R/'qa').glob('*.blend') if not p.name.endswith('.blend1')]
for d in (R/'qa').glob('independent*'):
 if d.is_dir():review_files += [p for p in d.rglob('*') if p.is_file() and p.suffix in ['.json','.html','.txt','.jpg','.md']]
review_files += [p for p in (R/'independent').rglob('*') if p.is_file()]
review_files=[p for p in review_files if not p.name.startswith('当前候选')]
files=sorted(set(model_files+review_files));manifest={'scene':'红金灯泡拱形舞台','version':'v1_first_verified','history':'无已确认旧发布模型；不编造版本历史','geometry':'279闭合网格，34,828三角；材质白模同顶点','evidence':'360p已解码有效帧；无独立左右基线；背部/厚度/边界推定','files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(R/'FREEZE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
result=[]
for name,group in [('红金灯泡拱形舞台_v1_双模型.zip',model_files),('红金灯泡拱形舞台_v1_来源核验.zip',review_files)]:
 p=D/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,9) as z:
  for f in sorted(set(group+[R/'FREEZE_MANIFEST.json'])):z.write(f,arcname=str(f.relative_to(R)))
 assert p.stat().st_size<18000000,(p,p.stat().st_size)
 result.append({'name':name,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'delivery_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
