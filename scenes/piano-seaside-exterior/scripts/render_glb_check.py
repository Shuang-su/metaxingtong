import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];stage=sys.argv[-1] if sys.argv[-1].startswith('r') else 'r05'
bpy.ops.wm.open_mainfile(filepath=str(root/'models'/stage/'piano_seaside_material.blend'))
sc=bpy.context.scene
for obj in list(sc.objects):
 if obj.type=='MESH':bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(root/'models'/stage/'piano_seaside_material.glb'))
sc.camera=bpy.data.objects['main'];sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.render.resolution_percentage=100
sc.render.filepath=str(root/'qa'/stage/'glb_reimport_main.png');bpy.ops.render.render(write_still=True)
print('GLB_RENDER_COMPLETE')
