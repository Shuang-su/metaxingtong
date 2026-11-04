import bpy,pathlib,json
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-observatory-source15-qa-20261104');t=json.loads((Q/'trial18-correspondences.json').read_text());e=Matrix(t['camera']['camera_rotation']).to_4x4();e.translation=Vector(t['camera']['camera_position']);out={}
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/f'R08_{mode}.blend'));s=bpy.context.scene;c=bpy.data.objects['SOURCE_15_exterior'];s.render.resolution_x=1192;s.render.resolution_y=671;s.render.resolution_percentage=100;errs=[]
 for p in t['points']:
  v=world_to_camera_view(s,c,Vector(p['world_target']));errs.extend(abs(a-b) for a,b in zip([1192*v.x,671*(1-v.y)],p['projected_pixel']))
 out[mode]={'matrix_delta':max(abs(c.matrix_world[i][j]-e[i][j]) for i in range(4)for j in range(4)),'lens':c.data.lens,'max_point_projection_delta_px':max(errs)}
(Q/'R08-saved-camera-check.json').write_text(json.dumps(out,indent=2));print(out)
