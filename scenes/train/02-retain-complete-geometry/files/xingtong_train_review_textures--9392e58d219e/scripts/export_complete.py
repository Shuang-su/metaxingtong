import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'deliverables';bpy.ops.wm.open_mainfile(filepath=str(O/'01_train_material.blend'));S=bpy.context.scene
for t in list(bpy.data.texts):
 if 'README' in t.name:bpy.data.texts.remove(t)
t=bpy.data.texts.new('README_中文');t.write((R/'README_中文.txt').read_text())
def hashgeom():
 h=hashlib.sha256()
 for o in sorted([o for o in S.objects if o.type=='MESH'],key=lambda a:a.name):
  h.update(o.name.encode());h.update(struct.pack('<16f',*[v for row in o.matrix_world for v in row]));h.update(struct.pack('<%df'%(len(o.data.vertices)*3),*[a for v in o.data.vertices for a in v.co]));h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode())
 return h.hexdigest()
def export(path):
 bpy.ops.object.select_all(action='DESELECT')
 for o in S.objects:
  if o.type in ['MESH','CAMERA']:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
S.camera=bpy.data.objects['INSPECT_01_forward_aisle'];S['Geometry_hash']=hashgeom();bpy.ops.wm.save_as_mainfile(filepath=str(O/'01_train_material.blend'),compress=True);export(O/'03_train_material.glb');h=hashgeom();print('MATERIAL_EXPORT_COMPLETE',h,flush=True)
w=bpy.data.materials.new('White matte inspection material');w.use_nodes=True;b=w.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.66,.66,.66,1);b.inputs['Roughness'].default_value=.82
for o in S.objects:
 if o.type=='MESH' and not any('glazing' in m.name.lower() for m in o.data.materials if m):o.data.materials.clear();o.data.materials.append(w)
 if o.type=='LIGHT':o.data.color=(1,1,1)
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.1,.1,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.12;S.view_settings.exposure=-.15;S['Version']='White model, exact same complete geometry'
bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
assert h==hashgeom();bpy.ops.wm.save_as_mainfile(filepath=str(O/'02_train_white.blend'),compress=True);export(O/'04_train_white.glb')
a=json.loads((O/'verification.json').read_text());a['white_geometry_sha256']=hashgeom();a['same_interior_geometry']=a['white_geometry_sha256']==a['geometry_sha256'];(O/'verification.json').write_text(json.dumps(a,indent=2));print('ALL_EXPORTS_COMPLETE',flush=True)
