import subprocess,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[1];head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=D,text=True).strip();names=subprocess.check_output(['git','ls-tree','-r','--name-only',head],cwd=D,text=True).splitlines();out=[]
for n in names:
 a=(D/n).read_bytes();b=subprocess.check_output(['git','show',f'{head}:{n}'],cwd=D);assert a==b,n;out.append({'path':n,'bytes':len(a),'sha256':hashlib.sha256(a).hexdigest()})
(D/'qa/frozen_git_readback.json').write_text(json.dumps({'content_commit':head,'tracked_file_count':len(out),'all_git_blob_bytes_match_local_files':True,'remote_pushed':False,'files':out},indent=2))
print(head,len(out))
