import bpy,math,json
from pathlib import Path
D=Path(__file__).resolve().parents[1]
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R02_{mode}.blend'))
 o=bpy.data.objects['LAMP_shade'];N=64;profiles=[(2.50,.43),(3.15,.25),(3.15,.23),(2.50,.41)]
 v=[(-5.45+r*math.cos(i*2*math.pi/N),2.8+r*math.sin(i*2*math.pi/N),z) for z,r in profiles for i in range(N)]
 f=[]
 for k in range(4):
  for i in range(N):j=(i+1)%N;f.append((k*N+i,k*N+j,((k+1)%4)*N+j,((k+1)%4)*N+i))
 me=bpy.data.meshes.new('LAMP_shade_closed_annular_mesh');me.from_pydata(v,[],f);me.update();m=o.data.materials[0];o.data=me;o.data.materials.append(m)
 import bmesh
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R02b_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R02b_{mode}.glb'),export_format='GLB',export_apply=True)
