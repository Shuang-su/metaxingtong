import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector,kdtree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/C06_remade_materials.blend'));dg=bpy.context.evaluated_depsgraph_get();expected=[];et=0;names=[];mats={}
for o in bpy.context.scene.objects:
 if o.type not in {'MESH','CURVE'}:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();et+=len(me.loop_triangles);expected.extend(tuple(ev.matrix_world@v.co) for v in me.vertices);names.append(o.name);mats[o.name]=[m.name for m in me.materials if m];ev.to_mesh_clear()
expected_materials={}
for n in sorted({n for vals in mats.values() for n in vals}):
 m=bpy.data.materials[n];bs=m.node_tree.nodes.get('Principled BSDF');expected_materials[n]={'base_color':list(bs.inputs['Base Color'].default_value),'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value)}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'models/C06_remade.glb'));bpy.context.view_layer.update();actual=[];at=0;an=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();at+=len(o.data.loop_triangles);actual.extend(tuple(o.matrix_world@v.co) for v in o.data.vertices);an.append(o.name)
def nearest(A,B):
 kd=kdtree.KDTree(len(B))
 for i,p in enumerate(B):kd.insert(Vector(p),i)
 kd.balance();ds=[kd.find(Vector(p))[2] for p in A];return {'max_distance_working_units':max(ds),'mean_distance':sum(ds)/len(ds),'over_1e_4':sum(d>1e-4 for d in ds)}
material_checks=[]
for n,v in expected_materials.items():
 m=bpy.data.materials.get(n);bs=next((x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'),None) if m else None
 a0={'base_color':list(bs.inputs['Base Color'].default_value),'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value)} if bs else None
 material_checks.append({'name':n,'expected':v,'actual':a0,'plain_parameter_equal':a0 is not None and max(abs(a-b) for a,b in zip(v['base_color'],a0['base_color']))<1e-5 and abs(v['roughness']-a0['roughness'])<1e-5 and abs(v['metallic']-a0['metallic'])<1e-5})
a=nearest(expected,actual);b=nearest(actual,expected);q={'actual_reimport':True,'from_actual_blend_not_only_expected_json':True,'expected_objects':len(names),'actual_meshes':len(an),'expected_triangles':et,'actual_triangles':at,'expected_to_imported':a,'imported_to_expected':b,'geometry_transport_pass':len(names)==len(an) and et==at and a['over_1e_4']==b['over_1e_4']==0,'plain_material_parameter_checks':material_checks,'materials':{'kind':'plain approximate Principled colors/roughness; no original textures claimed','not_tested':'photometric equivalence or source texture fidelity'},'limits':'transport not source geometry, image alignment, contacts or user acceptance','source_glb_sha256':hashlib.sha256((R/'models/C06_remade.glb').read_bytes()).hexdigest()};(R/'qa/C06_actual_glb_roundtrip.json').write_text(json.dumps(q,indent=2));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C06_actual_reimport.blend'));print(json.dumps(q,indent=2))
