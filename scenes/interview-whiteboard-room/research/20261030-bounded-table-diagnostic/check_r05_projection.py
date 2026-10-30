"""Run in Blender with frozen material file, read only; write one new QA JSON."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
cfg=json.loads((ROOT/'docs/camera-fit-r03.json').read_text());g=cfg['geometry']
scene=bpy.context.scene
points=[]
for name in ['TABLE.wood-top','TABLE.leg-LF','TABLE.leg-RF','TABLE.pad-LF','TABLE.pad-RF']:
    o=bpy.data.objects[name]
    world=[o.matrix_world@Vector(c) for c in o.bound_box]
    bounds=[[min(v[a] for v in world) for a in range(3)],[max(v[a] for v in world) for a in range(3)]]
    points.append(dict(object=name,bounds=bounds))
tc=[[g['table_x']+sx*g['table_width']/2,g['table_y']+sy*g['table_depth']/2,g['table_z']] for sx,sy in [(-1,1),(1,1),(-1,-1),(1,-1)]]
feet=[[g['table_x']+sx*(g['table_width']/2-.065),g['table_y']-g['table_depth']/2+.052,0] for sx in [-1,1]]
views={}
for view,camera_name in [('front','SOURCE front 1283.813032'),('oblique','SOURCE oblique 1505.632497')]:
    c=bpy.data.objects[camera_name]
    coords=[world_to_camera_view(scene,c,Vector(p)) for p in tc+feet]
    views[view]=dict(camera_location=list(c.location),lens_mm=c.data.lens,projections_px=[[float(p.x*1920),float((1-p.y)*1080)] for p in coords])
out=dict(input_blend=bpy.data.filepath,read_only=True,rendered=False,saved_blend=False,boxes=points,views=views)
(HERE/'blender-readonly-baseline.json').write_text(json.dumps(out,indent=2)+'\n')
print('READ_ONLY_BASELINE_COMPLETE')
