import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent;records=[]
for name in ['roof-r06b-experiment.blend','roof-r06b-white.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/name));s=bpy.context.scene;s.cycles.samples=64;s.cycles.use_denoising=False;s.render.resolution_percentage=100;s.render.resolution_x=796;s.render.resolution_y=448
 bpy.ops.object.camera_add(location=(4.1,-1,4.7));c=bpy.context.object;c.rotation_euler=(Vector((4.1,4.3,4.7))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=3.2;s.camera=c
 out=name.removesuffix('.blend')+'-front-close64.png';s.render.filepath=str(P/'research-r06'/out);bpy.ops.render.render(write_still=True)
 records.append({'file':out,'input_blend':name,'camera_location':list(c.location),'camera_rotation':list(c.rotation_euler),'camera_type':'ORTHO','ortho_scale':3.2,'dimensions':[796,448],'percentage':100,'samples':64,'denoise':False,'lighting':'unchanged original R05/R06b production lights/world','only_change_from_close8':'samples8 to64'})
(P/'research-r06/close64-recipe.json').write_text(json.dumps(records,indent=2))
