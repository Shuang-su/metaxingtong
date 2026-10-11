import bpy,os,json,hashlib,math,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Classroom_Textured.blend'));sc=bpy.context.scene
# Final construction QA: the extra corner desk is off the platform, so its fascia must be too.
for o in sc.objects:
 if (o.name.startswith('Desk perforated ochre front rail') or o.name.startswith('Desk front empty label mount')) and o.location.y<1.5:o.location.z-=.20
# Props retain true circular sections; only teacher-table geometry was narrowed.
for o in sc.objects:
 if o.name.startswith('Teacher cup') or o.name.startswith('Teacher stacked books') or 'desk ornament' in o.name.lower():o.dimensions.x*=1.88/1.25
# Television is wide and sits immediately below the ceiling beam in the complete wide reference.
for o in sc.objects:
 if o.name=='Teaching wall monitor':o.dimensions=(1.55,.095,.72);o.location.z=2.90
 elif o.name=='Monitor dark screen':o.dimensions=(1.48,.010,.65);o.location.z=2.90
 elif o.name.startswith('Monitor wall bracket'):o.location.z+=.13
 elif o.name.startswith('Clock'):o.location.z+=.08
# Source door leaf is dark brown, distinct from the oak desks.
m=bpy.data.materials.new('Observed deep brown door leaf');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.052,.030,.022,1);b.inputs['Roughness'].default_value=.51
o=bpy.data.objects['Observed dark door leaf'];o.data.materials.clear();o.data.materials.append(m)
bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in sc.objects if o.type=='MESH');bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.context.view_layer.update()
# Export/stat/render helpers from the finalization script, without rerunning construction.
t=ast.parse((R/'scripts/finalize.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'release_helpers','exec'))
sc.cycles.samples=40;sc.render.threads=6;sc.view_settings.exposure=0;sc.camera=bpy.data.objects['PANORAMA_Level_Front']
for im in bpy.data.images:
 if im.source=='FILE':im.filepath='//../textures/'+os.path.basename(im.filepath);im.pack()
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
bpy.ops.wm.open_mainfile(filepath=str(R/'models/Xingtong_Classroom_Textured.blend'));sc=bpy.context.scene;sc.cycles.samples=40;sc.render.threads=6
for n,ca in [('Level_Front','PANORAMA_Level_Front'),('Level_Windows','PANORAMA_Level_Windows'),('Match_A','MATCH_A_Front_00h15m19s'),('Match_B','MATCH_B_Windows_00h35m23s'),('Match_C_Wide','MATCH_C_Wide_01h11m24s')]:render('Final_Textured_'+n,ca)
render('Final_Textured_Desk_Detail','DETAIL_Desks_Podium')
print('FINAL_RELEASE_READY',flush=True)
