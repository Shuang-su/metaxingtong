import bpy,ast,math,os,json,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for v in ['Textured','White']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'models/Xingtong_Classroom_{v}.blend'));sc=bpy.context.scene
 COL={c.name:c for c in bpy.data.collections};cur='02_Front_Teaching_Wall'
 t=ast.parse((R/'scripts/build_classroom.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
 white=bpy.data.materials.get('Neutral white clay')
 chalk=white if v=='White' else bpy.data.materials['Chalk white']
 metal=white if v=='White' else bpy.data.materials['Charcoal painted metal']
 cu=bpy.data.curves.new('Verified chalk title 百日誓师','FONT');cu.body='百日誓师';cu.font=bpy.data.fonts.load('/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc');cu.size=.44;cu.space_character=1.06;cu.extrude=.00025;cu.resolution_u=6
 o=bpy.data.objects.new('Verified visible title 百日誓师',cu);COL[cur].objects.link(o);o.location=(1.68,.094,1.48);o.rotation_euler=(math.pi/2,0,math.pi);bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.data.materials.append(chalk);uvbox(o)
 verts=o.data.vertices;mins=[min(p.co[i] for p in verts) for i in range(3)];maxs=[max(p.co[i] for p in verts) for i in range(3)]
 for p in verts:
  for i,size in enumerate([1.65,.43,.0005]):p.co[i]=(p.co[i]-mins[i])/(maxs[i]-mins[i])*size
 bpy.context.view_layer.update()
 cur='05_Student_Desks_Chairs'
 for back in list(COL[cur].objects):
  if not back.name.endswith('chair curved-back oak panel'):continue
  pts=[back.matrix_world@v.co for v in back.data.vertices];cx=(min(p.x for p in pts)+max(p.x for p in pts))/2;yy=max(p.y for p in pts)+.008;lo=min(p.z for p in pts);hi=max(p.z for p in pts)
  tube(back.name+' observed arched top steel rail',[(cx-.168,yy,hi-.107),(cx-.163,yy,hi-.075),(cx-.142,yy,hi-.049),(cx-.10,yy,hi-.035),(cx,yy,hi-.029),(cx+.10,yy,hi-.035),(cx+.142,yy,hi-.049),(cx+.163,yy,hi-.075),(cx+.168,yy,hi-.107)],.011,metal)
  tube(back.name+' observed lower steel back rail',[(cx-.168,yy,lo-.008),(cx-.15,yy,lo+.016),(cx-.12,yy,lo+.021),(cx+.12,yy,lo+.021),(cx+.15,yy,lo+.016),(cx+.168,yy,lo-.008)],.010,metal)
 for ob in sc.objects:
  if ob.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 sc['inferences']='Metric dimensions, 4x4 desk grid plus front-right set, unseen back wall and generic exterior inferred. Four ceiling fixtures supported by wide reference. Only verified large board title 百日誓师 restored, using approximate font; small unreadable text omitted.'
 t=ast.parse((R/'scripts/finalize.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
 bpy.context.view_layer.update();sc.camera=bpy.data.objects['PANORAMA_Level_Front'];bpy.ops.wm.save_as_mainfile(filepath=str(R/f'models/Xingtong_Classroom_{v}.blend'),compress=True)
 json.dump(stats(meshes()),open(R/f'qa/blender_{v.lower()}_geometry.json','w'),indent=2);export(R/f'models/Xingtong_Classroom_{v}.glb')
print('VERIFIED_DETAILS_ADDED')
