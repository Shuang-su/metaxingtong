import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/"checkpoint_r05c"
def geomhash():
 h=hashlib.sha256()
 for o in sorted((o for o in s.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode());h.update(struct.pack('<16f',*[x for row in o.matrix_world for x in row]))
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
  for u in o.data.uv_layers:
   for d in u.data:h.update(struct.pack('<2f',*d.uv))
 return h.hexdigest()

rows=[];exports=[]
for kind in ['material','white']:
 p=next(O.glob(f'train_r05c_{kind}_candidate_*.blend'));bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;gh=geomhash();h=hashlib.sha256(p.read_bytes()).hexdigest();rows.append({'kind':kind,'file':str(p),'sha256':h,'bytes':p.stat().st_size,'geometry_topology_uv_hash':gh})
 out=O/f'train_r05c_{kind}_candidate.glb'
 if kind=='white':
  bpy.ops.object.select_all(action='DESELECT')
  for o in s.objects:
   if o.type in ['MESH','CAMERA']:o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
 exports.append({'kind':kind,'file':str(out),'input_blend_sha256':h,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'format':'Original Blender glTF export; no optimization/decimation/repacking'})
assert rows[0]['geometry_topology_uv_hash']==rows[1]['geometry_topology_uv_hash']
manifest={'status':'r05C shared proportion improvement checkpoint; source fit NOT accepted; r03 Library and CURRENT unchanged','blends':rows,'exports':exports,'same_geometry_topology_uv':True,'file_limit_scope':'18MB applies to individual semantic delivery ZIP; original inner GLB preserved'};(O/'checkpoint_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
