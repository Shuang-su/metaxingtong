import bpy,math,random,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/C03_right_eave_materials.blend'));s=bpy.context.scene;plant=bpy.data.materials['plant_proxy'];wood=bpy.data.materials['crate_approximate']
def rod(n,a,b,r,m):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o
# One visible nearby bare branch family, exact hidden joins/depth uncertain.
segments=[((5.7,13.3,0),(5.7,13.3,4.2),.11),((5.7,13.3,4.2),(4.5,13.1,6.5),.08),((4.5,13.1,6.5),(4.8,13.1,7.0),.025),((5.7,13.3,3.2),(7.6,13.6,4.1),.07),((7.6,13.6,4.1),(8.4,13.8,5.0),.04),((7.6,13.6,4.1),(8.6,13.8,4.2),.03),((5.1,13.2,5.3),(3.8,12.8,5.6),.035)]
for i,(a,b,r) in enumerate(segments):rod('V02_dead_branch_proxy_'+str(i),a,b,r,wood)
# Nearby prickly-pear silhouette proxies, not an exact counted plant reconstruction.
rod('V03_pad_stem',(6.6,10.8,0),(6.6,10.8,.9),.09,plant)
for i,(c,sc) in enumerate([((6.6,10.8,.95),(.32,.12,.55)),((6.95,10.8,1.5),(.31,.12,.47)),((6.25,10.8,1.4),(.28,.12,.44))]):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=c);o=bpy.context.object;o.name='V03_pad_proxy_'+str(i);o.scale=sc;o.data.materials.append(plant)
# Shared instanced low-poly tuft mesh, no scatter count claimed from screenshots.
grass=bpy.data.materials.new('dry_grass_proxy');grass.use_nodes=True;grass.use_fake_user=True;grass.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.27,.21,.075,1);verts=[];faces=[]
for i in range(6):
 a=math.tau*i/6;dx,dy=math.cos(a),math.sin(a);x,y=dx*.09,dy*.09;k=len(verts);verts.extend([(x-dy*.014,y+dx*.014,0),(x+dy*.014,y-dx*.014,0),(x+dx*.07,y+dy*.07,.13+(i%3)*.03)]);faces.append((k,k+1,k+2))
me=bpy.data.meshes.new('V04_shared_open_grass_sheet');me.from_pydata(verts,[],faces);me.materials.append(grass);rng=random.Random(20261102)
for i in range(60):
 # Bounded sparse context, no far canyon mesh. Exclude central tent footprint interior.
 x=rng.uniform(-6.5,7);y=rng.uniform(-.8,15.5)
 if -3<x<3 and 7<y<13:x+=4 if x>=0 else -4
 o=bpy.data.objects.new('V04_open_tuft_proxy_'+str(i),me);s.collection.objects.link(o);o.location=(x,y,.002);o.rotation_euler.z=rng.random()*math.tau;o.scale=(1,1,rng.uniform(.7,1.4))
# One shared qualitative light correction: ground shadows point left in the sources.
# Direction is an explicit uncalibrated lighting hypothesis, not measured sun data.
sun=bpy.data.objects['shared_sun'];sun.rotation_euler=Vector((-1,.5,-2)).to_track_quat('-Z','Y').to_euler();sun.data.energy=2.0;sun.data.angle=.22
bpy.context.preferences.filepaths.save_version=0;s.render.threads=2;s.cycles.samples=12;bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C04_partial_materials.blend'));(R/'qa/C04_changes.json').write_text(json.dumps({'stage':'C04 limited nearby proxies and shared light hypothesis','core_geometry':'C03 unchanged; source cameras unchanged','new_objects':'one segmented bare-tree proxy, prickly-pear proxy, 60 sparse shared-mesh tufts; counts/hidden branches not verified from source','grass':'intentional open sheets; do not close artificial volumes','light_direction_working':[-1,.5,-2],'source_status':'FAIL/PENDING, material/light approximations not acceptance'},indent=2))
for i in [1,2]:s.camera=bpy.data.objects[f'SOURCE_CONDITIONAL_{i}'];s.render.resolution_x=960;s.render.resolution_y=540;s.render.filepath=str(R/f'renders/C04_SOURCE_CONDITIONAL_{i}_materials.png');bpy.ops.render.render(write_still=True)
white=bpy.data.materials.get('WHITE_GEOMETRY_PERSISTENT');white.use_fake_user=True
for o in s.objects:
 if o.type in {'MESH','CURVE'}:o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C04_partial_white.blend'));print('C04_DONE')
