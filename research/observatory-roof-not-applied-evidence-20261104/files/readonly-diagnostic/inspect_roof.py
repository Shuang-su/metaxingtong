import bpy,json,pathlib,hashlib
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/observatory-candidate-20261104'); Q=P.parent/'observatory-roof-readonly-diagnostic-20261104'
f=P/'models/R09_material.blend'; bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene
out={'model':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_count':sum(o.type=='MESH' for o in s.objects),'cameras':{},'roof':{}}
for o in s.objects:
 if o.type=='CAMERA':out['cameras'][o.name]={'lens':o.data.lens,'matrix':[list(x)for x in o.matrix_world]}
 if o.type=='MESH' and o.name.startswith('ROOF_'):
  vs=[o.matrix_world@v.co for v in o.data.vertices];d={'vertices':len(vs),'bounds':[[min(v[i] for v in vs),max(v[i]for v in vs)]for i in range(3)],'projections':{}}
  if o.name=='ROOF_hollow_dome':d['radius_z_pairs']=sorted(set((round((v.x*v.x+v.y*v.y)**.5,4),round(v.z,4))for v in vs))
  for c in ['SOURCE_13_high','SOURCE_14_front','SOURCE_15_exterior','SOURCE_21_high']:
   ps=[world_to_camera_view(s,bpy.data.objects[c],v)for v in vs]; d['projections'][c]={'x':[min(p.x*1192 for p in ps),max(p.x*1192 for p in ps)],'y':[min((1-p.y)*671 for p in ps),max((1-p.y)*671 for p in ps)],'depth':[min(p.z for p in ps),max(p.z for p in ps)],'warning':'Raw un-clipped projected vertices, NOT visible silhouette or screen coverage; mixed/near-zero depth invalidates bounds for interior cameras'}
  out['roof'][o.name]=d
(Q/'actual-roof.json').write_text(json.dumps(out,indent=2)); print('mesh',out['mesh_count'],'cams',len(out['cameras']),'roof',len(out['roof']));print(json.dumps({k:v for k,v in out['roof'].items() if 'rib' not in k},indent=2))
