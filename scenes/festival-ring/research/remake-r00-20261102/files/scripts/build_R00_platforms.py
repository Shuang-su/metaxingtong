import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'versions/R00';out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=.5,em=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=em;return m
side=mat('inferred dark skirt',(.025,.022,.045),.3,.35);top=mat('placeholder top NOT source texture',(.065,.04,.11),.3,.3);pink=mat('declared pink state edge',(.6,.015,.22),.2,.35,1);cyan=mat('cyan perimeter fixture',(.02,.5,.5),.1,.3,1);gray=mat('shared white diagnostic',(.65,.65,.65))
objs=[]
def cyl(n,r,z0,z1,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=192,radius=r,depth=z1-z0,location=(0,0,(z0+z1)/2));o=bpy.context.object;o.name=n;o.data.materials.append(material);objs.append(o);return o
# Single watertight cylinder per level. No coincident duplicate top caps.
outer=cyl('P_OUT_single_closed_body',10,-1.4,0,side);outer.data.materials.append(top)
for p in outer.data.polygons:
 if p.normal.z>.5:p.material_index=1
base=cyl('P_IN_lower_base',4.95,0,.26,side)
waist=cyl('P_IN_text_waist_placeholder',4.65,.26,.55,side)
disc=cyl('P_IN_performance_disc',4.55,.55,.67,top)
def annulus(n,r0,r1,z0,z1,m):
 vs=[];N=192
 for z,r in [(z0,r0),(z0,r1),(z1,r0),(z1,r1)]:
  vs.extend([(r*math.cos(2*math.pi*i/N),r*math.sin(2*math.pi*i/N),z) for i in range(N)])
 fs=[]
 for i in range(N):
  j=(i+1)%N;fs +=[(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.data.materials.append(m);objs.append(o);return o
annulus('P_BASE_edge_lip',4.87,4.95,.26,.29,pink);annulus('P_TOP_edge_lip',4.48,4.55,.67,.7,pink)
# Count provisional; visible azimuth ordering not individually confirmed from one frame.
for i in range(64):
 a=2*math.pi*i/64;o=cyl('EDGE_FIXTURE_%02d_PROVISIONAL'%i,.06,0,.035,cyan);o.location.x=9.8*math.cos(a);o.location.y=9.8*math.sin(a)
camdata=bpy.data.cameras.new('C00_CONDITIONAL_NOT_CALIBRATED');cam=bpy.data.objects.new(camdata.name,camdata);bpy.context.collection.objects.link(cam);cam.location=(3,-27,11);target=Vector((0,0,1));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.lens=45;bpy.context.scene.camera=cam
for n,loc,power,size in [('key',(0,-8,14),2200,12),('fill',(-10,1,9),1500,10)]:
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.world.color=(.06,.06,.06);s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.unit_settings.system='NONE';s['stage_status']='R00 platform-only remake, NOT complete scene or source aligned';s['reference']='BV1gttHeGE9Z 53.951826 new native4K; not lost original';s['unknown']='Side arcs, central arches/star, background, characters omitted pending multi-view evidence; platform proportions and skirt depth provisional model units'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ring-remake-R00-platforms.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'ring-remake-R00-platforms.glb'),export_format='GLB')
rows=[]
for o in objs:
 rows.append({'id':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'source_status':'coarse platform-layer hypothesis from actual first source; counts/dimensions not accepted'})
(root/'qa/R00-object-inventory.json').write_text(json.dumps({'objects':rows,'count':len(rows),'source_sha256':'63a2fd0745a2a7623553ae53fe071511b42441b5a3e92b9c520c496436f00c11','units':'arbitrary model units','omitted':'all superstructure, pending multi-view','not_recovered':'new Nov2 script; not original F07'},indent=2))
