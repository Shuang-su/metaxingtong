"""Blender projection on existing approximate control points, no render or scene rebuild."""
import bpy, json, pathlib, sys, math
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from leaf_local_warp import Parameters, forward

R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
sidecar=json.loads((R/'upstream/models/lakeleaf-r06-cameras.json').read_text())
for row in sidecar['cameras'][:4]:
    d=bpy.data.cameras.new(row['name']);o=bpy.data.objects.new(row['name'],d);s.collection.objects.link(o)
    for k,v in row['data'].items():setattr(d,k,v)
    o.matrix_world=Matrix(row['matrix_world'])
bpy.context.view_layer.update()
def project(camera,p):
    a=world_to_camera_view(s,bpy.data.objects[camera],Vector(p))
    return [a.x*3840,(1-a.y)*2160]

old=json.loads((R/'upstream/qa/r06/conditional-landmarks.json').read_text())
landmarks=[]
for row in old['rows']:
    p=(-4.65,0,2.34) if row['point']=='left_apex' else (4.65,0,1.69)
    actual=project(row['camera'],p)
    landmarks.append(dict(**row,world_control_point=p,recomputed_px=actual,
        difference_from_archived_projection_px=math.dist(actual,row['render_predicted_px'])))
assert max(x['difference_from_archived_projection_px'] for x in landmarks)<.001
def original_point(u,v):
    width=1.58*max(0,1-u*u)**.72*(1+.06*math.sin(3*math.pi*u))
    z=.20+(2.30 if u<0 else 1.65)*abs(u)**3+.75*v*v*(1-abs(u)**1.1)+.045*math.sin(8*math.pi*u+v*.8)*abs(v)**3*max(0,1-u*u)-.16
    return [4.65*u,width*v,z]
probes=[('middle_center',original_point(0,0)),('middle_front_edge',original_point(0,-1)),
    ('left_shoulder_front',original_point(-.68,-1)),('left_shoulder_back',original_point(-.68,1))]
variants=[('baseline',Parameters()),('belly_down_008',Parameters(belly_dz=-.08)),('belly_up_008',Parameters(belly_dz=.08)),
    ('shoulder_wider_008',Parameters(shoulder_fraction=.08)),('shoulder_narrower_control_008',Parameters(shoulder_fraction=-.08))]
rows=[]
for name,params in variants:
    params.validate()
    for camera in [r['name'] for r in sidecar['cameras'][:4]]:
        for label,p in probes:
            a=project(camera,p);b=project(camera,forward(p,params))
            rows.append(dict(trial=name,camera=camera,probe=label,baseline_world=p,baseline_px=a,trial_px=b,delta_px=[b[i]-a[i] for i in range(2)]))
out=R/'qa';out.mkdir(exist_ok=True)
(out/'projection-sensitivity.json').write_text(json.dumps(dict(
    scope='Original 13-camera sidecar text, four original approximate tip marks and analytic surface probes. No original mesh recovery, source-image fit or full silhouette metric.',
    fixed_original_head='8a6c541935aad0dbf77559547c8fd316815bc230',landmarks=landmarks,probes=rows,
    source_pixels_reinspected=False,production_model_loaded=False,rendered_images=0),indent=2)+'\n')
print('Reproduced archived conditional point projections; sensitivity only, no geometry/source acceptance.')
