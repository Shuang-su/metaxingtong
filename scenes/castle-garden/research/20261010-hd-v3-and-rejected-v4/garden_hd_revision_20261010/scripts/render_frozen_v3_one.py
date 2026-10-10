import bpy,json,hashlib,sys
from pathlib import Path
R=Path('/workspace/scratch/fa58bfcf0425/garden_hd_revision_20261010');frozen=R/'models/Garden_HD_Conservative_v3_Frozen.blend'
fits=json.load(open(R/'qa/joint_candidate_v3_conservative.json'))['fits'];sha=hashlib.sha256(frozen.read_bytes()).hexdigest()
tag=sys.argv[sys.argv.index('--')+1]

# Reload the exact frozen bytes before every render.
bpy.ops.wm.open_mainfile(filepath=str(frozen));s=bpy.context.scene;s.camera=bpy.data.objects[tag];s.render.filepath=str(R/'renders'/f'conservative_v3_{tag}.png');bpy.ops.render.render(write_still=True)
out=Path(s.render.filepath);info={'input_blend':str(frozen),'input_sha256':sha,'post_input_sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'camera':tag,'matrix_world':[list(v) for v in s.camera.matrix_world],'lens_mm':s.camera.data.lens,'sensor_width':s.camera.data.sensor_width,'shift_y':s.camera.data.shift_y,'camera_identification':'HD principal point unknown, diagnostic feasible camera; not recovered original','resolution':[1180,664],'shared_geometry_materials_lights':True,'fit_snapshot':next((d for d in fits if d['tag']==tag),None),'geometry_changes':True,'threads':3,'samples':16}
json.dump(info,open(R/'renders'/f'conservative_v3_{tag}.camera.json','w'),ensure_ascii=False,indent=2)