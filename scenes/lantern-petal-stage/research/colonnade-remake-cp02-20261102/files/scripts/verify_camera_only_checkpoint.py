import bpy,json,hashlib,struct
from pathlib import Path
D=Path(__file__).resolve().parents[1]
def sig(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));r={}
 for o in bpy.data.objects:
  if o.type=='MESH':
   h=hashlib.sha256()
   for v in o.data.vertices:
    for x in o.matrix_world@v.co:h.update(struct.pack('<f',x))
   for f in o.data.polygons:
    for i in f.vertices:h.update(struct.pack('<I',i))
   r[o.name]=h.hexdigest()
 return r
r={}
for typ in ['material','white']:
 a=sig(D/f'models/NOV2_CP01_{typ}.blend');b=sig(D/f'models/NOV2_CP02_workcamera_{typ}.blend');r[typ]={'mesh_counts':[len(a),len(b)],'world_vertex_polygon_signatures_identical':a==b,'changed':[k for k in set(a)|set(b) if a.get(k)!=b.get(k)]}
(D/'qa/CP02-camera-only-geometry-check.json').write_text(json.dumps(r,indent=2));print(r)
