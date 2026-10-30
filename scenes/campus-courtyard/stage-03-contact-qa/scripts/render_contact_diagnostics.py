import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];D=R/'stage-03-contact-qa';out=D/'qa/contact_images';out.mkdir(exist_ok=True)
views={'BENCH01-paver-foot':((2.6,7.7,.29),(2.72,8.44,.06),55),'BENCH02-lawn-foot':((-8.8,16.9,.39),(-8.68,17.64,.16),55),'HOOP02-blue-base':((5.4,13.6,.65),(6.6,14.9,.18),45),'ENTRY-step-planter':((15.5,1.0,1.0),(18.4,4,.35),38)}
for phase,label in [('stage-02-material-candidate','before'),('stage-03-contact-qa','after')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/phase/'campus-courtyard_material.blend'));s=bpy.context.scene
 s.render.resolution_x=900;s.render.resolution_y=600;s.render.resolution_percentage=100;s.cycles.samples=48
 cam=bpy.data.objects['MAIN']
 for name,(loc,target,lens) in views.items():
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;s.camera=cam;s.render.filepath=str(out/(name+'_'+label+'.png'));bpy.ops.render.render(write_still=True)
print('CONTACT_DIAGNOSTICS_COMPLETE')
