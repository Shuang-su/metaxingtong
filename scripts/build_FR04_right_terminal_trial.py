# Finite RIGHT visible terminal roof/edge turn only. No inferred mirrored left wing/room/new columns.
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(D/'models/FR03_source_material.blend'));s=bpy.context.scene;created=[];L=1.1;turn=-math.radians(20);a=math.radians(-45);mid=(6.95+9.8)/2;rad=Vector((math.cos(a),math.sin(a)));tan=Vector((math.sin(a),-math.cos(a)))
def pt(u,t):
 angle=a+turn*max(u,0)/L;axis=Vector((math.cos(angle),math.sin(angle)));c=mid*rad+tan*u;xy=c+axis*((6.95+(9.8-6.95)*t)-mid);z=4.4+.45*math.sin(math.pi*t)+.12*(max(u,0)/L)**2-.01;return (xy.x,xy.y,z)
def patch(n,u0,u1,t0,t1,thick,mat,N=12,W=12,lift=0):
 v=[]
 for layer in [0,1]:
  for i in range(N+1):
   for j in range(W+1):
    x,y,z=pt(u0+(u1-u0)*i/N,t0+(t1-t0)*j/W);v.append((x,y,z+lift-layer*thick))
 K=(N+1)*(W+1);f=[]
 for layer in [0,1]:
  for i in range(N):
   for j in range(W):q=layer*K+i*(W+1)+j;face=(q,q+1,q+W+2,q+W+1);f.append(face if layer==0 else tuple(reversed(face)))
 b=list(range(W+1))+[i*(W+1)+W for i in range(1,N+1)]+[N*(W+1)+j for j in range(W-1,-1,-1)]+[i*(W+1) for i in range(N-1,0,-1)]
 for i,x in enumerate(b):y=b[(i+1)%len(b)];f.append((x,y,y+K,x+K))
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);o.data.materials.append(mat);o['evidence_grade']='C-visible right roof turn kind; length/angle/cross-section inferred, not entire entrance';created.append(n);return o
roofmat=bpy.data.materials['gray_tiles_work_approx'];gold=bpy.data.materials['bronze_work_approx'];patch('ENTRY_R_visible_turn_roof_trial',-.08,L,0,1,.14,roofmat);patch('ENTRY_R_inner_thick_edge_trial',-.08,L,-.01,.035,.28,gold,12,1,.02);patch('ENTRY_R_outer_thick_edge_trial',-.08,L,.965,1.01,.28,gold,12,1,.02);patch('ENTRY_R_terminal_thick_edge_trial',L-.06,L+.02,-.01,1.01,.24,gold,1,12,.02)
for i in range(9):
 u=i*L/8
 for j in range(6):
  p=Vector(pt(u,j/6));q=Vector(pt(u,(j+1)/6));p.z+=.025;q.z+=.025;d=q-p;bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.045,depth=d.length,location=(p+q)/2);o=bpy.context.object;o.name=f'ENTRY_R_tile_{i}_{j}';o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(roofmat);o['evidence_grade']='C-conditional tiled terminal surface';created.append(o.name)
report={'scope':'finite right entry/eave turn hypothesis only, not complete entrance or source accepted','working_length':L,'working_turn_degrees':-20,'working_upturn':.12,'roof_thickness':.14,'back_overlap_length':.08,'created':created,'no_new_columns':True,'no_left_mirror':True,'existing_layout_camera_unchanged':True,'support_scope':'new patch volume overlaps prior right arc end; thick inner/outer edge bands join existing finite eave, not structural load proof','limits':['exact angle/length/ridge topology not measured','left entry masked/cropped remains unbuilt','full known mismatch: pool and roof radius too small under current illustrative camera','no invented room or90degree corridor','contact checks pending']};(D/'qa/FR04-right-terminal-trial.json').write_text(json.dumps(report,indent=2))
for typ in ['material','white']:
 if typ=='white':
  m=bpy.data.materials.get('WHITE_SHARED') or bpy.data.materials.new('WHITE_SHARED');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/FR04_{typ}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/FR04_{typ}.glb'),export_format='GLB')
files=[]
for f in sorted((D/'models').glob('FR04*')):files.append({'file':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(D/'qa/FR04-checkpoint-files.json').write_text(json.dumps(files,indent=2));print('FR04 actual checkpoint saved')
