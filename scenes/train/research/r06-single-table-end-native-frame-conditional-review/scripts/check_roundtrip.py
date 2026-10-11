import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];out=[]
for f in sorted(P.glob('*.glb')):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(f));meshes=[o for o in bpy.data.objects if o.type=='MESH'];tri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
 bad=[]
 for o in meshes:
  for v in o.data.vertices:
   if any(not __import__('math').isfinite(x) for x in v.co):bad.append(o.name)
 table=[o for o in meshes if o.name.startswith('Booth -1 1 rounded wood table')];objs=[]
 for o in table:
  vs=[o.matrix_world@v.co for v in o.data.vertices];objs.append({'name':o.name,'bounds':[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)],'uv_layers':len(o.data.uv_layers),'materials':[m.name for m in o.data.materials]})
 out.append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_count':len(meshes),'triangles':tri,'finite_coordinates':not bad,'table':objs,'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images]})
(P/'glb_reimport_verification.json').write_text(json.dumps(out,indent=2))
