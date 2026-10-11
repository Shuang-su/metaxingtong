import bpy,bmesh,os
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_bar_fullroom';bpy.ops.wm.open_mainfile(filepath=R+'/models/seaside_bar_complete_textured.blend');S=bpy.context.scene
# Diagnostic section of a copy, removes right half at x=0 to expose aisle and construction.
for o in list(bpy.data.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted();co=inv@Vector((0,0,0));normal=o.matrix_world.to_3x3().transposed()@Vector((1,0,0))
 geom=list(bm.verts)+list(bm.edges)+list(bm.faces)
 if geom:
  res=bmesh.ops.bisect_plane(bm,geom=geom,dist=1e-6,plane_co=co,plane_no=normal,clear_outer=True,clear_inner=False)
  edges=[e for e in res['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
  if edges:
   try:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
   except:pass
 bm.to_mesh(o.data);bm.free()
S.camera=bpy.data.objects['01_前方全貌'];S.camera.location=(8,-9,5);S.camera.rotation_euler=(Vector((-1,-.5,1.5))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.render.resolution_x=1000;S.render.resolution_y=750;S.cycles.samples=32;S.render.filepath=R+'/renders/11_诊断剖切_x0_非主模型.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/section_diagnostic_only.blend')
