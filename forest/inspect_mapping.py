import bpy,json,pathlib,math
from bpy_extras.object_utils import world_to_camera_view
R=pathlib.Path('/workspace/scratch/fa58bfcf0425');bpy.ops.wm.open_mainfile(filepath=str(R/'forest-diagnostic-replay-20261104/models/R15_log-contact-diagnostic_material.blend'));s=bpy.context.scene
obs={'3032_blue_central':[632,557],'3042_blue_left':[132,540],'3042_blue_rear_left':[778,472],'3042_blue_rear_right':[858,497]}
rows=[]
for i in range(11):
 o=bpy.data.objects[f'FLOWER_{i:02d}_centre'];p=o.matrix_world.translation;pet=bpy.data.objects[f'FLOWER_{i:02d}_petal_0'];row={'id':i,'world':list(p),'petal_materials':[m.name for m in pet.data.materials],'projections':{}}
 for c in sorted([c for c in s.objects if c.type=='CAMERA' and c.name.startswith('SOURCE_')],key=lambda c:c.name):
  q=world_to_camera_view(s,c,p);xy=[1212*q.x,39+681*(1-q.y)]
  row['projections'][c.name]={'viewport_xy_hypothesis':xy,'depth':q.z,'residual_to_unmatched_observations_px':{k:math.dist(xy,v) for k,v in obs.items()}}
 rows.append(row)
out={'warning':'No SOURCE camera is verified for 3032/3042. Residuals are counterfactual arithmetic, not source alignment or identity evidence. No minimum chosen. Projection into assumed content rectangle x=0,y=39,w=1212,h=681 of 1212x774 viewport; source content rect not calibrated.','observations_approximate_px':obs,'scene_render_aspect':[s.render.resolution_x,s.render.resolution_y],'flowers':rows}
(R/'forest-stamen-readonly-notes-20261105/mapping-projections.json').write_text(json.dumps(out,indent=2))
for r in rows:print(r['id'],r['world'],r['petal_materials'],{k:[round(v) for v in p['viewport_xy_hypothesis']] for k,p in r['projections'].items()})
