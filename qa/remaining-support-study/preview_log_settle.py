import bpy,pathlib,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=pathlib.Path(__file__).resolve().parent;p=D.parent/'forest-diagnostic-replay-20261104/models/R14_anchor-diagnostic_white.blend';gap=json.load(open(D/'projected-surface-gap.json'))['objects'][1]['minimum_vertical_gap'];rows=[]
def bt(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[x.vertices[:] for x in o.data.polygons])
for tag,lower in [('before',0),('trial',gap+.003)]:
 bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects['LOG_left_fallen'];o.location.z-=lower;bpy.context.view_layer.update();t=bt(o);rels=[]
 vs=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector(tuple(min(v[k] for v in vs) for k in range(3)));hi=Vector(tuple(max(v[k] for v in vs) for k in range(3)))
 for other in bpy.context.scene.objects:
  if other.type!='MESH' or other==o:continue
  bb=[other.matrix_world@Vector(x) for x in other.bound_box]
  if any(max(v[k] for v in bb)<lo[k] or min(v[k] for v in bb)>hi[k] for k in range(3)):continue
  n=len(t.overlap(bt(other)))
  if n:rels.append({'object':other.name,'bvh_face_pairs':n})
 loc=Vector((-6.1,3.6,.15));target=Vector((-6.18,5.27,-.015));bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();c.data.lens=45;s=bpy.context.scene;s.camera=c
 lp=Vector((-6,4,.8));bpy.ops.object.light_add(type='AREA',location=lp);l=bpy.context.object;l.rotation_euler=(target-lp).to_track_quat('-Z','Y').to_euler();l.data.energy=45;l.data.size=1
 s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;png=D/(tag+'-log-white.png');s.render.filepath=str(png);bpy.ops.render.render(write_still=True)
 rows.append({'tag':tag,'world_z_translation':-lower,'intersections':rels,'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'camera':{'loc':list(loc),'target':list(target),'lens':45},'diagnostic_light':{'loc':list(lp),'watts':45,'size':1},'samples':8,'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'log-trial.json').write_text(json.dumps({'models_saved':False,'role':'in-memory inferred rigid lowering trial, not source view or accepted geometry','variants':rows},indent=2))
