import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];Q=D/'qa/R07_lantern'
def snap():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  p=[o.matrix_world@v.co for v in o.data.vertices];out[o.name]={'bounds':[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]],'geo':hashlib.sha256(str(([list(v.co) for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons],[list(r) for r in o.matrix_world])).encode()).hexdigest()}
 return out
result={};original={}
for typ in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R07b_lantern_trial_{typ}.blend'));original[typ]=a=snap();top={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name.startswith(('LANTERN_round_R0','LANTERN_string0_10')):continue
  uses={}
  for f in o.data.polygons:
   for e in f.edge_keys:uses[e]=uses.get(e,0)+1
  top[o.name]={'boundary_edges':sum(x==1 for x in uses.values()),'nonmanifold_edges':sum(x!=2 for x in uses.values())}
 result[typ+'_detail_topology']=top
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/f'models/R07b_lantern_trial_{typ}.glb'));b=snap();common=set(a)&set(b);result[typ+'_roundtrip']={'source_count':len(a),'reimport_count':len(b),'missing':sorted(set(a)-set(b)),'extra':sorted(set(b)-set(a)),'max_bbox_error':max(abs(a[n]['bounds'][j][k]-b[n]['bounds'][j][k]) for n in common for j in range(2) for k in range(3))}
result['same_white_material_geometry']=original['material']==original['white'];result['scope']='transport and edge closure only; collars/ribs intentionally overlap body; no exhaustive source acceptance or intersection certification'
(Q/'R07b-roundtrip.json').write_text(json.dumps(result,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(D/'models/R07_lantern_trial_material.blend'));base=snap();cam0={o.name:([list(r) for r in o.matrix_world],o.data.lens) for o in bpy.context.scene.objects if o.type=='CAMERA'}
centre0={o.name:[list(sum([o.matrix_world@v.co for v in o.data.vertices][i:i+8],Vector())/8) for i in range(0,len(o.data.vertices),8)] for o in bpy.context.scene.objects if '_rib_' in o.name}
bpy.ops.wm.open_mainfile(filepath=str(D/'models/R07b_lantern_trial_material.blend'));now=snap();cam1={o.name:([list(r) for r in o.matrix_world],o.data.lens) for o in bpy.context.scene.objects if o.type=='CAMERA'};centre1={o.name:[list(sum([o.matrix_world@v.co for v in o.data.vertices][i:i+8],Vector())/8) for i in range(0,len(o.data.vertices),8)] for o in bpy.context.scene.objects if '_rib_' in o.name}
result['unchanged_non_rib_meshes']=all(now[n]==v for n,v in base.items() if '_rib_' not in n);result['source_cameras_unchanged']=all(cam0[n]==cam1[n] for n in cam0 if n.startswith('SOURCE'));result['rib_section_centre_max_delta']=max(abs(centre0[n][i][k]-centre1[n][i][k]) for n in centre0 for i in range(len(centre0[n])) for k in range(3));(Q/'R07b-roundtrip.json').write_text(json.dumps(result,indent=2))
