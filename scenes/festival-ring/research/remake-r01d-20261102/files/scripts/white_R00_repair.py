import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[1];o=r/'versions/R00';bpy.ops.wm.open_mainfile(filepath=str(o/'ring-remake-R00-platforms.blend'));s=bpy.context.scene
m=bpy.data.materials.new('white_diagnostic_saved');m.use_nodes=True;m.diffuse_color=(.65,.65,.65,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.65,.65,.65,1);bs.inputs['Roughness'].default_value=.7;m.use_fake_user=True;s.view_layers[0].material_override=m
bpy.ops.wm.save_as_mainfile(filepath=str(o/'ring-remake-R00-white-same-geometry.blend'));s.render.filepath=str(o/'R00-platform-only-white-960.png');bpy.ops.render.render(write_still=True)
