import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/phone-material.blend'));s=bpy.context.scene;cam=s.camera
verts=[o.matrix_world@v.co for o in s.objects if o.type=='MESH' for v in o.data.vertices];center=Vector([(min(v[i] for v in verts)+max(v[i] for v in verts))/2 for i in range(3)])
for name,v in [('front',Vector((0,0,4.5))),('rear',Vector((0,0,-4.5))),('side',Vector((4.5,0,0))),('top',Vector((0,4.5,.45)))]:
 cam.location=center+v;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.filepath=str(R/f'renders/diagnostic-{name}.png');bpy.ops.render.render(write_still=True)
