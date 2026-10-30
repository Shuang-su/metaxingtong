"""Index original files by size/SHA256/Git blob ID. No archive or network action."""
from pathlib import Path
import hashlib,json,subprocess
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name=='file-index.json':continue
 data=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 actual=subprocess.check_output(['git','hash-object',str(p)],text=True).strip();assert blob==actual
 rows.append({'path':str(p.relative_to(ROOT)),'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':blob})
out={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'all scene ordinary files except this self-referential index and caches','count':len(rows),'total_bytes':sum(r['size_bytes'] for r in rows),'max_file_bytes':max(r['size_bytes'] for r in rows),'files':rows}
(ROOT/'file-index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='files'}))
