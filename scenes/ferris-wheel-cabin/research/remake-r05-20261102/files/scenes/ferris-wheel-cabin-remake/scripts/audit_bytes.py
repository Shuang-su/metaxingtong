from pathlib import Path
import subprocess,hashlib,json
R=Path(__file__).resolve().parents[3];head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();files=subprocess.check_output(['git','ls-tree','-r','--name-only',head],cwd=R,text=True).splitlines();rows=[]
for f in files:
 data=(R/f).read_bytes();committed=subprocess.check_output(['git','show',head+':'+f],cwd=R);assert data==committed
 rows.append({'path':f,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),'HEAD_byte_equal':True})
p=R.parent/'ferris-remake-local-byte-receipt-20261102.json';p.write_text(json.dumps({'head':head,'files':rows,'scope':'actual local HEAD readback, NOT remote verification'},indent=2));print(head,len(rows),p)
