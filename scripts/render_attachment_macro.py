import bpy,pathlib,json,hashlib,math,sys,argparse
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--light-energy',type=float,default=8);parser.add_argument('--variant',default='');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=R/'renders'/args.variant;out.mkdir(exist_ok=True,parents=True)
# The same diagnostic camera and lighting are reused without hiding any geometry.
cam_specs=None;rows=[]
for label,model in [('before',R/'inputs/leaf-only-r06-nonexact-diagnostic-replay.blend'),('after',R/'models/leaf-only-contact-candidate-v2.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2
 s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
 shell=s.objects['LEAF_001_ThinConcaveShell'];m=shell.data;m.calc_loop_triangles();v=[shell.matrix_world@p.co for p in m.vertices];tree=BVHTree.FromPolygons(v,[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True)
 vein=s.objects['LEAF_003_Branch_03_L'];tip=sum((vein.matrix_world@v.co for v in list(vein.data.vertices)[-18:-12]),Vector())/6
 if cam_specs is None:
  hit,n,_,_=tree.ray_cast(Vector((tip.x,tip.y,8)),Vector((0,0,-1)),20)
  target=tip-n*.004;direction=Vector((0,1,0));tangent=(direction-n*direction.dot(n)).normalized();position=target+tangent*.22+n*.045
  cam_specs=dict(target=list(target),location=list(position),rotation=list((target-position).to_track_quat('-Z','Y').to_euler()),ortho_scale=.23,lens=50,clip_start=.001,clip_end=50)
 for o in s.objects:
  material=bpy.data.materials.new('DIAGNOSTIC_'+o.name);material.use_nodes=True;p=material.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.48,.52,.50,1) if o==shell else (.55,.12,.015,1);p.inputs['Roughness'].default_value=.65;o.data.materials.clear();o.data.materials.append(material)
 d=bpy.data.cameras.new('ATTACHMENT_MACRO');c=bpy.data.objects.new('ATTACHMENT_MACRO',d);s.collection.objects.link(c);d.type='ORTHO';d.ortho_scale=cam_specs['ortho_scale'];d.lens=cam_specs['lens'];d.clip_start=cam_specs['clip_start'];d.clip_end=cam_specs['clip_end'];c.location=cam_specs['location'];c.rotation_euler=cam_specs['rotation'];s.camera=c
 world=bpy.data.worlds.new('Diagnostic');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.17,.19,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=world
 light=bpy.data.lights.new('MACRO_AREA','AREA');o=bpy.data.objects.new('MACRO_AREA',light);s.collection.objects.link(o);o.location=Vector(cam_specs['target'])+Vector((-.1,-.15,.35));o.rotation_euler=(Vector(cam_specs['target'])-o.location).to_track_quat('-Z','Y').to_euler();light.energy=args.light_energy;light.shape='DISK';light.size=.18
 s.render.filepath=str(out/('vein-tip-contact-'+label+'.png'));bpy.ops.render.render(write_still=True)
 rows.append(dict(label=label,model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),image=s.render.filepath,image_sha256=hashlib.sha256(pathlib.Path(s.render.filepath).read_bytes()).hexdigest(),all_20_meshes_visible=True))
(R/('qa/macro-render-manifest'+('-'+args.variant if args.variant else '')+'.json')).write_text(json.dumps(dict(camera=cam_specs,area_light_energy=args.light_energy,resolution=[1000,700],samples=16,threads=2,denoising=False,mode='Same diagnostic camera and neutral proxy materials. Not source photographs, no original scene recovery. Models not re-saved after diagnostics.',rows=rows),indent=2)+'\n')
