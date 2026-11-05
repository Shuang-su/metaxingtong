import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path('/workspace/scratch/fa58bfcf0425/cyber-roof-main-projection-study-20261105');Q=Path(__file__).parent;f=P.parent/'cyber-roof-stage-20261105/models/roof-r05.blend';sha=hashlib.sha256(f.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene
D=json.loads((P/'results/taper-object-displacements.json').read_text());S=json.loads((P/'results/taper-only-scan.json').read_text());objs={o.name:o for o in s.objects if o.name.startswith('ROOF_MAIN')};r={'input_sha':sha,'actual_objects':list(objs),'all_nine_cases':S['h_values'],'tested_h':[.74,.55],'cases':[]}
def change(p,h):
 t=min(1,abs((p.y-5.5)/3));return Vector((p.x*(h+(1-h)*t)/(.74+.26*t),p.y,p.z))
def project(p,n):
 cam=bpy.data.objects['SOURCE'+n+(' conditional camera' if n=='11' else ' auxiliary different state')];clip=cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=1192,y=671)@cam.matrix_world.inverted()@Vector((*p,1));return Vector(((clip.x/clip.w+1)*596,(1-clip.y/clip.w)*335.5)),clip.w
for h in r['tested_h']:
 orig=next(x for x in D['rows']if x['h']==h);case={'h':h,'object_displacement_errors':{},'envelope_reprojection_error':0,'min_forward_depth':1e9,'point_pixel_errors':[],'shell_pairs':None}
 for row in orig['objects']:
  o=objs[row['object']];v=[o.matrix_world@x.co for x in o.data.vertices];w=[change(p,h)for p in v];mx=max((b-a).length for a,b in zip(v,w));case['object_displacement_errors'][o.name]=abs(mx-row['max_vertex_displacement'])
  if o.name=='ROOF_MAIN closed shell':
   N=len(v)//2;ds=[(w[i+N]-w[i]).length for i in range(N)];case['shell_pairs']={'count':N,'min':min(ds),'max':max(ds),'producer':row['shell_solidify_index_pair_distances']}
  if 'gold front eave' in o.name:case['front_full_mesh_max_displacement']=mx
 scan=next(x for x in S['rows']if x['h']==h)
 for row in scan['points']:
  if 'actual_vertex_index'in row:p=change(objs[row['model_object']].matrix_world@objs[row['model_object']].data.vertices[row['actual_vertex_index']].co,h)
  else:p=Vector(row['world_centerline'])
  px,depth=project(p,'11');case['point_pixel_errors'].append((px-Vector(row['projected'])).length);case['min_forward_depth']=min(depth,case['min_forward_depth'])
 for n,bands in scan['lower_envelopes'].items():
  for band in bands:
   for a in band['three_samples']:
    px,d=project(Vector(a['world_edge_intersection']),n);case['envelope_reprojection_error']=max(case['envelope_reprojection_error'],(px-Vector((a['x'],a['y']))).length);case['min_forward_depth']=min(d,case['min_forward_depth'])
 r['cases'].append(case)
r['source_sha_unchanged']=sha==hashlib.sha256(f.read_bytes()).hexdigest();(Q/'check.json').write_text(json.dumps(r,indent=2));print('DONE')
