import bpy,json,hashlib,struct
from pathlib import Path
r=Path(__file__).resolve().parents[1];d={}
for fn in ['ring-remake-R00-platforms.blend','ring-remake-R00-white-same-geometry.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(r/'versions/R00'/fn));h=hashlib.sha256();names=[]
 for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  if o.type!='MESH':continue
  names.append(o.name);h.update(o.name.encode());h.update(repr([list(row) for row in o.matrix_world]).encode());h.update(repr([list(v.co) for v in o.data.vertices]).encode());h.update(repr([list(p.vertices) for p in o.data.polygons]).encode())
 d[fn]={'mesh_count':len(names),'geometry_sha256':h.hexdigest()}
d['equal']=len({v['geometry_sha256'] for v in d.values()})==1;(r/'qa/R00-shared-geometry.json').write_text(json.dumps(d,indent=2));print(d)
