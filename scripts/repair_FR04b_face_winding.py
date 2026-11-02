# Exact independently identified shell list only. Vertices and cameras/layout must remain identical.
import bpy,bmesh,json,hashlib,struct
from pathlib import Path
D=Path(__file__).resolve().parents[1];audit=json.load(open(D/'qa/independent-winding-audit-FR04-failed.json'));names=[x['name'] for x in audit['FR04']['meshes']];assert len(names)==12;bpy.ops.wm.open_mainfile(filepath=str(D/'models/FR04_material.blend'));s=bpy.context.scene
vs=lambda o:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest()
faces=lambda o:hashlib.sha256(str([list(p.vertices) for p in o.data.polygons]).encode()).hexdigest()
before={o.name:(vs(o),faces(o)) for o in s.objects if o.type=='MESH'};cams={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='CAMERA'};changed=[]
for name in names:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bad_before=sum(e.is_manifold and not e.is_contiguous for e in bm.edges);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.normal_update()
 bad_after=sum(e.is_manifold and not e.is_contiguous for e in bm.edges);volume=bm.calc_volume(signed=True);assert bad_after==0 and volume>0;(bm.to_mesh(o.data));bm.free();o.data.update();assert vs(o)==before[name][0];changed.append({'name':name,'inconsistent_shared_edges_before':bad_before,'after':bad_after,'positive_signed_volume':volume,'vertices_byte_identical':True})
after={o.name:(vs(o),faces(o)) for o in s.objects if o.type=='MESH'};unchanged={n:after[n]==v for n,v in before.items() if n not in names};report={'scope':'only face winding on exact12 independently identified shells','changes':changed,'all_other_mesh_vertices_and_face_indices_unchanged':all(unchanged.values()),'all_mesh_vertices_unchanged':all(after[n][0]==v[0] for n,v in before.items()),'camera_matrices_identical':cams=={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='CAMERA'},'no_source_acceptance':True,'FR04_failed_retained':True};(D/'qa/FR04b-face-winding-repair.json').write_text(json.dumps(report,indent=2))
for typ in ['material','white']:
 if typ=='white':
  m=bpy.data.materials.get('WHITE_SHARED') or bpy.data.materials.new('WHITE_SHARED');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/FR04b_{typ}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/FR04b_{typ}.glb'),export_format='GLB')
files=[]
for f in sorted((D/'models').glob('FR04b*')):files.append({'file':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(D/'qa/FR04b-checkpoint-files.json').write_text(json.dumps(files,indent=2));print('FR04b saved')
