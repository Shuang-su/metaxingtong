"""Read all current stage bytes and verify staged Git blobs, without network."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];repo=R.parents[1];Q=R/'qa/r09'
paths=[]
for d in [R/'models/r09',R/'textures/r09',Q]:
 for p in d.rglob('*'):
  if p.is_file() and p.suffix!='.blend1' and p.name not in ['artifact-manifest.json','local-git-byte-audit.json']:paths.append(p)
paths += list((R/'sources/native').glob('*.png'))
paths += [R/'scripts'/n for n in ['make_environment_textures.py','build_environment_r09.py','render_environment_r09.py','validate_environment_r09.py','make_environment_review_r09.py','audit_environment_r09.py','validate_scene.py','render_glb_check.py','make_review.py']]
paths += [R/'README.md',R/'docs/reproduce.md',R/'docs/object-evidence.md',R/'sources/source-manifest.json']
files=[]
for p in sorted(set(paths)):
 data=p.read_bytes();size=len(data);assert size<100*1024*1024,(str(p),size)
 files.append({'path':str(p.relative_to(R)),'bytes':size,'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(size).encode()+b'\0'+data).hexdigest()})
report={'stage':'r09 local candidate','scope':'current R09 output/inputs/scripts plus original five native sources; failed trial A bytes also retained in Git history','files':files,'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),'max_file':max(files,key=lambda f:f['bytes']),'network_operation':'none','source_acceptance':False}
(Q/'artifact-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
if '--git' in sys.argv:
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();mismatches=[]
 for f in files:
  path='scenes/piano-seaside-exterior/'+f['path'];p=subprocess.run(['git','cat-file','blob',head+':'+path],cwd=repo,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if p.returncode or len(p.stdout)!=f['bytes'] or hashlib.sha256(p.stdout).hexdigest()!=f['sha256']:mismatches.append(path)
 audit={'commit':head,'file_count':len(files),'actual_local_git_blob_reads':len(files),'byte_sha256_mismatches':mismatches,'remote_readback':'not performed for this local stage','publish_state':'local only; no remote write in R09'}
 (Q/'local-git-byte-audit.json').write_text(json.dumps(audit,indent=2)+'\n');assert not mismatches,mismatches
print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
