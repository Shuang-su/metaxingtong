"""Freeze existing Git HEAD to a verifiable bundle; no credentials or network."""
import subprocess,hashlib,json,sys
from pathlib import Path
D=Path(__file__).resolve().parents[1]; stem=Path(sys.argv[1]); bundle=stem.with_suffix('.bundle')
run=lambda a:subprocess.check_output(a,cwd=D).decode().strip()
head=run(['git','rev-parse','HEAD'])
subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=D,check=True)
rows=[]
for p in run(['git','ls-tree','-r','--name-only',head]).splitlines():
 b=subprocess.check_output(['git','show',head+':'+p],cwd=D)
 rows.append({'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'blob_sha':run(['git','rev-parse',head+':'+p])})
out={'head':head,'bundle':str(bundle),'bundle_bytes':bundle.stat().st_size,'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'files':rows,'limits':'Only committed HEAD files. No remote or Space verification claim.'}
Path(str(stem)+'-manifest.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='files'}));print('files',len(rows),'largest',max(x['bytes'] for x in rows))
