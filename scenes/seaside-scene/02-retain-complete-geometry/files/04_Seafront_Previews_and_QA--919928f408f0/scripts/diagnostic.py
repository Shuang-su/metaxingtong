import bpy,bmesh,json,math
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/seaside_scene_fullscene';bpy.ops.wm.open_mainfile(filepath=R+'/models/Seafront_Textured.blend');S=bpy.context.scene
# This diagnostic copy isolates a finite section -4 <= y <= 4; no production changes.
for o in list(S.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);inv=o.matrix_world.inverted()
 for y,n in [(-4,(0,-1,0)),(4,(0,1,0))]:
  res=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-5,plane_co=inv@Vector((0,y,0)),plane_no=o.matrix_world.to_3x3().transposed()@Vector(n),clear_outer=True,clear_inner=False)
  ed=[e for e in res['geom_cut'] if isinstance(e,bmesh.types.BMEdge)]
  if ed and not ('leaflet' in o.name or 'groundcover' in o.name or 'ocean' in o.name.lower()):
   try:bmesh.ops.holes_fill(bm,edges=ed,sides=0)
   except:pass
 if not bm.faces:bm.free();bpy.data.objects.remove(o,do_unlink=True);continue
 bm.to_mesh(o.data);bm.free()
cam=bpy.data.objects['QA03_近端断面'];cam.location=(-17,-31,12);cam.rotation_euler=(Vector((6,0,-1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=35;S.camera=cam;S.cycles.samples=16;S.cycles.use_denoising=False;S.render.resolution_x=1188;S.render.resolution_y=668;S.render.filepath=R+'/renders/QA11_诊断横断面.png';bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/section_diagnostic_only.blend',compress=True);bpy.ops.render.render(write_still=True)
