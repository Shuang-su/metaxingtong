"""Local file and committed-byte audit; no network and no rebuild."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];repo=R.parents[1];Q=R/'qa/r10';base='74cadf12765d2b6b17743b04351342440d62bebf'
changed=subprocess.check_output(['git','diff','--name-only',base],cwd=repo,text=True).splitlines();protected=[p for p in changed if any('/'+folder+'/' in p for folder in ['models/r09','qa/r09','textures/r09','sources'])];assert not protected,protected
paths=[]
for d in [R/'models/r10',R/'textures/r10_trial',Q]:
 paths.extend(p for p in d.rglob('*') if p.is_file() and p.suffix!='.blend1' and p.name not in ['artifact-manifest.json','local-git-byte-audit.json'])
paths.extend(p for p in (R/'scripts').glob('*r10.py'));paths.extend([R/'README.md',R/'docs/reproduce.md'])
records=[]
for p in sorted(set(paths)):
 b=p.read_bytes();assert len(b)<100*1024*1024
 records.append({'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()})
retained=[]
for p in sorted((R/'models/r09').glob('*.glb')):
 b=p.read_bytes();old=subprocess.check_output(['git','cat-file','blob',base+':scenes/piano-seaside-exterior/'+str(p.relative_to(R))],cwd=repo);assert b==old;retained.append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'rerendered_or_reexported':False,'reason':'world-only change; original GLB excludes worlds/lights/cameras'})
report={'stage':'R10 bounded sky sampling correction','baseline':base,'modified_R09_or_source_files':protected,'file_count':len(records),'total_bytes':sum(x['bytes'] for x in records),'max_file':max(records,key=lambda x:x['bytes']),'retained_GLB':retained,'files':records,'external_requests_this_stage':0,'source_acceptance':False}
(Q/'artifact-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
if '--git' in sys.argv:
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();bad=[]
 for f in records:
  p='scenes/piano-seaside-exterior/'+f['path'];b=subprocess.check_output(['git','cat-file','blob',head+':'+p],cwd=repo)
  if len(b)!=f['bytes'] or hashlib.sha256(b).hexdigest()!=f['sha256']:bad.append(p)
 assert not bad,bad
 (Q/'local-git-byte-audit.json').write_text(json.dumps({'commit':head,'actual_local_git_blob_reads':len(records),'mismatches':bad,'remote_readback':'not performed; local-only stage'},indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
