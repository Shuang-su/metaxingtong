import bpy,bmesh,os,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
os.sched_setaffinity(0,{sorted(os.sched_getaffinity(0))[0]})
V=os.environ.get('AUDIT_VERSION','R05')
D=Path('/workspace/scratch/fa58bfcf0425/metaxingtong-red-moon-remake-20261102'); O=Path('/workspace/scratch/fa58bfcf0425/review-red-moon-remake-20261102');out={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
 result={};trees={};dep=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  ev=o.evaluated_get(dep);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);bm.transform(o.matrix_world);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();bm.normal_update()
  vs=[tuple(v.co) for v in bm.verts]; fs=[tuple(v.index for v in f.verts) for f in bm.faces];boundary=sum(e.is_boundary for e in bm.edges)
  result[o.name]={'vertices':vs,'faces':fs,'triangles':[tuple(l.vert.index for l in tri) for tri in bm.calc_loop_triangles()],'boundary':boundary,'nonmanifold':sum(not e.is_manifold for e in bm.edges),'noncontiguous_manifold':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'signed_volume':bm.calc_volume(signed=True) if boundary==0 else None,'bounds':[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]}
  trees[o.name]=BVHTree.FromBMesh(bm);bm.free();ev.to_mesh_clear()
 return result,trees
def compact(s):return {k:{q:v for q,v in r.items() if q not in ['vertices','faces','triangles']} for k,r in s.items()}
def nearest(a,b):
 t=KDTree(len(b))
 for i,v in enumerate(b):t.insert(v,i)
 t.balance();ds=[t.find(v)[2] for v in a];return {'max':max(ds),'over1e-4':sum(d>1e-4 for d in ds)}
def surface_distance(src,dst):
 tree=BVHTree.FromPolygons([Vector(v) for v in dst['vertices']],dst['triangles'],all_triangles=True);ds=[]
 for tri in src['triangles']:
  p=sum((Vector(src['vertices'][i]) for i in tri),Vector())/3;hit=tree.find_nearest(p);ds.append(hit[3])
 return {'triangle_centroid_samples':len(ds),'max_distance':max(ds) if ds else None,'over1e-4':sum(x>1e-4 for x in ds)}
def compare(a,b):
 r={'missing':sorted(set(a)-set(b)),'extra':sorted(set(b)-set(a)),'objects':{}}
 for k in a.keys()&b.keys():r['objects'][k]={'forward':nearest(a[k]['vertices'],b[k]['vertices']),'reverse':nearest(b[k]['vertices'],a[k]['vertices']),'surface_forward':surface_distance(a[k],b[k]),'surface_reverse':surface_distance(b[k],a[k])}
 return r
baseline={}
for mode in ['material','white']:
 blend=D/f'models/{V}_{mode}.blend'; glb=D/f'models/{V}_{mode}.glb';before={p.name:sha(p) for p in [blend,glb]};bpy.ops.wm.open_mainfile(filepath=str(blend));s,t=snapshot();baseline[mode]=s
 out[mode]={'blend_topology':compact(s),'cameras':{o.name:{'matrix':list(map(list,o.matrix_world)),'lens':o.data.lens} for o in bpy.context.scene.objects if o.type=='CAMERA'}}
 if mode=='material':
  stage=t['STAGE_shared_rounded_lobes'];ground=t['GROUND_finite_work_extent'];st=s['STAGE_shared_rounded_lobes'];records=[]
  for ix in range(49):
   for iy in range(65):
    x=st['bounds'][0][0]+(st['bounds'][0][1]-st['bounds'][0][0])*ix/48;y=st['bounds'][1][0]+(st['bounds'][1][1]-st['bounds'][1][0])*iy/64
    hit=stage.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2)[0]
    if hit is None:continue
    g=ground.ray_cast(Vector((x,y,.001)),Vector((0,0,-1)),1)[0];records.append({'xy':[x,y],'stage_top':hit.z,'ground_top':None if g is None else g.z})
  out['stage_ground_samples']={'total_stage_hits':len(records),'missing_ground':sum(r['ground_top'] is None for r in records),'missing_examples':[r for r in records if r['ground_top'] is None][:20],'limits':'Uniform footprint vertical samples, not mechanical load test; tests actual finite work geometry'}
  names=['GROUND_finite_work_extent','STAGE_shared_rounded_lobes','STAGE_shared_border','BAND_finite_arc','GLASS_finite_arc','L_COLUMN_core','L_COLUMN_foot','L_COLUMN_cap','R_COLUMN_core','R_COLUMN_foot','R_COLUMN_cap','L_front_NOTCHED','R_front_NOTCHED','L_rear_ORANGE','R_rear_ORANGE']
  out['support_bounds']={n:s[n]['bounds'] for n in names if n in s}
 # Major support endpoint samples: actual evaluated surface rays, not AABB intersection claims.
 if mode=='material':
  pairs=[('GROUND_finite_work_extent',side+'_COLUMN_foot') for side in ['L','R']]+[(side+'_COLUMN_foot',side+'_COLUMN_core') for side in ['L','R']]+[(side+'_COLUMN_core',side+'_COLUMN_cap') for side in ['L','R']]+[(side+'_COLUMN_cap','BAND_finite_arc') for side in ['L','R']]+[('BAND_finite_arc','GLASS_finite_arc')]+[('GROUND_finite_work_extent',n) for n in ['L_front_NOTCHED','R_front_NOTCHED','L_rear_ORANGE','R_rear_ORANGE']]
  results=[]
  for lower,upper in pairs:
   # Cap/band uses cap footprint; otherwise sample upper footprint.
   sample=lower if upper=='BAND_finite_arc' else upper;bb=s[sample]['bounds'];N=81 if upper=='GLASS_finite_arc' else 17;vals=[];miss=0;one=0
   for ix in range(N):
    for iy in range(N):
     x=bb[0][0]+(bb[0][1]-bb[0][0])*(ix+.5)/N;y=bb[1][0]+(bb[1][1]-bb[1][0])*(iy+.5)/N
     a=t[lower].ray_cast(Vector((x,y,20)),Vector((0,0,-1)),40)[0];b=t[upper].ray_cast(Vector((x,y,-20)),Vector((0,0,1)),40)[0]
     if a is not None and b is not None:vals.append(b.z-a.z)
     elif (a is not None if sample==lower else b is not None):miss+=1
   results.append({'lower':lower,'upper':upper,'grid':N,'both_surface_hits':len(vals),'sample_footprint_missing_counterpart':miss,'gap_min':min(vals)if vals else None,'gap_max':max(vals)if vals else None,'interpretation':'Negative is overlap, zero contact, positive separation; sample only, not load capacity/source proof'})
  out['support_endpoint_samples']=results
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));g,_=snapshot();out[mode]['actual_glb_import_topology']=compact(g);out[mode]['actual_glb_world_vertex_compare']=compare(s,g);# Diagnostic seam weld on imported in-memory meshes ONLY, never save originals.
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bm.to_mesh(obj.data);bm.free()
 welded,_=snapshot();out[mode]['glb_in_memory_weld1e-5_topology']=compact(welded)
 out[mode]['read_only_hash_unchanged']=all(sha(p)==before[p.name] for p in [blend,glb])
 (O/f'{V}-independent-audit.json').write_text(json.dumps(out,indent=2))
out['material_white_exact_geometry']=all(baseline['material'][k]['vertices']==baseline['white'][k]['vertices'] and baseline['material'][k]['faces']==baseline['white'][k]['faces'] for k in baseline['material']) and set(baseline['material'])==set(baseline['white'])
(O/f'{V}-independent-audit.json').write_text(json.dumps(out,indent=2));print('AUDIT_DONE',out['material_white_exact_geometry'],out['stage_ground_samples'])
