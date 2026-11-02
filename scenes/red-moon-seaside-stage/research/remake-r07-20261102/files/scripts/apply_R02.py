import bpy,os,json,math,bmesh,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
os.sched_setaffinity(0,{sorted(os.sched_getaffinity(0))[-1]})
D=Path(__file__).resolve().parents[1];fits=json.loads((D/'models/R02-camera-fit.json').read_text())
for mode in ['material','white']:
 bpy.ops.wm.open_mainfile(filepath=str(D/f'models/R01_{mode}.blend'));s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=16
 # Shared physical layer placement: rear board inner edge now x±4.3, fixed in all cameras.
 for side,sign in[('L',-1),('R',1)]:bpy.data.objects[side+'_rear_ORANGE'].location.x=sign*5.05
 for name,p in fits.items():
  o=bpy.data.objects[name];o.location=p['location'];o.rotation_euler=Matrix((p['right'],p['up'],[-v for v in p['forward']])).transposed().to_euler();o.data.lens=p['lens_mm'];o['fit_status']=p['status'];o['fit_rms_native_px']=p['rms_native_px']
 s['R02_limit']='Static screen soft fit only; near-coplanar anchors ill-conditioned, P1 camera distance hits bound. Stage/column/frame/umbrella not accepted.'
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R02_{mode}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R02_{mode}.glb'),export_format='GLB',export_cameras=True,export_lights=False)
 if mode=='material':
  records=[]
  for o in s.objects:
   if o.type!='MESH':continue
   bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);vol=bm.calc_volume(signed=True);records.append({'name':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_world':vol,'min_z':min(v.co.z for v in bm.verts),'max_z':max(v.co.z for v in bm.verts),'interpretation':'Open leaf/paper surfaces intentional; other open boundaries or negative volume require review'});bm.free()
  (D/'models/R02-topology-audit.json').write_text(json.dumps(records,indent=2))
print('R02_SAVED')
