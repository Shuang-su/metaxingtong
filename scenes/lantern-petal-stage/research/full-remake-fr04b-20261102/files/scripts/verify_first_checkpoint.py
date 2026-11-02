import bpy,json,hashlib,struct,math
from pathlib import Path
from collections import Counter
D=Path(__file__).resolve().parents[1]
def snapshot():
 out={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  coords=[tuple(o.matrix_world@v.co) for v in o.data.vertices];h=hashlib.sha256()
  for v in coords:h.update(struct.pack('<3f',*v))
  for p in o.data.polygons:
   for i in p.vertices:h.update(struct.pack('<I',i))
  edges=Counter(tuple(sorted((p.vertices[i],p.vertices[(i+1)%len(p.vertices)]))) for p in o.data.polygons for i in range(len(p.vertices)))
  out[o.name]={'geometry_sha256':h.hexdigest(),'bounds':[[min(v[i] for v in coords) for i in range(3)],[max(v[i] for v in coords) for i in range(3)]],'non2_edges':sum(v!=2 for v in edges.values())}
 return out
report={};ref=None
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/FR01_{typ}.blend'));a=snapshot();ref=a if ref is None else ref;report[typ]={'mesh_count':len(a),'same_as_material_geometry':{k:v['geometry_sha256'] for k,v in a.items()}=={k:v['geometry_sha256'] for k,v in ref.items()},'closed_individual_meshes':all(v['non2_edges']==0 for v in a.values()),'bad_edge_meshes':[k for k,v in a.items() if v['non2_edges']]}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/f'models/FR01_{typ}.glb'));b=snapshot();common=set(a)&set(b);delta=max(abs(a[n]['bounds'][i][j]-b[n]['bounds'][i][j]) for n in common for i in range(2) for j in range(3));report[typ]['actual_glb_roundtrip']={'mesh_count':len(b),'missing':list(set(a)-set(b)),'extra':list(set(b)-set(a)),'max_world_bbox_delta':delta}
report['known_support_gap_audit']=[{'row':n,'radius':r,'roof_underside_z':4.4+.45*math.sin(math.pi*(r-6.95)/(9.8-6.95))-.14,'support_top_z':4.37,'positive_gap':4.4+.45*math.sin(math.pi*(r-6.95)/(9.8-6.95))-.14-4.37} for n,r in [('IN',7.3),('OUT',9.2)]];report['scope']='individual closure and transport are not all contacts/source validation; analytical roof support gap found, requires FR02 repair rather than hiding failure'
(D/'qa/FR01-technical-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
