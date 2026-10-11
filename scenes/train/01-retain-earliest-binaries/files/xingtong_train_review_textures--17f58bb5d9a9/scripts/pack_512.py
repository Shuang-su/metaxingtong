import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'deliverables';T=O/'textures';T.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'01_train_material.blend'));s=bpy.context.scene
for im in bpy.data.images:
 if im.source!='FILE':continue
 stem=Path(im.filepath).name
 if stem.endswith('.png'):
  if 'destination_sign' not in stem:im.scale(512,512)
  im.filepath_raw=str(T/stem);im.file_format='PNG';im.save();im.pack()
s['PBR_maps']='18 original UV PBR maps at 512x512, plus verified station sign image. Packed and external PNGs.';s['Export_note']='512px maps keep each delivery ZIP below 18 MiB. Original work maps were 1024px.'
for t in bpy.data.texts:
 if t.name.startswith('README'):t.clear();t.write((R/'README_中文.txt').read_text().replace('18张1024×1024','18张512×512'))
s.camera=bpy.data.objects['QA_WIDE_FORWARD_FLOOR'];bpy.ops.wm.save_as_mainfile(filepath=str(O/'01_train_material.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if (o.type=='MESH' and not any(c.name.startswith('11_') for c in o.users_collection)) or o.type=='CAMERA':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'03_train_material.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
print('PACKED_512_READY')
# Use the actual final saved file for primary user-facing verification renders.
s.cycles.samples=48;s.render.resolution_percentage=100
for name,fn in [('QA_WIDE_FORWARD_FLOOR','packed_normal_material'),('MATCH_A_15m19_right_booth','packed_A_material'),('MATCH_D_13m59_wide','packed_D_material')]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/'renders'/f'{fn}.png');bpy.ops.render.render(write_still=True)
print('PACKED_RENDER_READY')
