import bpy,json,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'deliverables';item=next(x for x in json.loads((R/'frozen_r03/freeze_manifest.json').read_text())['blends'] if x['kind']=='material')
def snap():
 out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  m=o.data;nm=o.matrix_world.to_3x3().inverted().transposed();d={}
  cn=[x.vector.copy() for x in m.corner_normals]
  for i,l in enumerate(m.loops):
   v=o.matrix_world@m.vertices[l.vertex_index].co;n=(nm@cn[i]).normalized();p=tuple(round(float(a),4) for a in v);t=tuple(n)
   d.setdefault(p,set()).add(t)
  out[o.name]=d
 return out
bpy.ops.wm.open_mainfile(filepath=item['file']);a=snap();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'03_train_material.glb'));b=snap();rows=[]
for name,x in a.items():
 y=b[name];bestmax=0;missing=0;over=0
 for p,q in [(x,y),(y,x)]:
  for key,ns in p.items():
   qs=q.get(key)
   if not qs:missing+=1;continue
   for n in ns:
    dot=max(sum(u*v for u,v in zip(n,m)) for m in qs);angle=math.degrees(math.acos(max(-1,min(1,dot))));bestmax=max(bestmax,angle);over+=angle>.25
 rows.append({'name':name,'max_best_matching_normal_angle_degrees_both_directions':bestmax,'normals_over_0_25deg':over,'missing_position_keys':missing})
report={'input_blend_sha256':item['sha256'],'gltf_sha256':hashlib.sha256((O/'03_train_material.glb').read_bytes()).hexdigest(),'method':'For each unique normal at world vertex rounded1e-4, choose closest-angle normal at same reimport position; check both directions. Rounding equality differences separately retained.','max_angle_deg':max(r['max_best_matching_normal_angle_degrees_both_directions'] for r in rows),'total_normals_over_0_25deg':sum(r['normals_over_0_25deg'] for r in rows),'missing_position_keys':sum(r['missing_position_keys'] for r in rows),'objects_over_0_25deg':[r for r in rows if r['normals_over_0_25deg']],'per_object':rows};(O/'normal_angle_roundtrip.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='per_object'},indent=2))
