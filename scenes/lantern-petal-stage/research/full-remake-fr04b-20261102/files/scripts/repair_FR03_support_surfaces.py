# Independent review-driven technical correction, no source camera/layout fit.
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/FR02_material.blend'));s=bpy.context.scene;changes=[]
for o in list(s.objects):
 if not(o.name.startswith('COL_') and o.name.endswith('_roof_support')):continue
 roof=bpy.data.objects['ROOF_'+o.name.split('_')[1]+'_thick_curved_solid'];coords=[o.matrix_world@v.co for v in o.data.vertices];xmin,xmax=min(v.x for v in coords),max(v.x for v in coords);ymin,ymax=min(v.y for v in coords),max(v.y for v in coords);bottom=4.27;N=16;v=[];hits=[]
 for layer in [0,1]:
  for i in range(N+1):
   for j in range(N+1):
    x=xmin+(xmax-xmin)*i/N;y=ymin+(ymax-ymin)*j/N;ok,p,n,f=roof.ray_cast(Vector((x,y,4.31)),Vector((0,0,1)));assert ok,(o.name,x,y);z=p.z+.008 if layer==0 else bottom;v.append((x,y,z));hits.append(p.z)
 K=(N+1)**2;faces=[]
 for layer in [0,1]:
  for i in range(N):
   for j in range(N):a=layer*K+i*(N+1)+j;face=(a,a+N+1,a+N+2,a+1);faces.append(face if layer==0 else tuple(reversed(face)))
 boundary=list(range(N+1))+[i*(N+1)+N for i in range(1,N+1)]+[N*(N+1)+j for j in range(N-1,-1,-1)]+[i*(N+1) for i in range(N-1,0,-1)]
 for i,a in enumerate(boundary):b=boundary[(i+1)%len(boundary)];faces.append((a,b,b+K,a+K))
 me=bpy.data.meshes.new(o.name+'_sampled_roof_underside');me.from_pydata(v,[],faces);me.update();m=o.data.materials[0];o.data=me;o.matrix_world=Matrix.Identity(4);o.data.materials.append(m);o['evidence_grade']='C-inferred support shape fitted to working model roof, NOT source measured joinery';changes.append({'name':o.name,'grid':[17,17],'footprint':[xmin,ymin,xmax,ymax],'bottom':bottom,'roof_underside_hit_range':[min(hits),max(hits)],'intentional_roof_embed':.008})
# Solid annular step carries formerly floating middle metal lip; buried overlaps deliberate.
N=128;r0=4.99;r1=5.09;z0=.05;z1=.23
v=[(r*math.cos(k*2*math.pi/N),r*math.sin(k*2*math.pi/N),z) for r,z in [(r0,z0),(r1,z0),(r1,z1),(r0,z1)] for k in range(N)];faces=[]
for j in range(4):
 for k in range(N):faces.append((j*N+k,j*N+(k+1)%N,((j+1)%4)*N+(k+1)%N,((j+1)%4)*N+k))
me=bpy.data.meshes.new('MIDDLE_STEP_SUPPORT_SOLID');me.from_pydata(v,[],faces);me.update();o=bpy.data.objects.new('STAGE_middle_step_support_inferred',me);s.collection.objects.link(o);o.data.materials.append(bpy.data.materials['pale_column_work_approx']);o['evidence_grade']='C-minimal support for working step, actual source cross section unverified'
report={'status':'FR03 technical repairs only; FR02 retained','roof_supports':changes,'middle_step_support':{'r':[r0,r1],'z':[z0,z1],'core_radial_overlap':.01,'lower_step_vertical_overlap':.025,'middle_lip_vertical_overlap':.025,'middle_lip_radial_overlap':.045,'does_not_fill_pool_opening':True},'unchanged':'all other geometry/material values/cameras/layout/curve hypotheses','not_acceptance':'requires independent surface and connection review, source geometry remains unverified'};(D/'qa/FR03-repair.json').write_text(json.dumps(report,indent=2))
for typ in ['material','white']:
 if typ=='white':
  m=bpy.data.materials.get('WHITE_SHARED') or bpy.data.materials.new('WHITE_SHARED');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/FR03_{typ}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/FR03_{typ}.glb'),export_format='GLB')
files=[]
for f in sorted((D/'models').glob('FR03*')):files.append({'file':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(D/'qa/FR03-checkpoint-files.json').write_text(json.dumps(files,indent=2));print('FR03 saved before rendering')
