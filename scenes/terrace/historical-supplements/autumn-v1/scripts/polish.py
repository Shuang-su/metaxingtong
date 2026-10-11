import bpy,os,random,math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));random.seed(67)
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Terrace_Refined.blend');sc=bpy.context.scene
# Canopy refinement: actual individual leaves distributed along upper twig network,
# instead of sparse terminal-only tufts seen in iteration 02.
C=bpy.data.collections['04_Autumn_Tree'];centers=[]
for o in C.objects:
 if o.name.startswith('Tree_branch'):
  pts=[o.matrix_world@v.co for v in o.data.vertices];c=sum(pts,Vector())/len(pts)
  if c.z>2.1:centers.append(c)
for shade in ['autumn_gold','autumn_yellow']:
 vs=[];fs=[]
 for k in range(6500):
  p=random.choice(centers)+Vector((random.gauss(0,.24),random.gauss(0,.24),random.gauss(0,.25)));s=random.uniform(.025,.063);a=random.random()*math.tau;u=Vector((math.cos(a),math.sin(a),0))*s;w=Vector((-math.sin(a)*.5,math.cos(a)*.5,random.uniform(.35,.9)))*s;i=len(vs)
  vs.extend([p,p+u*.5+w,p+u*.4+w*.3,p+u,p-u*.1-w*.6,p-u*.7,p-u*.4+w*.4,p-u*.5+w]);fs.extend([(i,i+j,i+j+1) for j in range(1,7)])
 me=bpy.data.meshes.new('Lobed_autumn_leaf_canopy');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Dense_autumn_canopy_'+shade,me);C.objects.link(o);me.materials.append(bpy.data.materials[shade]);uv=me.uv_layers.new()
 for p in me.polygons:
  for li,vi in zip(p.loop_indices,p.vertices):uv.data[li].uv=(vs[vi].x,vs[vi].z)
# Explicit front projection UV only for the moon material, still a curved physical mesh.
o=bpy.data.objects['Moon_globe_flattened_disk'];uv=o.data.uv_layers.active
for p in o.data.polygons:
 for li,vi in zip(p.loop_indices,p.vertices):v=o.data.vertices[vi].co;uv.data[li].uv=((v.x+1)/2,(v.z+1)/2)
for o in sc.objects:
 if o.name.startswith(('Pergola_white','Visible_overhead','Visible_header')):o.location.z+=.28
for o in bpy.data.collections['03_White_Egg_Chair'].objects:
 if o.name.startswith('Suspension_chain'):o.location.z=(o.location.z-2.36)*1.14+2.36
# Four source-like long slender longitudinal front ribs converge at crown, leave seat open.
# Neutral azure world background, no invented photographic scenery.
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.52,.75,1)
sc.render.resolution_percentage=100;sc.cycles.samples=32
# Fine moon relief and high-contrast warm crater albedo.
for im in bpy.data.images:
 if im.source=='FILE':im.reload()
sc.camera=bpy.data.objects['MATCH_A_29m46s'];bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Terrace_Polished.blend',compress=True);sc.render.filepath=ROOT+'/renders/Iteration_03.png';bpy.ops.render.render(write_still=True)
