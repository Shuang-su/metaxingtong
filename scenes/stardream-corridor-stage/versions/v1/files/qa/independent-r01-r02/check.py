import bpy,bmesh,json,pathlib,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
P=pathlib.Path('/workspace/scratch/fa58bfcf0425/stardream-corridor-20261105');Q=pathlib.Path('/workspace/scratch/fa58bfcf0425/independent-corridor-qa-20261105');R={};snaps={}
def bvh(objects):
 vs=[];fs=[]
 for o in objects:
  off=len(vs);vs.extend([o.matrix_world@v.co for v in o.data.vertices]);o.data.calc_loop_triangles();fs.extend([tuple(off+i for i in t.vertices) for t in o.data.loop_triangles])
 return BVHTree.FromPolygons(vs,fs,all_triangles=True)
for ver in ['R01','R02']:
 for mode in ['material','white']:
  f=P/'models'/f'{ver}_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];data={};geo={}
  for o in obs:
   bm=bmesh.new();bm.from_mesh(o.data);data[o.name]={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)};bm.free();geo[o.name]=hashlib.sha256(repr(([tuple(o.matrix_world@v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
  k=f'{ver}_{mode}';snaps[k]=geo;R[k]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_count':len(obs),'camera_count':sum(o.type=='CAMERA' for o in bpy.context.scene.objects),'anomalies':{n:v for n,v in data.items() if v['nonmanifold'] or v['degenerate'] or v['signed_volume']<=0},'audit':data}
  if k!='R02_material':continue
  shell=bvh([o for o in obs if o.name.startswith(('WALL_side','WALL_end','FLOOR_finite','CEILING_finite'))]);doors=[]
  for end,w,h in [(-1,1.6,2.5),(1,1.15,2.35)]:
   wall=bvh([o for o in obs if o.name.startswith(f'WALL_end_{end}_')]);leaf=bvh([bpy.data.objects[f'DOOR_leaf_{end}']]);tests=[]
   for x in [-w*.45,0,w*.45]:
    for z in [.1,h/2,h-.1]:
     p=Vector((x,end*5.5,z));d=Vector((0,end,0));tests.append({'x':x,'z':z,'wall_hit':wall.ray_cast(p,d,1)[0] is not None,'leaf_hit':leaf.ray_cast(p,d,1)[0] is not None})
   doors.append({'end':end,'interior9':tests})
  R[k]['door_samples']=doors;seams=[]
  for z in [.001,.05,1.9,3.75,3.799]:
   for y in [-6.001,-5.999,0,5.999,6.001]:
    for side in [-1,1]:seams.append(shell.ray_cast(Vector((0,y,z)),Vector((side,0,0)),3)[0] is not None)
  R[k]['side_boundary_ray_samples']={'count':len(seams),'hits':sum(seams)}
  fit=json.load(open(P/'qa/R02-line-fit.json'));out={}
  for n,r in fit.items():
   c=bpy.data.objects[n];errs=[];depths=[]
   for key,ends in r['world_line_assumptions'].items():
    uv=[world_to_camera_view(bpy.context.scene,c,Vector(p)) for p in ends];depths.extend([p.z for p in uv]);a,b=[Vector((p.x*1192,(1-p.y)*671)) for p in uv];v=b-a;normal=Vector((-v.y,v.x)).normalized();errs.extend([normal.dot(Vector(p)-a) for p in r['observed_segments'][key]])
   expected=r['fit_signed_endpoint_errors_px'];out[n]={'matrix_max_error':max(abs(c.matrix_world[i][j]-r['matrix_world'][i][j]) for i in range(4) for j in range(4)),'abs_endpoint_errors':list(map(abs,errs)),'max_abs_difference_record':max(abs(abs(a)-abs(b)) for a,b in zip(errs,expected)),'world_line_endpoint_depths':depths,'lens':c.data.lens}
  R[k]['fit_check']=out
R['material_white_geometry_equal']={v:snaps[v+'_material']==snaps[v+'_white'] for v in ['R01','R02']}
(Q/'checks.json').write_text(json.dumps(R,indent=2));print('DONE',[(k,len(v.get('anomalies',{}))) for k,v in R.items()])
