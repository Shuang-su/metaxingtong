"""Freeze tracked original files and real Git history for supported transfer; no remote claims."""
import argparse,subprocess,pathlib,hashlib,json,datetime
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--basis');a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1]
def git(*args): return subprocess.check_output(['git','-C',str(root),*args])
if git('diff','--cached','--name-only').strip(): raise SystemExit('Index has uncommitted staged data')
head=git('rev-parse','HEAD').decode().strip(); branch=git('symbolic-ref','HEAD').decode().strip()
output=pathlib.Path(a.output).resolve(); output.parent.mkdir(parents=True,exist_ok=True)
args=['bundle','create',str(output),branch]
if a.basis: args+=['^'+a.basis]
git(*args);git('bundle','verify',str(output))
files=[]
for path in git('ls-tree','-r','--name-only','-z','HEAD').decode().split('\0'):
 if not path:continue
 b=git('show','HEAD:'+path); files.append(dict(path=path,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),git_blob=git('rev-parse','HEAD:'+path).decode().strip()))
b=output.read_bytes();d=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),head=head,ref=branch,prerequisite=a.basis,bundle_path=str(output),bundle_bytes=len(b),bundle_sha256=hashlib.sha256(b).hexdigest(),file_count=len(files),payload_bytes=sum(x['bytes'] for x in files),files=files,remote_verified=False,scope="Committed HEAD only; active untracked render outputs excluded and not claimed delivered")
output.with_suffix('.manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items() if k!='files'},indent=2))
