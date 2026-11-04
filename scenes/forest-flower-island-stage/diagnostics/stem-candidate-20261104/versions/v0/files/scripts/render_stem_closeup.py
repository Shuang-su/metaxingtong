import bpy,pathlib,json
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1];out=R/'renders/stem-closeup';out.mkdir(exist_ok=True,parents=True)
for version in ['R09_white','R10_support-diagnostic_white']:
 bpy.ops.wm.open_mainfile(filepath=str(R/('models/'+version+'.blend')));s=bpy.context.scene
 target=Vector((-1.71156,-1.58421,4.59));loc=target+Vector((.40,-.48,.15));bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.name='DIAGNOSTIC_inferred_stem_closeup';c.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();c.data.lens=55;s.camera=c;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.cycles.samples=12;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.filepath=str(out/(version+'.png'));bpy.ops.render.render(write_still=True)
(out/'camera.json').write_text(json.dumps({'role':'synthetic geometric diagnostic, NOT source camera','target':list(target),'location':list(loc),'lens_mm':55,'size':[800,600],'samples':12,'denoise':False,'no_saved_camera_changes':True},indent=2))
