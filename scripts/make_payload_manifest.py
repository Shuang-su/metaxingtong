from pathlib import Path
import hashlib,json,subprocess
r=Path(__file__).resolve().parents[1];out=r/'docs/payload-manifest.json';rows=[]
for p in sorted(r.rglob('*')):
 if not p.is_file() or '.git' in p.parts or p==out:continue
 rows.append({'path':str(p.relative_to(r)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'git_blob':subprocess.check_output(['git','hash-object',str(p)],text=True).strip()})
out.write_text(json.dumps({'scope':'All working-tree payload files excluding this manifest itself and .git; external frozen-tree manifest supplies self hash after commit','files':rows},indent=2))
