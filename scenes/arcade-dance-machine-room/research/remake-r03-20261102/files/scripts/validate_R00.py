import bpy,json,math
from pathlib import Path
D=Path(__file__).resolve().parents[1]
def snapshot():
 out={};g=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(g);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];edges={}
  for p in m.polygons:
   for a,b in p.edge_keys:edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
  out[o.name]={'vertices':len(vs),'faces':len(m.polygons),'min':[min(v[j]for v in vs)for j in range(3)],'max':[max(v[j]for v in vs)for j in range(3)],'nonfinite':sum(not all(math.isfinite(c)for c in v)for v in vs),'non_two_face_edges':sum(v!=2 for v in edges.values()),'class':o.get('validation_class','unclassified')};e.to_mesh_clear()
 return out
bpy.ops.wm.open_mainfile(filepath=str(D/'models/arcade_remake_R00_material.blend'));a=snapshot();bpy.ops.wm.open_mainfile(filepath=str(D/'models/arcade_remake_R00_white.blend'));b=snapshot();assert a==b
mesh={'finite':all(v['nonfinite']==0 for v in a.values()),'solid_nonmanifold':{n:v['non_two_face_edges']for n,v in a.items()if v['class']=='solid'and v['non_two_face_edges']},'same_material_white_evaluated':True,'mesh_count':len(a),'printed_sheets_excluded_from_closed_volume_requirement':[n for n,v in a.items()if v['class']!='solid']}
assembly=[]
for i in range(1,4):
 p=f'M{i:02d}';pad=a[p+'_pad_base'];pl=a[p+'_plinth'];body=a[p+'_body'];shelf=a[p+'_shelf'];assembly.extend([{'test':p+' pad-floor','gap':pad['min'][2],'expected':0},{'test':p+' plinth-floor','gap':pl['min'][2],'expected':0},{'test':p+' body-plinth','gap':body['min'][2]-pl['max'][2],'expected':0}])
 for side in [-1,1]:assembly.append({'test':p+f' prop-foot-{side}-shelf','gap':a[p+f'_PROP_foot_{side}']['min'][2]-shelf['max'][2],'expected':0})
 assembly.append({'test':p+' pad-cabinet separation','gap':pl['min'][1]-pad['max'][1],'expected':'positive; working gap not source measured'})
reimports=[]
for kind in ['material','white']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(D/f'models/arcade_remake_R00_{kind}.glb'));c=snapshot();missing=sorted(set(a)-set(c));extra=sorted(set(c)-set(a));delta=max(abs(a[n][k][j]-c[n][k][j])for n in set(a)&set(c)for k in ['min','max']for j in range(3));reimports.append({'kind':kind,'mesh_count':len(c),'missing':missing,'extra':extra,'max_bbox_difference':delta})
(D/'qa/mesh_validation_R00.json').write_text(json.dumps(mesh,indent=2));(D/'qa/assembly_validation_R00.json').write_text(json.dumps({'contacts':assembly,'limits':'bbox contact/intentional overlap only, not full collision/clearance proof; shell ray test pending; source dimensions not accepted'},indent=2));(D/'qa/glb_reimport_R00.json').write_text(json.dumps(reimports,indent=2));print(json.dumps({'mesh':mesh,'assembly':assembly,'reimports':reimports}))
