import bpy,json
from pathlib import Path
r=Path('/workspace/scratch/fa58bfcf0425/hospital_object_audit/candidate')
m=bpy.data.materials.new('Diagnostic white - same candidate geometry');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.74,.74,.74,1);p.inputs['Roughness'].default_value=.8
count=0
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m);count+=1
bpy.ops.wm.save_as_mainfile(filepath=str(r/'hospital_endboard_shape_candidate_white.blend'));bpy.ops.export_scene.gltf(filepath=str(r/'hospital_endboard_shape_candidate_white.glb'),export_format='GLB',use_selection=False)
(r/'white_variant_note.json').write_text(json.dumps({'changed_material_objects':count,'geometry_changed':False,'purpose':'Same geometry white model; material replacement only, no camera-dependent changes'},indent=2))
