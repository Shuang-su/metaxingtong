from pathlib import Path
import subprocess,json,hashlib,time
R=Path('/workspace/scratch/fa58bfcf0425/red_gold_stage_v1');views=json.load(open(R/'qa/build_facts.json'))['views'];jobs=[('textured',x) for x in views if x!='源图匹配']+[('white',x) for x in ['左前','背面','底面']];manifest=[x for x in (json.load(open(R/'qa/render_manifest.json')) if (R/'qa/render_manifest.json').exists() else []) if (x['variant'],x['view']) not in jobs]
for typ,v in jobs:
 p=R/'models'/f'red_gold_stage_{typ}.blend';before=hashlib.sha256(p.read_bytes()).hexdigest();start=time.time()
 with open(R/f'render_{typ}_{v}.log','w') as f:r=subprocess.run(['/usr/bin/blender','-b','-t','4','--python',str(R/'scripts/render_one.py'),'--',typ,v],stdout=f,stderr=subprocess.STDOUT)
 after=hashlib.sha256(p.read_bytes()).hexdigest();assert r.returncode==0 and before==after,(typ,v,r.returncode)
 name=v if v=='明确剖切_X0_诊断' else v+('_材质' if typ=='textured' else '_白模');im=R/'renders'/f'{name}.png';assert im.exists()
 manifest.append({'variant':typ,'view':v,'model_sha256':before,'render_sha256':hashlib.sha256(im.read_bytes()).hexdigest(),'seconds':time.time()-start});(R/'qa/render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(v,typ,'saved',flush=True)
(R/'renders/渲染状态_暂勿作最终验收.txt').unlink(missing_ok=True)
