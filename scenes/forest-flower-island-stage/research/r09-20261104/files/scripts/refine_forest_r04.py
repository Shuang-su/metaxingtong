import bpy,math,random,pathlib,bmesh
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];random.seed(110404);bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/R03_material.blend'))
src=(ROOT/'scripts/build_forest_r01.py').read_text();exec(src[src.index('def mesh('):src.index('# Finite uneven earth')]);bark=bpy.data.materials['Bark'];leaf=bpy.data.materials['Leaf'];soil=bpy.data.materials['Moss_and_earth']
white=bpy.data.materials.get('WHITE_clay')
if white is None:white=bpy.data.materials.new('WHITE_clay');white.diffuse_color=(.65,.65,.65,1);white.use_nodes=True;white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.65,.65,1)
# Wider scalloped cup petals based on visible flower family; not exact flower species.
flower_records=[]
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name.startswith('FLOWER_') and '_petal_' in ob.name:
  name=ob.name;idx=int(name.split('_')[1]);pet=int(name.split('_')[-1]);mat=ob.data.materials[0]
  centres={0:(-2.8,1,.85),1:(-2.45,1.8,.8),2:(-1.4,2.6,1),3:(1.1,2.7,.9),4:(2.7,1.1,.95),5:(2.95,.1,.65),6:(1.1,-2.65,.55),7:(-.95,-2.7,.5),8:(-2.6,-1.2,.7)}
  x,y,h=centres[idx];bpy.data.objects.remove(ob,do_unlink=True);vs=[];fs=[];rows=9;cols=9
  for side in [-1,1]:
   for k in range(rows):
    t=k/(rows-1);r=.045+.48*t;z=4.5+h-.18+.46*t**.6-.10*t**4
    for j in range(cols):
     u=j/(cols-1)-.5;a=pet*math.tau/5+u*1.6*math.sin(math.pi*(.12+.72*t));edge=.035*math.sin(u*math.pi*5)*t**4
     vs.append((x+r*math.cos(a),y+r*math.sin(a),z+edge+side*.008))
  K=rows*cols
  for side in [0,K]:
   for k in range(rows-1):
    for j in range(cols-1):q=side+k*cols+j;fs.append((q,q+1,q+cols+1,q+cols))
  boundary=list(range(cols))+[r*cols+cols-1 for r in range(1,rows)]+[(rows-1)*cols+j for j in range(cols-2,-1,-1)]+[r*cols for r in range(rows-2,0,-1)]
  for j,a in enumerate(boundary):b=boundary[(j+1)%len(boundary)];fs.append((a,b,b+K,a+K))
  mesh(name,vs,fs,mat,'Broad curved scalloped cup petals inferred from source silhouette; exact petal overlap and backside unverified')
# Working-domain extension to avoid known visible cutoff in R03 wide render; not recovered forest limits.
terrain=bpy.data.objects['TERRAIN_finite_working_domain'];terrain.scale.x=2;terrain.scale.y=2;terrain['inference']='Finite32-radius terrain working envelope; true forest extent unknown, not measured boundary'
# Dense multilevel finite forest, exact trees beyond identified anchor are proxies.
for i in range(20):
 a=i*math.tau/20;r=random.uniform(17,26);x,y=r*math.cos(a),r*math.sin(a);height=random.uniform(22,30)
 tube('FAR_TREE_%02d'%i,[(x,y,-.1),(x+.3,y,5),(x-.4,y+.2,12),(x+.3,y,height)],[random.uniform(.5,.9),.5,.38,.12],bark,16)
 for j in range(3):
  a2=j*math.tau/3+i;tip=(x+4*math.cos(a2),y+4*math.sin(a2),height-2+j)
  tube('FAR_TREE_%02d_branch_%d'%(i,j),[(x,y,height*.5),(x+2*math.cos(a2),y+2*math.sin(a2),height*.8),tip],[.25,.13,.03],bark,10)
 items=[]
 for k in range(1800):
  a2=random.random()*math.tau;r2=4.5*math.sqrt(random.random());items.append(((x+r2*math.cos(a2),y+r2*math.sin(a2),random.uniform(height-7,height)),.65,.25,(random.uniform(-1,1),random.uniform(-1,1),.2)))
 leaves('FAR_TREE_%02d_crown'%i,items,leaf)
for i,(x,y) in enumerate([(-7,9),(-4,12),(4,10),(8,7),(-9,4),(8,12),(.5,6),(-10,-3),(10,-2)]):
 items=[]
 for k in range(2200):
  a=random.random()*math.tau;r=4.5*math.sqrt(random.random());items.append(((x+r*math.cos(a),y+r*math.sin(a),random.uniform(10,19)),random.uniform(.3,.6),random.uniform(.1,.22),(random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.3,.5))))
 leaves('NEAR_TREE_dense_crown_%02d'%i,items,leaf)
# More physically textured bark; same procedural shader across all source and check cameras.
n=bark.node_tree.nodes;l=bark.node_tree.links;tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=12;tex.inputs['Detail'].default_value=5;coord=n.new('ShaderNodeTexCoord');mp=n.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(3,3,.4);l.new(coord.outputs['Generated'],mp.inputs[0]);l.new(mp.outputs['Vector'],tex.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.025,.022,.012,1);ramp.color_ramp.elements[1].color=(.20,.16,.08,1);l.new(tex.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
# Explicit world illumination, no fog painted over geometry residuals.
s=bpy.context.scene;s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.30,.42,.50,1);bg.inputs['Strength'].default_value=.3
bpy.data.objects['SUN_fixed'].data.energy=3.5
# Additional actual source views: pose remains conditional, no physical animation values claimed.
def cam(name,loc,target,lens):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name=name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o['source_width']=1920;o['source_height']=1080
cam('SOURCE_E_under',(7,-9,1.6),(-1.5,0,4.4),38)
cam('SOURCE_F_top',(8,-9,16),(0,0,6),50)
s.camera=bpy.data.objects['SOURCE_F_top'];s.cycles.use_denoising=False;s.cycles.samples=32
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R04_material.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R04_material.glb'),export_format='GLB',export_apply=True,export_cameras=True)
for o in s.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/R04_white.blend'));bpy.ops.export_scene.gltf(filepath=str(ROOT/'models/R04_white.glb'),export_format='GLB',export_apply=True,export_cameras=True)
print('R04_SAVED',len([o for o in s.objects if o.type=='MESH']))
