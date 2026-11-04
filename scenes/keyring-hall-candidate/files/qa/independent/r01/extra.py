import bpy,json,bmesh,hashlib
from pathlib import Path
O=Path(__file__).parent;R=O/'frozen/models';result={}
for variant in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'keyring-{variant}.blend'));s=bpy.context.scene
 cams={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='CAMERA'}
 raw=[]
 for o in s.objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);raw.append({'name':o.name,'raw_nonmanifold':sum(not e.is_manifold for e in bm.edges),'raw_degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'modifiers':[(m.name,m.type) for m in o.modifiers]});bm.free()
 pairs={}
 for a,b in [('piano-soundboard','piano-body-rim'),('piano-open-lid','piano-body-rim'),('four-point-concave-floor-inlay','stage-central-solid'),('white-key-00','stage-outer-floor'),('white-key-18','stage-outer-floor')]:
  v=lambda n:[o.matrix_world@x.co for o in [s.objects[n]] for x in o.data.vertices]
  va,vb=v(a),v(b);pairs[a+' -> '+b]={'upper_object_minZ':min(p.z for p in va),'lower_object_maxZ':max(p.z for p in vb),'strict_z_separation':min(p.z for p in va)-max(p.z for p in vb)}
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/f'keyring-{variant}.glb'))
 ce={n:max(abs(bpy.data.objects[n].matrix_world[i][j]-m[i][j]) for i in range(4) for j in range(4)) for n,m in cams.items()}
 result[variant]={'raw_mesh_audit':raw,'strict_z_bounds':pairs,'camera_matrix_max_errors':ce}
(O/'extra.json').write_text(json.dumps(result,indent=2))
