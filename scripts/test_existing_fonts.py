import bpy,bmesh,json,os
r=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));out=[]
for path in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc','/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc']:
 if not os.path.exists(path):continue
 bpy.ops.wm.read_factory_settings(use_empty=True);font=bpy.data.fonts.load(path);cu=bpy.data.curves.new('test','FONT');cu.body='QQ炫舞';cu.font=font;cu.extrude=.025;cu.bevel_depth=0;cu.resolution_u=8;o=bpy.data.objects.new('test',cu);bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');b=bmesh.new();b.from_mesh(o.data);bmesh.ops.remove_doubles(b,verts=list(b.verts),dist=1e-5);steps=[]
 for i in range(9):
  if i:bmesh.ops.dissolve_limit(b,angle_limit=1e-5,use_dissolve_boundaries=False,verts=list(b.verts),edges=list(b.edges),delimit={'NORMAL'});bmesh.ops.dissolve_degenerate(b,dist=1e-7,edges=list(b.edges));bmesh.ops.recalc_face_normals(b,faces=list(b.faces))
  tri=b.calc_loop_triangles();zero=sum(((t[1].vert.co-t[0].vert.co).cross(t[2].vert.co-t[0].vert.co)).length<2e-12 for t in tri);steps.append({'step':i,'v':len(b.verts),'f':len(b.faces),'zero_triangles':zero,'nm':sum(not e.is_manifold for e in b.edges)})
 out.append({'font_path':path,'loaded_name':font.name,'steps':steps});b.free()
json.dump(out,open(r+'/qa/existing-font-alternatives.json','w'),indent=2);print(out)
