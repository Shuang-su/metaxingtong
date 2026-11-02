import bpy,os,json,math,hashlib
from pathlib import Path
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[-6:]))
D=Path(__file__).resolve().parents[1];records={}
for mode in['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R05_{mode}.blend'));ground=bpy.data.objects['GROUND_finite_work_extent'];stage=bpy.data.objects['STAGE_shared_rounded_lobes'];maxr=max(math.hypot(*(stage.matrix_world@v.co)[:2])for v in stage.data.vertices);radius=math.ceil((maxr+.5)*10)/10
 for v in ground.data.vertices:v.co.x*=radius/8;v.co.y*=radius/8
 ground['evidence']=f'R06 inferred finite working ground radius{radius}; covers extended working stage closure. NOT observed front hall/coastline extent.'
 bpy.context.scene['R06_status']='R05 same source geometry/cameras; ONLY inferred work ground extent corrected after107 unsupported stage samples. Source still not accepted.'
 records[mode]={'old_ground_radius':8,'stage_max_radius':maxr,'new_ground_radius':radius,'other_geometry_and_cameras_unchanged':True,'reason':'Independent R05 1057stage hits/107uncovered by workingground; source-visible scene NOT validated by this engineering extent change'}
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R06_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R06_{mode}.glb'),export_format='GLB',export_cameras=True,export_lights=False)
(D/'models/R06-extent-change.json').write_text(json.dumps(records,indent=2));print('R06_SAVED')
