import bpy,json,hashlib
from pathlib import Path
V=Path(__file__).resolve().parents[1];R=V.parents[1]
def snapshot(file):
 bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;out={}
 for o in s.objects:
  if o.type!='MESH':continue
  out[o.name]={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'matrix':[list(r) for r in o.matrix_world],'materials':[]}
  for m in o.data.materials:
   p=m.node_tree.nodes.get('Principled BSDF');out[o.name]['materials'].append({'name':m.name,'base':list(p.inputs['Base Color'].default_value),'metal':p.inputs['Metallic'].default_value,'roughness':p.inputs['Roughness'].default_value})
 return out
out={}
for v in ['material','white']:
 a=snapshot(R/f'versions/V02/models/phone-{v}.blend');b=snapshot(V/f'models/phone-{v}.blend');out[v]={'exact_geometry_transform_materials_unchanged':a==b,'mesh_count':len(a),'v02_mesh_state_sha256':hashlib.sha256(json.dumps(a,sort_keys=True).encode()).hexdigest(),'v03_mesh_state_sha256':hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest()}
json.dump(out,open(V/'qa/unchanged-geometry.json','w'),indent=2)
