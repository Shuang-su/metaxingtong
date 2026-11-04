from pathlib import Path
import hashlib,json,subprocess,sys
p=Path(__file__).resolve().parents[1];name=sys.argv[1];files=[]
for f in subprocess.check_output(['git','ls-files','-z'],cwd=p).decode().split('\0'):
 if not f:continue
 q=p/f;r=q.read_bytes();files.append(dict(path=str(q),relative_path=f,bytes=len(r),sha256=hashlib.sha256(r).hexdigest(),git_blob_sha=subprocess.check_output(['git','hash-object',f],cwd=p).decode().strip()))
b=p/'backups'/(name+'.bundle');subprocess.run(['git','bundle','create',str(b),'--all'],cwd=p,check=True);r=b.read_bytes()
a=dict(scene='redwhite-twistframe-hall',version=name,repository=str(p),branch=subprocess.check_output(['git','branch','--show-current'],cwd=p).decode().strip(),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p).decode().strip(),files=files,bundle=dict(path=str(b),bytes=len(r),sha256=hashlib.sha256(r).hexdigest()),status='CONDITIONAL / source FAILED; no acceptance')
(p/'backups'/(name+'_manifest.json')).write_text(json.dumps(a,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in a.items() if k!='files'},indent=2));print(len(files),sum(x['bytes'] for x in files))
