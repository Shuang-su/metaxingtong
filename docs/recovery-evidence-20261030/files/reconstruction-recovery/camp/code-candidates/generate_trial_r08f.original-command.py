s=open('scripts/trial_r08e_shared_edges.py').read();tail=s[s.index("s.render.threads_mode='FIXED'"):].replace('R08e','R08f').replace('R08E','R08F')
head='''import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];out=r/'qa/R08_trial';bpy.ops.wm.open_mainfile(filepath=str(r/'models/R08e_shared_edges_trial.blend'));s=bpy.context.scene
q=json.load(open(out/'R08e_report.json'));old=Vector((-3.3,9.5,3.89));delta=old-Vector(q['left_eave_working_xyz'])
for i in [0,5]:
 for prefix,N,M in [('T01_roof_panel_',14,12),('T01_skirt_panel_',16,16)]:
  o=bpy.data.objects[f'{prefix}{i:02}']
  for v in o.data.vertices:
   a,b=divmod(v.index,N+1);t=a/M;u=b/N;v.co+=delta*t*((1-u) if i==0 else u)
for i,a,b in [(0,old,Vector((-.5396,8.1541,3.8916))),(5,Vector((-1.99651054,10.,5.49581436)),old)]:
 o=bpy.data.objects[f'T01_roof_hem_{i}'];o.location=(a+b)/2;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.dimensions.z=(b-a).length
(out/'R08f_report.json').write_text(json.dumps({'action':'rollback failed R08e left-eave joint correspondence only','reason':'ray separation .371, ~13-15px residual, folded roof dark triangle; do not optimize cameras to hide failure','retained':'R08b conditional roof area, .10 shared top-edge sag, R08d chair sag, right-only bag contraction, bands ground correction and duplicate cap weld','left_eave':'old R07 position preserved and known incorrect, not accepted','not_accepted':True},indent=2));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'models/R08f_partial_geometry.blend'))
'''
open('scripts/trial_r08f_rollback_invalid_eave.py','w').write(head+tail)
