import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/keyring-material.blend'));s=bpy.context.scene
PARAMS=[{'name':'inferred-low-bridge-central-step','ri':4.99,'ro':5.03,'z':-.35,'h':.1,'a':-math.pi,'b':math.pi,'N':96,'targets':['stage-central-solid','stage-step-ring']},{'name':'inferred-low-bridge-step-outer','ri':5.99,'ro':6.03,'z':-.45,'h':.1,'a':-.66*math.pi,'b':.66*math.pi,'N':96,'targets':['stage-step-ring','stage-outer-floor']}]
def meshstate(o):return {'matrix':[list(x) for x in o.matrix_world],'verts':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'uv':[[list(d.uv) for d in l.data] for l in o.data.uv_layers],'materials':[m.name for m in o.data.materials],'hide':[o.hide_render,o.hide_viewport]}
def camera(o):return {'matrix':[list(x) for x in o.matrix_world],'lens':o.data.lens,'sensor':[o.data.sensor_width,o.data.sensor_height],'fit':o.data.sensor_fit,'shift':[o.data.shift_x,o.data.shift_y],'clip':[o.data.clip_start,o.data.clip_end]}
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def add(p):
 n,ri,ro,z,h,a,b,N=[p[k] for k in ['name','ri','ro','z','h','a','b','N']];vs=[]
 for zz in [z,z+h]:
  for rr in [ri,ro]:
   for i in range(N+1):
    t=a+(b-a)*i/N;vs.append((rr*math.sin(t),rr*math.cos(t),zz))
 k=N+1;fs=[]
 for i in range(N):fs.extend([(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
 if abs(b-a-2*math.pi)>1e-7:fs.extend([(0,k,3*k,2*k),(N,2*k+N,3*k+N,k+N)])
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);o.data.materials.append(bpy.data.materials['navy-stage']);o['evidence']='INFERRED low structural connector test; no source-confirmed hidden construction; work units only';return o

def geom(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();vs=[o.matrix_world@v.co for v in m.vertices];fs=[tuple(t.vertices) for t in m.loop_triangles];bm=bmesh.new();bm.from_mesh(m);audit={'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)};bm.free();b=BVHTree.FromPolygons(vs,fs,all_triangles=True);e.to_mesh_clear();return vs,fs,b,audit

def intersect_volume(a,b):
 o=bpy.data.objects.new('temporary-boolean-test',a.data.copy());s.collection.objects.link(o);o.matrix_world=a.matrix_world.copy();m=o.modifiers.new('intersection-test','BOOLEAN');m.operation='INTERSECT';m.solver='EXACT';m.object=b;bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();bm=bmesh.new();bm.from_mesh(me);v=abs(bm.calc_volume(signed=True));f=len(bm.faces);bm.free();e.to_mesh_clear();bpy.data.objects.remove(o,do_unlink=True);return {'volume':v,'faces':f}

before={o.name:meshstate(o) for o in s.objects if o.type=='MESH'};cams={o.name:camera(o) for o in s.objects if o.type=='CAMERA'}
base_names=['stage-central-solid','stage-step-ring','stage-outer-floor'];base={n:geom(s.objects[n])[2] for n in base_names}
new=[add(p) for p in PARAMS];bpy.context.view_layer.update();D={o.name:geom(o) for o in s.objects if o.type=='MESH'}
report={'input_sha256':hashlib.sha256((R/'inputs/keyring-material.blend').read_bytes()).hexdigest(),'parameters':PARAMS,'original_mesh_count':len(before),'original_11_cameras_unchanged':all(camera(s.objects[n])==v for n,v in cams.items()),'original_162_meshes_unchanged':all(meshstate(s.objects[n])==v for n,v in before.items()),'original_mesh_state_sha256':digest(before),'new_meshes':{},'source_status':'FAILED; only hidden-connector hypothesis','mechanical_load_acceptance':'NOT TESTED'}
for o,p in zip(new,PARAMS):
 vs,fs,b,audit=D[o.name];neighbors=[];unexpected=[]
 for n,(vv,ff,bb,aa) in D.items():
  if n==o.name:continue
  gap=max(max(min(v[i] for v in vs)-max(v[i] for v in vv),min(v[i] for v in vv)-max(v[i] for v in vs),0) for i in range(3))
  if gap>1e-7:continue
  pairs=len(b.overlap(bb));vol=intersect_volume(o,s.objects[n]);neighbors.append({'object':n,'bvh_pairs':pairs,'boolean_intersection':vol})
  if n not in p['targets'] and (pairs>0 or vol['volume']>1e-9):unexpected.append(n)
 expected=[x for x in neighbors if x['object'] in p['targets']];assert len(expected)==2 and all(x['boolean_intersection']['volume']>1e-7 and x['bvh_pairs']>0 for x in expected)
 print('AUDIT',o.name,audit,'UNEXPECTED',unexpected,'NEIGHBORS',neighbors,flush=True)
 assert not unexpected and audit['nonmanifold']==0 and audit['degenerate']==0 and audit['signed_volume']>0
 report['new_meshes'][o.name]={'audit':audit,'aabb_candidates':neighbors,'unexpected_surface_or_volume_overlap':unexpected,'state_sha256':digest(meshstate(o))}
allb={**base,**{o.name:D[o.name][2] for o in new}}
def hits(x,y,B):return [{'object':n,'z':q[0].z} for n,b in B.items() if (q:=b.ray_cast(Vector((x,y,5)),Vector((0,0,-1)),10))[0] is not None]
rays={};center=[(x*.2,y*.2) for x in range(-24,25) for y in range(-24,25) if (x*.2)**2+(y*.2)**2<4.85**2]
samples=[('central',center)]
for name,r,a,b in [('step_mid',5.5,-math.pi,math.pi),('outer_mid',7.5,-2,2),('gap_central_step',5.01,-math.pi,math.pi),('gap_step_outer',6.01,-2,2)]:samples.append((name,[(r*math.sin(t:=a+(b-a)*i/180),r*math.cos(t)) for i in range(181)]))
for name,pts in samples:
 rows=[{'xy':[x,y],'before':hits(x,y,base),'after':hits(x,y,allb)} for x,y in pts];rays[name]={'samples':len(rows),'before_hits':sum(bool(x['before']) for x in rows),'after_hits':sum(bool(x['after']) for x in rows),'regressed_samples':[x for x in rows if x['before'] and not x['after']]};
 if name.startswith('gap'):rays[name]['rows']=rows;assert rays[name]['before_hits']==0 and rays[name]['after_hits']==181
 assert not rays[name]['regressed_samples']
# Outside the finite outer angle, bridge 2 must not appear.
o=new[1];testangles=[-math.pi+i*2*math.pi/360 for i in range(361) if abs(-math.pi+i*2*math.pi/360)>.66*math.pi+1e-5];outside=[a for a in testangles if hits(6.01*math.sin(a),6.01*math.cos(a),{o.name:D[o.name][2]})];assert not outside
report['floor_rays']=rays;report['bridge2_outside_angle_probe']={'samples':len(testangles),'hit_angles':outside};report['saved_candidate_model']=False
(R/'results/memory-test.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='floor_rays'},indent=2))
