import bpy,ast,math,os,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for v in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/Xingtong_Classroom_{v}.blend'));sc=bpy.context.scene
 for o in list(sc.objects):
  if 'chair curved-back oak panel s' in o.name and o.dimensions.x>.05:bpy.data.objects.remove(o,do_unlink=True)
 o=bpy.data.objects['Verified visible title 百日誓师']
 verts=o.data.vertices;mins=[min(p.co[i] for p in verts) for i in range(3)];maxs=[max(p.co[i] for p in verts) for i in range(3)]
 for p in verts:
  for i,size in enumerate([1.65,.43,.0005]):p.co[i]=(p.co[i]-mins[i])/(maxs[i]-mins[i])*size
 o.scale=(1,1,1);o.location=(1.68,.094,1.48);bpy.context.view_layer.update()
 t=ast.parse((R/'scripts/finalize.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
 bpy.ops.wm.save_as_mainfile(filepath=str(R/f'models/Xingtong_Classroom_{v}.blend'),compress=True);json.dump(stats(meshes()),open(R/f'qa/blender_{v.lower()}_geometry.json','w'),indent=2);export(R/f'models/Xingtong_Classroom_{v}.glb')
 if False:
  sc.cycles.samples=8;sc.render.threads=4;sc.render.filepath=str(R/'qa/Detail_repair_preview.png');bpy.ops.render.render(write_still=True)
