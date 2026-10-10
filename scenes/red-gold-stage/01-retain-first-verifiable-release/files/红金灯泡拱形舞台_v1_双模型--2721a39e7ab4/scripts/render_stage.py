import bpy, json,sys,bmesh
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/red_gold_stage_v1';views=json.load(open(R+'/qa/build_facts.json'))['views']
for typ in ['textured','white']:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/red_gold_stage_'+typ+'.blend');S=bpy.context.scene;S.cycles.samples=48;S.cycles.use_denoising=False;cam=S.camera
 names=list(views) if typ=='textured' else ['源图匹配','左前','背面','底面']
 if '--preview' in sys.argv:names=['源图匹配']
 for v in names:
  loc,target,lens=views[v];cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;S.render.filepath=R+'/renders/'+v+('_材质.png' if typ=='textured' else '_白模.png');bpy.ops.render.render(write_still=True)
if '--preview' not in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=R+'/models/red_gold_stage_textured.blend');S=bpy.context.scene;S.cycles.samples=36;S.cycles.use_denoising=False
 for o in list(S.objects):
  if o.type!='MESH':continue
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
  bm=bmesh.new();bm.from_mesh(o.data);point=o.matrix_world.inverted()@Vector((0,0,0));normal=o.matrix_world.to_3x3().transposed()@Vector((1,0,0));r=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False);edges=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=edges,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 cam=S.camera;cam.location=(12,-11,7);cam.rotation_euler=(Vector((0,.5,2.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=44;S.render.filepath=R+'/renders/明确剖切_X0_诊断.png';bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/section_diagnostic_only.blend')
