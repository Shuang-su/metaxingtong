import bpy,bmesh
bpy.ops.wm.open_mainfile(filepath='/workspace/shared/desert-camp-build-20261031/scenes/desert-tent-camp/models/R06_camp_materials.blend')
for n in ['L01_handle','T01_right_guy_rope']:
 o=bpy.data.objects[n];bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');bm=bmesh.new();bm.from_mesh(o.data);print(n,'before',sum(e.is_boundary for e in bm.edges),len(bm.verts));bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);print('afterweld',sum(e.is_boundary for e in bm.edges),len(bm.verts),sum(not e.is_manifold for e in bm.edges));bm.free()
