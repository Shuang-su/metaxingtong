import bpy,bmesh
from mathutils import Vector,Matrix
R='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery'
bpy.ops.wm.open_mainfile(filepath=R+'/models/KTV_Complete_Open_Stage.blend');sc=bpy.context.scene
# Isolated, unsaved diagnostic copy. Original geometry file is never overwritten.
for o in list(sc.objects):
 if o.type!='MESH':continue
 o.data=o.data.copy();o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4)
 bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,0,0)),plane_no=Vector((1,0,0)),clear_outer=True,clear_inner=False)
 bm.to_mesh(o.data);bm.free();o.data.update()
d=bpy.data.cameras.new('Diagnostic_section_camera');c=bpy.data.objects.new('Diagnostic_section_camera',d);sc.collection.objects.link(c);c.location=(10,-12,3);c.rotation_euler=(Vector((-1,-.5,.2))-c.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=15;sc.camera=c
sc.render.filepath=R+'/renders/13_DIAGNOSTIC_SECTION_ONLY.png';sc.cycles.samples=24;bpy.ops.render.render(write_still=True)
