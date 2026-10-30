"""Connect inferred mirror support to the finite headliner after arbitrary-view review."""
import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/car_passenger_cabin_white.blend'))
o=bpy.data.objects['M03_mirror_support_inferred'];attrs=dict(o.items());name=o.name;mats=list(o.data.materials)
bpy.data.objects.remove(o,do_unlink=True)
a=Vector((.01,.80,1.535));b=Vector((.01,.70,1.75));d=b-a
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.018,depth=d.length,location=(a+b)/2)
o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for k,v in attrs.items():o[k]=v
o['limitations']='Inferred attachment; connected to partial roof, source mechanism unobserved'
for m in mats:o.data.materials.append(m)
for p in o.data.polygons:p.use_smooth=True
bpy.context.scene['support_revision']='M03 inferred support reconnected to headliner after main-view review'
bpy.data.objects['P12_side_window_glass']['evidence_class']='observed-aperture_inferred-glazing'
bpy.data.objects['P12_side_window_glass']['limitations']='Window aperture observed; whether glass is raised, thickness and IOR inferred'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/car_passenger_cabin_white.blend'))
