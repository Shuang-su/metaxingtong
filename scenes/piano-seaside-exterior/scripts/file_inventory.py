from pathlib import Path
import hashlib,json,datetime
root=Path(__file__).resolve().parents[1]
files=[]
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.suffix=='.blend1' or '__pycache__' in p.parts or p.name in ['file-manifest.json','local-commit-readback.json']:continue
 b=p.read_bytes();files.append({'path':str(p.relative_to(root.parent.parent)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()})
out={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'local conditional candidate; no remote upload/push claimed','excluded':['file-manifest.json (self)','local-commit-readback.json (post-commit audit)','Blender .blend1 backups and __pycache__'],'files':files}
(root/'file-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(len(files),'files',sum(x['bytes'] for x in files),'bytes',max(x['bytes'] for x in files),'largest')
