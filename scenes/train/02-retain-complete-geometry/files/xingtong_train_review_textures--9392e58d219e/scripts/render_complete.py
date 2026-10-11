import bpy,bmesh,sys,math,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'deliverables';mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'qa'
if mode=='white':bpy.ops.wm.open_mainfile(filepath=str(O/'02_train_white.blend'))
else:bpy.ops.wm.open_mainfile(filepath=str(O/'01_train_material.blend'))
S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;S.cycles.use_denoising=False;S.render.image_settings.file_format='PNG';S.cycles.samples=16
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
if mode=='qa':names=[f'INSPECT_{i:02d}_' for i in range(1,9)];names=[o.name for o in S.objects if any(o.name.startswith(n) for n in names)]
elif mode=='source':names=['MATCH_A_15m19_right_booth','MATCH_B_45m12_left_booth','MATCH_D_13m59_wide'];S.render.resolution_x=1188;S.render.resolution_y=668;S.cycles.samples=24
elif mode=='white':
 d=bpy.data.cameras.new('INSPECT_12_support_detail');d.lens=18;d.sensor_width=36;d.clip_start=.02;o=bpy.data.objects.new('INSPECT_12_support_detail',d);S.collection.objects.link(o);o.location=(0,-.90,.27);o.rotation_euler=(Vector((1.50,-.90,.32))-o.location).to_track_quat('-Z','Y').to_euler()
 names=['INSPECT_01_forward_aisle','INSPECT_03_right_booth','INSPECT_05_ceiling','INSPECT_07_forward_door','INSPECT_08_reverse_door','INSPECT_12_support_detail'];S.cycles.samples=16
elif mode in ['exterior','cutaway']:
 S.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.13,.17,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.5;S.view_settings.exposure=.15
 for i,(loc,energy,size) in enumerate([((4,-6,7),950,5),((-4,-2,5),600,5),((0,7,6),1000,6)]):
  d=bpy.data.lights.new('Diagnostic exterior lamp','AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new('Diagnostic exterior lamp',d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.3))-o.location).to_track_quat('-Z','Y').to_euler()
 names=['INSPECT_09_exterior_front','INSPECT_10_exterior_reverse']
 if mode=='cutaway':
  # Independent diagnostic half-section, never applied to the saved full scene or source renders.
  for o in list(S.objects):
   if o.type!='MESH':continue
   wp=[o.matrix_world@v.co for v in o.data.vertices]
   if min(p.x for p in wp)>.08:bpy.data.objects.remove(o,do_unlink=True);continue
   if max(p.x for p in wp)<=.08:continue
   bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
   im=o.matrix_world.inverted();bm=bmesh.new();bm.from_mesh(o.data);res=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=im@Vector((.08,0,0)),plane_no=o.matrix_world.to_3x3().transposed()@Vector((1,0,0)),clear_outer=True,clear_inner=False)
   edges=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=edges,sides=0);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
  names=['INSPECT_11_cutaway'];S['Diagnostic_only']='True x=0.08 mesh half-section; full delivery and source views unchanged.'
else:raise ValueError(mode)
for name in names:
 S.camera=bpy.data.objects[name]
 if mode in ['exterior','cutaway']:S.camera.data.lens=25
 if mode=='exterior':
  from bpy_extras.object_utils import world_to_camera_view
  corners=[Vector((x,y,z)) for x in [-1.635,1.635] for y in [-5.675,5.675] for z in [-.15,2.71]]
  for _ in range(20):
   points=[world_to_camera_view(S,S.camera,p) for p in corners]
   if min(p.x for p in points)>.035 and max(p.x for p in points)<.965 and min(p.y for p in points)>.035 and max(p.y for p in points)<.965:break
   S.camera.data.lens*=.94
 out=R/'renders'/(('white_' if mode=='white' else '')+name+'.png');S.render.filepath=str(out);bpy.ops.render.render(write_still=True);print('RENDER_READY',out,flush=True)
