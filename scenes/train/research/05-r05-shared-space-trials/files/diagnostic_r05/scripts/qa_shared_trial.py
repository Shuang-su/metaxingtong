import bpy,bmesh,json,sys,math,collections,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parents[1]/'analysis/qa'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
candidate=Path(args[0]) if args else Path(next(x for x in json.loads((R/'frozen_r03/freeze_manifest.json').read_text())['blends'] if x['kind']=='material')['file'])
def cams():
 return {o.name:{'matrix':[list(row) for row in o.matrix_world], 'location':list(o.location), 'rotation':list(o.rotation_euler),'lens':o.data.lens,'sensor_width':o.data.sensor_width,'sensor_height':o.data.sensor_height,'sensor_fit':o.data.sensor_fit,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y,'type':o.data.type} for o in bpy.context.scene.objects if o.type=='CAMERA' and o.name.startswith(('MATCH_','APPROX_'))}
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'xingtong_train/original/01_train_material.blend')); original_cameras=cams()

if candidate.suffix.lower()=='.glb':
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(candidate))
else:bpy.ops.wm.open_mainfile(filepath=str(candidate))
S=bpy.context.scene;DG=bpy.context.evaluated_depsgraph_get()
report={'candidate':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'camera_equality':original_cameras==cams(),'original_cameras':original_cameras,'candidate_cameras':cams(),'units':{'system':S.unit_settings.system,'scale':S.unit_settings.scale_length},'scene_properties':{k:str(v) for k,v in S.items()},'meshes':[]}
meshdata=[]
for o in S.objects:
 if o.type!='MESH':continue
 eo=o.evaluated_get(DG);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);me.calc_loop_triangles()
 if candidate.suffix.lower()=='.glb':bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-7)
 worldverts=[o.matrix_world@v.co for v in me.vertices]
 bounds=[[min(v[i] for v in worldverts) for i in range(3)],[max(v[i] for v in worldverts) for i in range(3)]]
 row={'name':o.name,'bounds':bounds,'verts':len(me.vertices),'faces':len(me.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_triangles':sum(t.area<1e-12 for t in me.loop_triangles),'triangles':len(me.loop_triangles),'zero_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'zero_edges':sum(e.calc_length()<1e-8 for e in bm.edges),'inconsistent_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'hidden':o.hide_render or o.hide_get(),'materials':[m.name if m else None for m in me.materials], 'properties':{k:str(v) for k,v in o.items()}}
 report['meshes'].append(row)
 polys=[tuple(p.vertices) for p in me.polygons]
 meshdata.append((o.name,worldverts,polys,[c.name for c in o.users_collection],row))
 bm.free();eo.to_mesh_clear()
def make_bvh(predicate):
 vs=[];fs=[];names=[]
 for name,verts,polys,cols,row in meshdata:
  if not predicate(name,cols,row):continue
  off=len(vs);vs.extend(verts);fs.extend(tuple(v+off for v in p) for p in polys);names.extend([name]*len(polys))
 return BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0.0),names
def cast(bvh,origin,direction,dist=10):
 b,n=bvh;p,no,i,t=b.ray_cast(Vector(origin),Vector(direction),dist)
 return {'object':n[i],'distance':t,'point':list(p),'normal':list(no)} if i is not None else None
def isglass(n):return 'glazing' in n or n.startswith('End door rounded glass pane')
allb=make_bvh(lambda n,c,r: not r['hidden'])
opaque=make_bvh(lambda n,c,r:not r['hidden'] and not isglass(n))
glassb=make_bvh(lambda n,c,r:isglass(n))
shellb=make_bvh(lambda n,c,r: any(cn.startswith('01_') for cn in c) or isglass(n) or r['properties'].get('Geometry_role')=='envelope' or n.startswith(('Central warm ivory','Continuous floor','Lower walnut','Window sill','Upper walnut','Sloped wood','Ceiling shoulder','Walnut wall pier','Corner wall','Window side return','Window sill or head','Solid doorway','Door jamb','Door head','Door glass full','Door threshold','End door leaf','End door rounded dark','Continuous side floor skirting')))
roofb=make_bvh(lambda n,c,r:n=='Complete profiled roof solid')
# Each window has a 21 x 21 core scan through its backing depth, plus a glass-presence scan.
report['windows']=[]
for side in [-1,1]:
 for yc in [-4.5,-2.7,-.9,.9,2.7,4.5]:
  blocks=[];missing=[];N=0
  for j in range(21):
   y=yc-.53+j*1.06/20
   for k in range(21):
    z=1.12+k*.56/20;N+=1
    hit=cast(opaque,(side*1.515,y,z),(side,0,0),.25)
    if hit:blocks.append({'y':y,'z':z,**hit})
    if not cast(glassb,(side*1.39,y,z),(side,0,0),.30):missing.append([y,z])
  report['windows'].append({'side':side,'y':yc,'rays':N,'opaque_backing_count':len(blocks),'opaque_examples':blocks[:8],'missing_glass_count':len(missing),'missing_glass_examples':missing[:8]})
# Both door lights: avoid their intentional top crossbar, test center and near border.
report['door_lights']=[]
for side in [-1,1]:
 blocks=[];missing=[];N=0
 for j in range(21):
  x=-.20+j*.40/20
  for k in range(33):
   z=1.34+k*.68/32
   if 1.85<z<1.89:continue
   N+=1;hit=cast(opaque,(x,side*5.50,z),(0,side,0),.30)
   if hit:blocks.append({'x':x,'z':z,**hit})
   if not cast(glassb,(x,side*5.40,z),(0,side,0),.30):missing.append([x,z])
 report['door_lights'].append({'side':side,'rays':N,'opaque_count':len(blocks),'opaque_examples':blocks[:12],'missing_glass_count':len(missing),'missing_glass_examples':missing[:8]})
# End planes across the entire intended interior profile. Extra samples hug sloped roof and corners.
report['end_closure']=[]
for side in [-1,1]:
 misses=[];N=0
 for j in range(325):
  x=-1.62+j*3.24/324
  maxz=2.59 if abs(x)<=.575 else 2.59-(abs(x)-.575)*.245/1.06
  zs=[.004+i*(maxz-.008)/240 for i in range(241)]+[maxz-e for e in [.0005,.001,.003,.005,.01,.02,.04]]
  for z in zs:
   N+=1
   if not cast(shellb,(x,side*5.20,z),(0,side,0),.60):misses.append([x,z])
 report['end_closure'].append({'side':side,'rays':N,'misses':len(misses),'examples':misses[:30]})
# Sidewalls including floor, all window edges, and wall/roof seam; glass is deliberate closure.
report['side_closure']=[]
for side in [-1,1]:
 misses=[];N=0
 ys=[-5.59+i*11.18/560 for i in range(561)]
 for yc in [-4.5,-2.7,-.9,.9,2.7,4.5]:
  ys.extend(yc+d for d in [-.625,-.617,-.615,-.611,-.606,.606,.611,.615,.617,.625])
 zs=[.001+i*2.41/241 for i in range(242)]+[.002,.005,.008,.010,.02,1.075,1.079,1.081,1.085,1.09,1.715,1.719,1.723,1.727,2.34,2.345,2.35,2.355,2.36,2.365,2.37,2.38,2.395,2.41]
 for y in ys:
  for z in zs:
   N+=1
   if not cast(shellb,(side*1.385,y,z),(side,0,0),.40):misses.append([y,z])
 report['side_closure'].append({'side':side,'rays':N,'misses':len(misses),'examples':misses[:30]})
# Roof itself must be a true positive-thickness two-sided shell, including both slopes.
report['roof_test']={'samples':0,'misses':[],'bad_normals':[],'thickness_min':None,'thickness_max':None}
th=[]
for x in [-1.63+i*3.26/326 for i in range(327)]:
 for y in [-5.61,-5.60,-5.55,-5.50,0,5.50,5.55,5.60,5.61]:
  report['roof_test']['samples']+=1
  lower=cast(roofb,(x,y,2),(0,0,1),1);upper=cast(roofb,(x,y,3),(0,0,-1),1)
  if not lower or not upper:report['roof_test']['misses'].append([x,y]);continue
  t=upper['point'][2]-lower['point'][2];th.append(t)
  if lower['normal'][2]>=0 or upper['normal'][2]<=0 or t<=0:report['roof_test']['bad_normals'].append([x,y,t,lower['normal'],upper['normal']])
if th:report['roof_test']['thickness_min']=min(th);report['roof_test']['thickness_max']=max(th)
# Support contact: for each table and seat, straight vertical contact should run from lower body to floor.
report['supports']=[]
for name,verts,polys,cols,row in meshdata:
 if name.startswith('Table brass pedestal'):
  x=(row['bounds'][0][0]+row['bounds'][1][0])/2;y=(row['bounds'][0][1]+row['bounds'][1][1])/2
  names=[];missing=[]
  for z in [.002,.015,.03,.06,.10,.12,.125,.14,.40,.73]:
   h=cast(allb,(x-.16,y,z),(1,0,0),.30)
   if h:names.append([z,h['object']])
   else:missing.append(z)
  report['supports'].append({'name':name,'kind':'table','sample_hits':names,'missing_heights':missing})
 if name.startswith('Seat lower timber plinth'):
  x=(row['bounds'][0][0]+row['bounds'][1][0])/2;y=(row['bounds'][0][1]+row['bounds'][1][1])/2
  h=cast(allb,(x,y,.005),(0,0,-1),.02)
  report['supports'].append({'name':name,'kind':'seat','floor_contact':h})

report['support_chains']=[]
for name,verts,polys,cols,row in meshdata:
 if name.startswith('Table brass pedestal'):
  x=sum(row['bounds'][i][0] for i in [0,1])/2;y=sum(row['bounds'][i][1] for i in [0,1])/2
  needed=['Table circular floor mounting plate','Table pedestal lower continuation','Table brass pedestal']
  parts=[]
  for prefix in needed:
   choices=[r for n,v,p,c,r in meshdata if n.startswith(prefix)]
   chosen=min(choices,key=lambda r:(sum(r['bounds'][i][0] for i in [0,1])/2-x)**2+(sum(r['bounds'][i][1] for i in [0,1])/2-y)**2)
   parts.append(chosen)
  choices=[r for n,v,p,c,r in meshdata if n.startswith('Booth ') and 'rounded wood table' in n]
  chosen=min(choices,key=lambda r:(sum(r['bounds'][i][0] for i in [0,1])/2-x)**2+(sum(r['bounds'][i][1] for i in [0,1])/2-y)**2);parts.append(chosen)
  gaps=[parts[0]['bounds'][0][2]]+[parts[i+1]['bounds'][0][2]-parts[i]['bounds'][1][2] for i in range(3)]
  report['support_chains'].append({'name':name,'parts':[r['name'] for r in parts],'vertical_gaps':gaps,'pass':max(gaps)<1e-5})
 if name.startswith('Seat lower timber plinth'):
  x=sum(row['bounds'][i][0] for i in [0,1])/2;y=sum(row['bounds'][i][1] for i in [0,1])/2
  choices=[r for n,v,p,c,r in meshdata if n.startswith('Seat continuous floor contact foot')]
  chosen=min(choices,key=lambda r:(sum(r['bounds'][i][0] for i in [0,1])/2-x)**2+(sum(r['bounds'][i][1] for i in [0,1])/2-y)**2)
  gaps=[chosen['bounds'][0][2],row['bounds'][0][2]-chosen['bounds'][1][2]]
  report['support_chains'].append({'name':name,'parts':[chosen['name'],name],'vertical_gaps':gaps,'pass':max(gaps)<1e-5})

# Glass shader must be a real transmissive material, not an opaque painted wall.
report['glass_materials']=[]
for m in bpy.data.materials:
 if 'glaz' in m.name.lower() or any(isglass(n) and m.name in row['materials'] for n,v,p,c,row in meshdata):
  shaders=[]
  if m.use_nodes:
   for n in m.node_tree.nodes:
    if n.type=='BSDF_PRINCIPLED':shaders.append({k:(list(n.inputs[k].default_value) if hasattr(n.inputs[k].default_value,'__len__') else n.inputs[k].default_value) for k in ['Base Color','Metallic','Roughness','Alpha','Transmission Weight','IOR'] if k in n.inputs})
  report['glass_materials'].append({'name':m.name,'shaders':shaders})
report['summary']={'mesh_objects':len(meshdata),'vertices':sum(r['verts'] for r in report['meshes']),'faces':sum(r['faces'] for r in report['meshes']),'nonmanifold_objects':[r['name'] for r in report['meshes'] if r['nonmanifold_edges']],'degenerate_objects':[r['name'] for r in report['meshes'] if r['zero_faces'] or r['zero_edges'] or r['degenerate_triangles']],'inconsistent_normal_objects':[r['name'] for r in report['meshes'] if r['inconsistent_edges']],'negative_volume_objects':[r['name'] for r in report['meshes'] if r['signed_volume']< -1e-10]}
out=OUT/(candidate.stem+'_qa.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2));print('QA_REPORT',out,flush=True);print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','original_cameras','candidate_cameras','scene_properties','supports']},ensure_ascii=False,indent=2),flush=True)
