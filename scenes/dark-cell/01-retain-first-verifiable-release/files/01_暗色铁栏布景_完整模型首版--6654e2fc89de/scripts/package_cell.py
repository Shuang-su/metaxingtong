from pathlib import Path
import zipfile,hashlib,json
R=Path('/workspace/scratch/fa58bfcf0425/dark_cell_v1');out=R/'delivery';out.mkdir(exist_ok=True)
parts={'01_暗色铁栏布景_完整模型首版.zip':[], '02_暗色铁栏布景_来源与中文核验.zip':[]}
for p in R.rglob('*'):
 if not p.is_file() or '__pycache__' in p.parts or 'pre_fix' in p.parts or 'pre_color_fix' in p.parts or 'delivery' in p.parts or p.suffix in ['.blend1','.log','.pfm']:continue
 rel=p.relative_to(R)
 if rel.name in ['MODEL_FREEZE.json','build_facts.json','geometry_validation.json','assembly_checks.json'] or rel.parts[0]=='models' or rel.parts[0]=='textures' or rel.name.startswith('README') or rel.parts[0]=='scripts':parts['01_暗色铁栏布景_完整模型首版.zip'].append(p)
 if rel.parts[0]=='references' or rel.parts[0]=='qa' or rel.name.startswith('README') or (rel.parts[0]=='renders' and p.name.endswith('_clean.png')):parts['02_暗色铁栏布景_来源与中文核验.zip'].append(p)
rows=[]
for name,files in parts.items():
 path=out/name
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for p in sorted(files):z.write(p,p.relative_to(R))
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 assert path.stat().st_size<18_000_000
 rows.append({'name':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'first_version':True,'contents':len(files)})
(out/'DELIVERY_FREEZE.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False,indent=2))
