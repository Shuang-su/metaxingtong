import subprocess,json,hashlib,time,concurrent.futures
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/dark_cell_v1');views=json.load(open(R/'qa/build_facts.json'))['views'];jobs=[('textured',x) for x in views]+[('white',x) for x in ['01_来源932正面','04_室内左后','10_外部背面','11_底面','13_3626关系未证实']];manifest=[]
def run(job):
 typ,v=job;p=R/'models'/f'dark_cell_{typ}.blend';h=hashlib.sha256(p.read_bytes()).hexdigest();start=time.time()
 with open(R/f'render_{typ}_{v}.log','w') as f:r=subprocess.run(['/usr/bin/blender','-b','-t','4','--python',str(R/'scripts/render_cell.py'),'--',typ,v],stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0 and h==hashlib.sha256(p.read_bytes()).hexdigest(),job
 p=R/'renders'/f'{v}_{typ}.png';assert p.exists();return {'variant':typ,'view':v,'model_sha256':h,'render_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'seconds':time.time()-start}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for row in pool.map(run,jobs):
  manifest.append(row);(R/'qa/render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(row['view'],row['variant'],flush=True)
