import bpy,pathlib,json
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-qa-20261105');r={}
def snap():
 o=bpy.data.objects['FLOOR_finite_slab'];uv=o.data.uv_layers.active;return sorted(set(tuple(round(x,5) for x in list(o.matrix_world@o.data.vertices[l.vertex_index].co)+list(uv.data[l.index].uv)) for l in o.data.loops))
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R06_{mode}.blend'));a=snap();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/'models'/f'R06_{mode}.glb'));b=snap();r[mode]={'world_corner_uv_pairs_equal_rounded_1e5':a==b,'counts':[len(a),len(b)],'original_pairs':a,'imported_pairs':b}
(Q/'R06-floor-uv-roundtrip.json').write_text(json.dumps(r,indent=2));print('DONE')
