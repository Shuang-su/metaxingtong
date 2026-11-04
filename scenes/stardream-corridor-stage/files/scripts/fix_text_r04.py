import bpy,bmesh,json,pathlib,hashlib
P=pathlib.Path(__file__).resolve().parents[1];records={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R03_{mode}.blend'));o=bpy.data.objects['ONAIR_text'];bm=bmesh.new();bm.from_mesh(o.data)
 def audit():return {'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume':float(bm.calc_volume(signed=True))}
 before=audit();bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));after=audit();bm.to_mesh(o.data);bm.free();o.data.update();o['topology_repair']='Weld coincident glyph extrusion cap/side vertices within1e-6, recalc outward face normals. Original font failure retained R01-R03.';bpy.context.view_layer.update();f=P/'models'/f'R04_{mode}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(f));bpy.ops.export_scene.gltf(filepath=str(P/'models'/f'R04_{mode}.glb'),export_format='GLB',export_cameras=True,export_extras=True);records[mode]={'before':before,'after':after,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(P/'qa/R04-text-repair.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
