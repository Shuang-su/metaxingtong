import subprocess,json,hashlib,sys
from pathlib import Path
D=Path(__file__).resolve().parents[1];stem=Path(sys.argv[1]);basis=sys.argv[2];bundle=stem.with_suffix('.bundle')
run=lambda args:subprocess.check_output(args,cwd=D).decode().strip()
head=run(['git','rev-parse','HEAD']);branch=run(['git','symbolic-ref','HEAD'])
subprocess.run(['git','bundle','create',str(bundle),basis+'..'+branch],cwd=D,check=True)
files=[]
for p in run(['git','ls-tree','-r','--name-only',head]).splitlines():
 b=subprocess.check_output(['git','show',head+':'+p],cwd=D);files.append({'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'blob_sha':run(['git','rev-parse',head+':'+p])})
changed=run(['git','diff','--name-status',basis,head]).splitlines();r={'head':head,'basis':basis,'basis_remote_ref':'history/city-window-bedroom-original-20261103','bundle':str(bundle),'bundle_bytes':bundle.stat().st_size,'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'files':files,'changes_from_basis':changed,'limits':'Incremental ordinary Git bundle, requires exact basis object/history. Does not alone contain old payload. Consumer must independently fetch verified remote basis, unbundle and verify entire manifest. No claim of new remote publication.'};Path(str(stem)+'-manifest.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['files','changes_from_basis']}));print('files',len(files),'changed',len(changed))
