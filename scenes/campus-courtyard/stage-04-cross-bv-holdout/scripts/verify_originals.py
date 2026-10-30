"""Verify ordinary source/model/render/QA files through actual local Git blob bytes."""
from pathlib import Path
import subprocess,json,hashlib,sys
D=Path(__file__).resolve().parents[1];REPO=D.parents[2];Q=D/'qa'
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args])
def digest(b):return hashlib.sha256(b).hexdigest()
if sys.argv[1]=='manifest':
    files=[]
    for p in sorted(D.rglob('*')):
        if not p.is_file() or p.name in ['original_file_manifest.json','git_originals_readback.json']:continue
        b=p.read_bytes();files.append({'path':str(p.relative_to(REPO)),'bytes':len(b),'sha256':digest(b),'git_blob_sha':git('hash-object',str(p)).decode().strip()})
    (Q/'original_file_manifest.json').write_text(json.dumps({'scope':'complete current Stage04 ordinary files, excluding this manifest and subsequent readback receipt','files':files,'files_count':len(files),'total_bytes':sum(x['bytes'] for x in files),'max_file_bytes':max(x['bytes'] for x in files)},indent=2))
    print('MANIFEST',len(files),sum(x['bytes'] for x in files),max(x['bytes'] for x in files))
elif sys.argv[1]=='readback':
    commit=git('rev-parse',sys.argv[2]).decode().strip();rows=[]
    for r in json.loads((Q/'original_file_manifest.json').read_text())['files']:
        spec=commit+':'+r['path'];blob=git('rev-parse',spec).decode().strip();b=git('cat-file','blob',spec)
        rows.append({**r,'read_commit':commit,'read_blob_sha':blob,'read_bytes':len(b),'read_sha256':digest(b),'match':blob==r['git_blob_sha'] and len(b)==r['bytes'] and digest(b)==r['sha256']})
    frozen=[]
    for name in ['campus-courtyard_material.blend','campus-courtyard_white.blend','campus-courtyard.glb']:
        p=D.parent/'stage-03-contact-qa'/name;relative=str(p.relative_to(REPO));old=git('cat-file','blob','87b37f98911f533605d5aebdd60756edb96fe951:'+relative);now=p.read_bytes()
        frozen.append({'path':relative,'bytes':len(now),'sha256':digest(now),'identical_to_frozen_commit_bytes':now==old})
    result={'read_commit':commit,'all_match':all(x['match'] for x in rows),'count':len(rows),'rows':rows,'frozen_model_files':frozen,'all_frozen_model_files_unchanged':all(x['identical_to_frozen_commit_bytes'] for x in frozen),'scope':'Actual local commit/tree/blob bytes read. No remote push or download; no output Library upload.'}
    assert result['all_match'] and result['all_frozen_model_files_unchanged']
    (Q/'git_originals_readback.json').write_text(json.dumps(result,indent=2));print('GIT_READBACK',commit,len(rows),'PASS')
