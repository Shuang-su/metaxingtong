import bpy,math,json
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[1];Q=D/'qa/R07_lantern'
bpy.ops.wm.open_mainfile(filepath=str(D/'models/R07_lantern_trial_material.blend'));s=bpy.context.scene;changes=[]
for ob in list(s.objects):
 if not ob.name.startswith(('LANTERN_round_R0_rib_','LANTERN_string0_10_rib_')):continue
 old=[ob.matrix_world@v.co for v in ob.data.vertices];points=[sum(old[i:i+8],Vector())/8 for i in range(0,len(old),8)];r=sum((old[j]-points[0]).length for j in range(8))/8;v=[];faces=[];u=None;N=8
 for i,p in enumerate(points):
  tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
  if u is None:u=tangent.cross(Vector((0,0,1)) if abs(tangent.z)<.9 else Vector((1,0,0))).normalized()
  else:u=(u-tangent*u.dot(tangent)).normalized()
  w=tangent.cross(u).normalized()
  v.extend(tuple(p+r*(u*math.cos(j*2*math.pi/N)+w*math.sin(j*2*math.pi/N))) for j in range(N))
 for i in range(len(points)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;faces.append((a,b,b+N,a+N))
 faces += [tuple(reversed(range(N))),tuple((len(points)-1)*N+j for j in range(N))]
 me=bpy.data.meshes.new(ob.name+'_parallel_transport');me.from_pydata(v,[],faces);me.update();m=ob.data.materials[0];ob.data=me;ob.matrix_world.identity();ob.data.materials.append(m)
 for f in me.polygons:f.use_smooth=True
 changes.append({'name':ob.name,'radius':r,'same_centreline':True,'sections':len(points)})
(Q/'R07b-rib-frame-changes.json').write_text(json.dumps({'parent':'693a416','change':'parallel transported cross sections replacing abrupt tangent-based reference switch','changed_ribs':changes,'not_changed':'body outline, placement, count, source cameras, paper values, other geometry','suspected_defect_not_yet_source_pass':'visible lower rib breaks in isolated R07 inspection'},indent=2))
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.threads=2;s.cycles.samples=32
for typ in ['material','white']:
 if typ=='white':
  mat=bpy.data.materials.new('WHITE_R07b');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.65,.65,1)
  for o in s.objects:
   if o.type=='MESH':o.data.materials.clear();o.data.materials.append(mat)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/f'models/R07b_lantern_trial_{typ}.blend'));bpy.ops.export_scene.gltf(filepath=str(D/f'models/R07b_lantern_trial_{typ}.glb'),export_format='GLB')
 # source camera native round crop before isolated inspection
 s.camera=bpy.data.objects['SOURCE1'];s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1400/1920;s.render.border_max_x=1700/1920;s.render.border_min_y=1-390/1080;s.render.border_max_y=1-100/1080;s.render.filepath=str(D/f'renders/R07b_round_SOURCE1_nativecrop_{typ}.png');bpy.ops.render.render(write_still=True)
 selected=[o for o in s.objects if o.type=='MESH' and o.name.startswith('LANTERN_round_R0')]
 for o in s.objects:
  if o.type=='MESH':o.hide_render=o not in selected
 p=[o.matrix_world@v.co for o in selected for v in o.data.vertices];center=Vector([(min(v[i] for v in p)+max(v[i] for v in p))/2 for i in range(3)]);cam=bpy.data.cameras.new('R07b_INSPECTION_ONLY');o=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(o);o.location=center+Vector((2,-4,1));o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=2;s.camera=o;s.render.resolution_x=512;s.render.resolution_y=512;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(D/f'renders/R07b_round_INSPECTION_ONLY_{typ}.png');bpy.ops.render.render(write_still=True)
 for o in s.objects:
  if o.type=='MESH':o.hide_render=False
