import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'stages/r02-shared-scene';Q=O/'preview';Q.mkdir(exist_ok=True)
for state,cams in [('white',['SOURCE_PREVIEW_FRONT_CONDITIONAL']),('material',['SOURCE_PREVIEW_FRONT_CONDITIONAL','SOURCE_PREVIEW_WIDE_CONDITIONAL'])]:
    bpy.ops.wm.open_mainfile(filepath=str(O/('harbor-scene-r02-'+state+'.blend')));sc=bpy.context.scene;sc.cycles.use_denoising=False;sc.cycles.samples=48;sc.render.resolution_x=768;sc.render.resolution_y=432
    for name in cams:
        sc.camera=bpy.data.objects[name];sc.render.filepath=str(Q/(state+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
