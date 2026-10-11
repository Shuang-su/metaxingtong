import bpy,json,sys,bmesh
from mathutils import Vector
R='/workspace/scratch/fa58bfcf0425/red_gold_stage_v1';args=sys.argv[sys.argv.index('--')+1:];typ,v=args
bpy.ops.wm.open_mainfile(filepath=R+'/models/red_gold_stage_'+typ+'.blend');S=bpy.context.scene;S.cycles.samples=24;S.cycles.use_denoising=False;S.cycles.adaptive_threshold=.04
cam=S.camera;views=json.load(open(R+'/qa/build_facts.json'))['views']
if v=='明确剖切_X0_诊断':
 bpy.ops.object.select_all(action='DESELECT')
 for o in list(S.objects):
  if o.type!='MESH':continue
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
  bm=bmesh.new();bm.from_mesh(o.data);point=o.matrix_world.inverted()@Vector((0,0,0));normal=o.matrix_world.to_3x3().transposed()@Vector((1,0,0));bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 loc,target,lens=(12,-11,7),(0,.5,2.3),44;filename=v
else:
 loc,target,lens=views[v];filename=v+('_材质' if typ=='textured' else '_白模')
if v=='底面':
 d=bpy.data.lights.new('底面诊断补光_仅检查','AREA');d.energy=2300;d.shape='DISK';d.size=10;o=bpy.data.objects.new('底面诊断补光_仅检查',d);S.collection.objects.link(o);o.location=(0,-2,-8);o.rotation_euler=(Vector((0,-1,0))-o.location).to_track_quat('-Z','Y').to_euler()
cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;S.render.filepath=R+'/renders/'+filename+'.png';bpy.ops.render.render(write_still=True)
if v=='明确剖切_X0_诊断':bpy.ops.wm.save_as_mainfile(filepath=R+'/qa/section_diagnostic_only.blend')
