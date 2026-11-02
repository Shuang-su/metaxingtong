import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
r=Path(__file__).resolve().parents[1];out=r/'versions/R01B';out.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(r/'versions/R01A/ring-remake-R01A-platform-fit.blend'));s=bpy.context.scene
fit=json.loads((r/'qa/shared-inner-arch-conditional-fit.json').read_text());az,Y,Z,R,Df,ef,ff,cyf=fit['params'];cp=fit['camera4k_fixed_platform'];dark=bpy.data.materials['inferred dark skirt'];pink=bpy.data.materials['declared pink state edge'];top=bpy.data.materials['placeholder top NOT source texture']
created=[]
def mesh(n,vs,fs,m):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.data.materials.append(m);created.append(o);return o
# Each arc is a physical thick sweep with closed truncation caps, NOT full unseen ring closure.
def arc(n,center,u,v,radius,width,depth,a0,a1,mat,steps=128):
 c=Vector(center);u=Vector(u).normalized();v=Vector(v).normalized();normal=u.cross(v).normalized();vs=[]
 for i in range(steps+1):
  a=a0+(a1-a0)*i/steps;radial=u*math.cos(a)+v*math.sin(a)
  for rr,dd in [(radius-width,-depth/2),(radius,-depth/2),(radius,depth/2),(radius-width,depth/2)]:vs.append(tuple(c+radial*rr+normal*dd))
 fs=[(3,2,1,0)]
 for i in range(steps):
  for k in range(4):fs.append((4*i+k,4*i+(k+1)%4,4*(i+1)+(k+1)%4,4*(i+1)+k))
 fs.append(tuple(4*steps+k for k in range(4)));return mesh(n,vs,fs,mat)
def ticks(n,center,u,v,rad,a0,a1,count,dep=.44):
 c=Vector(center);u=Vector(u);v=Vector(v);normal=u.cross(v).normalized()
 for i in range(count):
  a=a0+(a1-a0)*i/max(1,count-1);radial=u*math.cos(a)+v*math.sin(a);loc=c+radial*(rad-.22)+normal*(dep/2+.014)
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=f'{n}_TICK_{i:02d}_COUNT_INFERRED';o.dimensions=(.055,.035,.3);o.rotation_euler=(radial).to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(pink);created.append(o)
def arch(n,y,z,rad,width):
 start=math.asin(max(-.999,-z/rad));arc(n,(0,y,z),(1,0,0),(0,0,1),rad,width,.44,start,math.pi-start,dark);ticks(n,(0,y,z),(1,0,0),(0,0,1),rad,start,math.pi-start,34)
arch('ARCH_INNER_CIRCLE_CONDITIONAL',Y,Z,R,.42)
arch('ARCH_MIDDLE_UNDERCONSTRAINED',Y-.6,Z+.15,R+1.02,.48)
arch('ARCH_LARGEST_TOP_UNSEEN',-.6,5.8,11.5,.55)
for side in [-1,1]:
 beta=math.radians(side*-15);u=(math.cos(beta),math.sin(beta),0);v=(0,0,1);center=(side*8.1,1.3,.05)
 arc(f'SIDE_MAIN_{side}_UPPER_ONLY_INFERRED_CAPS',center,u,v,5.4,.46,.55,0,math.pi,dark)
 arc(f'SIDE_MAIN_{side}_EDGE',center,u,v,5.4,.035,.57,0,math.pi,pink)
 center2=(side*8.1,2.3,1.95);start=math.asin(-1.95/2.5)
 arc(f'SIDE_SMALL_TICK_{side}_SEPARATE',center2,u,v,2.5,.27,.32,start,math.pi-start,dark);ticks(f'SIDE_SMALL_{side}',center2,u,v,2.5,start,math.pi-start,22,.32)
# One declared geometric chain plus offset companion hypothesis; not sole camera anchors.
def rod(n,a,b,rad,mat):
 a=Vector(a);b=Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=rad,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);created.append(o)
points=[(-5.1,8.4),(0,5.0),(5.1,8.4),(2.0,3.2),(4.1,.25),(0,2.0),(-4.1,.25),(-2.0,3.2)]
for chain,dy,offset in [('A',0,0),('B',.35,-.25)]:
 ps=[(x,Y-.65+dy,z+offset) for x,z in points]
 for i in range(8):rod(f'STAR_CHAIN_{chain}_{i}_STATE_UNCERTAIN',ps[i],ps[(i+1)%8],.025,pink)
# Curved visible background sectors, one continuous panorama UV coordinate across all panels.
tex=bpy.data.images.load(str(r/'textures/led-continuous-authored-approximation.png'));tex.pack();m=bpy.data.materials.new('LED authored continuous panorama NOT original');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=tex;m.node_tree.links.new(node.outputs['Color'],b.inputs['Base Color']);m.node_tree.links.new(node.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=.5;b.inputs['Roughness'].default_value=.8
for i in range(14):
 a0=math.radians(18+i*144/14);a1=math.radians(18+(i+.94)*144/14);N=12;vs=[]
 for z,rad in [(0,16),(0,16.25),(11,16),(11,16.25)]:
  for k in range(N+1):
   a=a0+(a1-a0)*k/N;vs.append((rad*math.cos(a),rad*math.sin(a),z))
 L=N+1;fs=[]
 for k in range(N):fs.extend([(k,k+1,2*L+k+1,2*L+k),(L+k,3*L+k,3*L+k+1,L+k+1),(k,L+k,L+k+1,k+1),(2*L+k,2*L+k+1,3*L+k+1,3*L+k)])
 fs.extend([(0,2*L,3*L,L),(N,L+N,3*L+N,2*L+N)]);o=mesh(f'LED_PANEL_{i:02d}_BACKSIDE_INFERRED',vs,fs,m);uv=o.data.uv_layers.new()
 for poly in o.data.polygons:
  for idx in poly.loop_indices:
   vtx=o.data.vertices[o.data.loops[idx].vertex_index].co;a=math.atan2(vtx.y,vtx.x);uv.data[idx].uv=((a-math.radians(18))/math.radians(144),vtx.z/11)
# Two observed dark wedges and distinct bright rear equipment class; locations conditional.
for i,x in enumerate([-1.6,1.6]):
 vs=[(x-.55,-2.6,.698),(x+.55,-2.6,.698),(x+.55,-1.9,.698),(x-.55,-1.9,.698),(x-.55,-2.6,.83),(x+.55,-2.6,.83),(x+.55,-1.9,1.08),(x-.55,-1.9,1.08)];fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];mesh(f'DARK_WEDGE_{i}_SOURCE_GROUP',vs,fs,dark)
for i in range(12):
 a=math.radians(25+i*130/11);bpy.ops.mesh.primitive_cube_add(size=1,location=(4.05*math.cos(a),4.05*math.sin(a),.79));o=bpy.context.object;o.name=f'BRIGHT_REAR_FIXTURE_{i}_CLASS_UNCERTAIN';o.dimensions=(.36,.18,.18);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(pink);created.append(o)
def camera(n,D,e,az,f,cx,cy,W,H,roll=0):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=(D*math.cos(e)*math.sin(az),-D*math.cos(e)*math.cos(az),D*math.sin(e));o.rotation_mode='QUATERNION';o.rotation_quaternion=(-o.location).to_track_quat('-Z','Y')@Quaternion((0,0,1),roll);d.sensor_width=36;d.sensor_fit='HORIZONTAL';d.lens=f*36/W;d.shift_x=(W/2-cx)/W;d.shift_y=(cy-H/2)/W;return o
cams=[camera('C_4K_CONDITIONAL',30,cp[0],az,cp[1],cp[2],cp[3],3840,2160,cp[7]),camera('C_FRONT_CONDITIONAL',Df,ef,0,ff,960,cyf,1920,1080),camera('C_OBLIQUE_UNCALIBRATED',7,.05,-math.pi/3,1300,960,980,1920,1080,-.02)]
s.camera=cams[0];s['stage_status']='R01B actual shared superstructure hypothesis, all sources training, no reconstruction acceptance';s['uncertainties']='Circle fit uses ambiguous partial same-layer edges; lower closure/feet and largest top inferred. Side main arcs upper only separate from small scale arcs. Star chains not reliable fixed identities; background panorama authored approximation.'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ring-remake-R01B-shared-candidate.blend'));bpy.ops.export_scene.gltf(filepath=str(out/'ring-remake-R01B-shared-candidate.glb'),export_format='GLB')
(r/'qa/R01B-object-inventory.json').write_text(json.dumps({'new_objects':len(created),'total_meshes':sum(o.type=='MESH' for o in s.objects),'all_inferred_counts':'ticks, fixtures, background panels not fully source-counted','source_camera_names':[o.name for o in cams],'scope':s['uncertainties']},indent=2))
for name,cam in zip(['source4k','front','oblique'],cams):
 s.camera=cam;s.render.resolution_x=960;s.render.resolution_y=540;s.render.filepath=str(out/(name+'-low-material.png'));bpy.ops.render.render(write_still=True)
