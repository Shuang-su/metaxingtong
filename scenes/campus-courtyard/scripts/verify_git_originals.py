"""Verify actual committed Git blob bytes for every manifest path; local only."""
from pathlib import Path
import subprocess,json,hashlib,sys
R=Path(__file__).resolve().parents[1];repo=R.parents[1]
commit=sys.argv[1] if len(sys.argv)>1 else subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
manifest=json.loads((R/'qa/original_file_manifest.json').read_text());out=[]
for row in manifest['files']:
    path='scenes/campus-courtyard/'+row['relative_path'];entry=subprocess.check_output(['git','ls-tree','-l',commit,'--',path],cwd=repo,text=True).strip()
    if not entry:out.append({'path':path,'pass':False,'reason':'missing committed path'});continue
    cols=entry.split();blob=cols[2];size=int(cols[3]);data=subprocess.check_output(['git','cat-file','blob',blob],cwd=repo)
    sha=hashlib.sha256(data).hexdigest();out.append({'path':path,'commit':commit,'git_blob':blob,'bytes':size,'sha256':sha,'pass':blob==row['git_blob_sha'] and size==row['bytes'] and sha==row['sha256']})
result={'verified_commit':commit,'local_git_tree_and_actual_blob_readback':True,'remote_push_or_download':False,'all_pass':all(x['pass'] for x in out),'count':len(out),'files':out}
(R/'qa/git_originals_readback.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
