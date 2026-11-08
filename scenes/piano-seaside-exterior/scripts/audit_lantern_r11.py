"""Read local artifact bytes and committed blobs. No network or publication."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];repo=R.parents[1];Q=R/'qa/r11';base='f4138510cde1fd199b49d4fad8bb1a4fc429cb10'
changed=subprocess.check_output(['git','diff','--name-only',base],cwd=repo,text=True).splitlines()
for p in changed:
 assert p.startswith('scenes/piano-seaside-exterior/'),p
 if any('/'+x+'/' in p for x in ['sources','models/r09','models/r10','qa/r09','qa/r10','textures/r09','textures/r10_trial']):raise AssertionError('protected prior/source file changed: '+p)
paths=[]
for d in [R/'models/r11',R/'textures/r11',Q]:paths.extend(p for p in d.rglob('*') if p.is_file() and p.suffix!='.blend1' and p.name not in ['artifact-manifest.json','local-git-byte-audit.json'])
paths.extend((R/'scripts').glob('*r11.py'));paths.extend([R/'README.md',R/'docs/reproduce.md'])
files=[]
for p in sorted(set(paths)):
 b=p.read_bytes();assert len(b)<100*1024*1024;files.append({'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()})
sources=[]
for p in sorted((R/'sources/native').glob('*.png')):
 b=p.read_bytes();old=subprocess.check_output(['git','cat-file','blob',base+':scenes/piano-seaside-exterior/'+str(p.relative_to(R))],cwd=repo);assert b==old;sources.append({'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'same_as_frozen_R10':True})
white=(R/'models/r11/piano_seaside_white.glb').read_bytes();assert white==(R/'models/r09/piano_seaside_white.glb').read_bytes()
report={'baseline':base,'stage':'R11 shared paper-lamp emission and actual lighting correction','files':files,'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),'max_file':max(files,key=lambda f:f['bytes']),'sources':sources,'white_GLB':'byte-identical R09 copy, reimported in R11 validation','external_mutations_before_artifact_commit':0,'publication':'snapshot before authorized normal Git publication; no attachment upload attempted','source_acceptance':False}
(Q/'artifact-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
if '--git' in sys.argv:
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();bad=[]
 for f in files:
  b=subprocess.check_output(['git','cat-file','blob',head+':scenes/piano-seaside-exterior/'+f['path']],cwd=repo)
  if len(b)!=f['bytes'] or hashlib.sha256(b).hexdigest()!=f['sha256']:bad.append(f['path'])
 assert not bad,bad
 (Q/'local-git-byte-audit.json').write_text(json.dumps({'commit':head,'actual_local_git_blob_reads':len(files),'mismatches':bad,'remote_readback':'not performed; local-only stage'},indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['files','sources']},indent=2))
