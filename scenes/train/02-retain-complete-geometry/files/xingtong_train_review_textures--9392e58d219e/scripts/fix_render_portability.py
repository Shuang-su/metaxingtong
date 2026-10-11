import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for f in ['01_train_material.blend','02_train_white.blend']:
 p=R/'deliverables'/f;bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.scene.cycles.use_denoising=False;bpy.context.scene.cycles.samples=32;bpy.context.scene['Denoising_note']='Scene renders without OIDN dependency. Review PNGs may be separately denoised without geometric transforms.';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
