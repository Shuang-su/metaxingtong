"""Read every indexed Git blob from a real commit; stdout JSON suitable for handoff.
Run after final commit. Does not mutate repository or use any network.
"""
import json,subprocess,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
commit=subprocess.check_output(['git','rev-parse',sys.argv[1] if len(sys.argv)>1 else 'HEAD'],text=True).strip()
repo=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],text=True).strip());rel=ROOT.relative_to(repo)
index=json.loads(subprocess.check_output(['git','show',f'{commit}:{rel}/file-index.json']))
bad=[];total=0
for r in index['files']:
 path=f'{rel}/{r["path"]}'
 blob=subprocess.check_output(['git','rev-parse',f'{commit}:{path}'],text=True).strip()
 data=subprocess.check_output(['git','cat-file','blob',f'{commit}:{path}']);total+=len(data)
 if blob!=r['git_blob_sha1'] or len(data)!=r['size_bytes'] or hashlib.sha256(data).hexdigest()!=r['sha256']:bad.append(path)
print(json.dumps({'commit':commit,'indexed_files_read_back':len(index['files']),'bytes_read_back':total,'mismatches':bad,'method':'actual local git cat-file bytes, not remote retrieval','network_used':False},indent=2))
sys.exit(bool(bad))
