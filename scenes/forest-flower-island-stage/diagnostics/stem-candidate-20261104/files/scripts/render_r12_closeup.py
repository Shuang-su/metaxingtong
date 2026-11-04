import bpy,pathlib,json
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/('models/R12_support-diagnostic_'+mode+'.blend')));s=bpy.context.scene
 j=json.load(open(R/'renders/stem-closeup/camera.json'));target=Vector(j['target']);loc=Vector(j['location']);bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.name='DIAGNOSTIC_inferred_stem_closeup';c.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();c.data.lens=j['lens_mm'];s.camera=c;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.filepath=str(R/('renders/stem-closeup/R12_'+mode+'.png'));bpy.ops.render.render(write_still=True)
