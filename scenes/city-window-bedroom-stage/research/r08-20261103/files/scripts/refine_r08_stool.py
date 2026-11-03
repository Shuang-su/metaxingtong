import bpy,bmesh,math,json
from pathlib import Path
D=Path(__file__).resolve().parents[1];p=json.load(open(D/'qa/R08-hourglass-profile.json'));profile=p['dense_profile'];N=96
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R07_{mode}.blend'));o=bpy.data.objects['CENTRE_hourglass_stool'];old=o.data;mat=old.materials[0]
 v=[(.7*r*math.cos(i*2*math.pi/N),1.25+.7*r*math.sin(i*2*math.pi/N),.7*z-.007) for z,r in profile for i in range(N)];f=[]
 for k in range(len(profile)-1):
  for i in range(N):j=(i+1)%N;f.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
 f += [tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 me=bpy.data.meshes.new('hourglass_continuous_profile');me.from_pydata(v,[],f);me.update();o.data=me;me.materials.append(mat)
 for poly in me.polygons:poly.use_smooth=(len(poly.vertices)==4)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o['observation_status']='Source supports continuously curved hourglass silhouette; PCHIP interpolation of existing hypothesized radii, dimensions remain unmeasured. No camera/light changes.'
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R08_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R08_{mode}.glb'),export_format='GLB',export_apply=True)
