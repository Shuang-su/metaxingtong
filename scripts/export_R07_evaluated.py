import bpy,os,json,hashlib
from pathlib import Path
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[-6:]))
D=Path(__file__).resolve().parents[1];records={}
for mode in['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R06_{mode}.blend'));s=bpy.context.scene;s['R07_export_fix']='export_apply=True ensures umbrella Solidify evaluated thickness; geometry and cameras otherwise unchanged from R06.'
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R07_{mode}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(D/f'models/R07_{mode}.glb'),export_format='GLB',export_cameras=True,export_lights=False,export_apply=True)
 records[mode]={'base':'R06','export_apply':True,'reason':'Independent R05/06 default GLB omitted Solidify underside,49 evaluated vertices differed,max .00800016 workingunits','geometry_and_cameras_unchanged_from_R06':True,'blend_sha256':hashlib.sha256((D/f'models/R07_{mode}.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((D/f'models/R07_{mode}.glb').read_bytes()).hexdigest()}
(D/'models/R07-export-record.json').write_text(json.dumps(records,indent=2));print('R07_SAVED')
