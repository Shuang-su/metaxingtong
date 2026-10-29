import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'stage-02-material-candidate'
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'preview'
bpy.ops.wm.open_mainfile(filepath=str(out/'campus-courtyard_material.blend'))
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=24 if mode=='preview' else 64
s.render.resolution_percentage=50 if mode=='preview' else 100
target=out/('previews' if mode=='preview' else 'renders');target.mkdir(exist_ok=True)
cams=['SRC01','SRC02','SRC03','SRC04'] if mode=='preview' else ['MAIN','SRC01','SRC02','SRC03','SRC04']+[o.name for o in s.objects if o.type=='CAMERA' and o.name.startswith('CHECK')]
for name in cams:
    if mode!='preview':
        s.render.resolution_x=1280 if name.startswith('CHECK') else 1920
        s.render.resolution_y=720 if name.startswith('CHECK') else 1080
    s.camera=bpy.data.objects[name];s.render.filepath=str(target/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDER_COMPLETE',name,flush=True)
