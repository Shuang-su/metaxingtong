import json,struct,pathlib,hashlib
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105/models');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-qa-20261105');r={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for ext in ['blend','glb']:r['material_'+ext]={'sha04':sha(P/f'R04_material.{ext}'),'sha05':sha(P/f'R05_material.{ext}'),'byte_equal':(P/f'R04_material.{ext}').read_bytes()==(P/f'R05_material.{ext}').read_bytes()}
def load(p):
 b=p.read_bytes();ln=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+ln]),b[28+ln:]
a,ab=load(P/'R04_white.glb');b,bb=load(P/'R05_white.glb');diff=[]
def rec(a,b,path):
 if type(a)!=type(b):diff.append([path,a,b]);return
 if isinstance(a,dict):
  for k in a.keys()|b.keys():
   if k not in a or k not in b:diff.append([path+'/'+k,a.get(k),b.get(k)])
   else:rec(a[k],b[k],path+'/'+k)
 elif isinstance(a,list):
  if len(a)!=len(b):diff.append([path+'/len',len(a),len(b)])
  else:
   for i,(x,y) in enumerate(zip(a,b)):rec(x,y,path+'/'+str(i))
 elif a!=b:diff.append([path,a,b])
rec(a,b,'');r['white_glb']={'sha04':sha(P/'R04_white.glb'),'sha05':sha(P/'R05_white.glb'),'json_diff':diff,'binary_chunk_equal':ab==bb}
(Q/'R05-glb-byte-diff.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
