import bpy,bmesh
bpy.ops.wm.open_mainfile(filepath='/workspace/shared/desert-camp-build-20261031/scenes/desert-tent-camp/models/R07_training_bug_corrected.blend')
for n in ['L01_handle','T01_right_guy_rope']:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);es=[e for e in bm.edges if e.is_boundary];vs={v for e in es for v in e.verts};print(n,len(es),len(vs));print('bounds',[(min(v.co[i] for v in vs),max(v.co[i] for v in vs)) for i in range(3)]);print('edge faces',[len(e.link_faces) for e in es]);res=bmesh.ops.holes_fill(bm,edges=es,sides=0);print('repeat',len(res['faces']),sum(e.is_boundary for e in bm.edges));bm.free()
