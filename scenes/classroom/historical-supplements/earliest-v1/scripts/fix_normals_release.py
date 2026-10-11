import bpy,os,json,hashlib,math,ast,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Classroom_Textured.blend'));sc=bpy.context.scene
result={'mesh_count':0,'closed_before_negative_volume':0,'closed_after_negative_volume':0,'method':'BMesh outward-normal recalculation; coordinates and UV preserved. All objects retain the same metric shapes.'}
for o in sc.objects:
 if o.type!='MESH':continue
 result['mesh_count']+=1;bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);v=bm.calc_volume(signed=True)
 if closed and v < -1e-10:result['closed_before_negative_volume']+=1
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if closed and bm.calc_volume(signed=True)<-1e-10:
  bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 if closed and bm.calc_volume(signed=True)<-1e-10:result['closed_after_negative_volume']+=1
 bm.to_mesh(o.data);o.data.update();bm.free()
json.dump(result,open(R/'qa/normal_orientation_check.json','w'),indent=2)
t=ast.parse((R/'scripts/finalize.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
sc.cycles.samples=32;sc.render.threads=6;sc.camera=bpy.data.objects['PANORAMA_Level_Front'];sc.view_settings.exposure=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Classroom_Textured.blend'),compress=True);json.dump(stats(meshes()),open(R/'qa/blender_textured_geometry.json','w'),indent=2);export(R/'models/Xingtong_Classroom_Textured.glb')
# Produce the white model immediately, ensuring the geometry export pair exists before renders.
savedmats={o.name:list(o.data.materials) for o in meshes()};w=bpy.data.materials.new('Neutral white clay');w.use_nodes=True;p=w.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.59,.59,.59,1);p.inputs['Roughness'].default_value=.78
for o in meshes():
 o.data.materials.clear();o.data.materials.append(w)
 for poly in o.data.polygons:poly.material_index=0
for o in sc.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1)
sc.view_settings.exposure=-.8;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.35,.35,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
# The white file needs no unused image datablocks. Native textured file is already packed safely.
for ma in list(bpy.data.materials):
 if ma.users==0:bpy.data.materials.remove(ma)
for im in list(bpy.data.images):
 if im.users==0:bpy.data.images.remove(im)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Classroom_White.blend'),compress=True);json.dump(stats(meshes()),open(R/'qa/blender_white_geometry.json','w'),indent=2);export(R/'models/Xingtong_Classroom_White.glb')
for n,ca in [('Level_Front','PANORAMA_Level_Front'),('Level_Windows','PANORAMA_Level_Windows')]:render('Final_White_'+n,ca)
# Reopen the packed textured file so white-only materials and light adjustments cannot leak back.
bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Classroom_Textured.blend'));sc=bpy.context.scene;sc.cycles.samples=32;sc.render.threads=6
for n,ca in [('Level_Front','PANORAMA_Level_Front'),('Level_Windows','PANORAMA_Level_Windows'),('Match_A','MATCH_A_Front_00h15m19s'),('Match_B','MATCH_B_Windows_00h35m23s'),('Match_C_Wide','MATCH_C_Wide_01h11m24s')]:render('Final_Textured_'+n,ca)
render('Final_Textured_Desk_Detail','DETAIL_Desks_Podium')
print('FINAL_RELEASE_READY',flush=True)
