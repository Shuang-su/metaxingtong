import bpy,os,math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/Terrace_Working.blend');sc=bpy.context.scene
# Overlay-guided refinement 02: broad tall tree canopy; supported pergola beam grid.
for o in bpy.data.collections['04_Autumn_Tree'].objects:
 if o.name.startswith('Fallen'):continue
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co;p.x=-1.9+(p.x+1.9)*1.43;p.z*=1.48;p.y=1.35+(p.y-1.35)*1.15;v.co=inv@p
# The reference chair is open and sparsely woven at its crown, not a dense cage.
for o in list(bpy.data.objects):
 if o.name.startswith('Egg_chair_back_cross_weave'):
  n=int(o.name.rsplit('.',1)[-1]) if '.' in o.name else 0
  if n%2==0:bpy.data.objects.remove(o,do_unlink=True)
# Pergola and visible left post confirmed by independent low-oblique 45:27 view.
C=bpy.data.collections['06_Cedar_Feature_Wall'];m=bpy.data.materials['white']
def cube(n,l,d):
 bpy.ops.mesh.primitive_cube_add(size=1,location=l);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.data.materials.append(m)
for x in [-4.05,-2.98,-1.91,-.84,.23,1.30]:cube('Pergola_white_depth_beam',(x,.7,4.27),(.075,2.3,.18))
for y in [-.42,.68]:cube('Pergola_white_cross_beam',(-1.35,y,4.27),(5.45,.075,.18))
cube('Pergola_left_visible_support',(-4.07,2.10,2.2),(.14,.14,4.4))
# Source fence has fewer broader slats; stretch gap rhythm while preserving railing height.
for o in bpy.data.collections['02_Fences_Railing'].objects:
 if 'horizontal_cedar_slat' in o.name:o.dimensions.z*=1.25
# Moon placement and size aligned to reference right-panel anchor.
o=bpy.data.objects['Moon_globe_flattened_disk'];o.location.x+=.24;o.location.z+=.11
# Blank canvas records unreadable copyrighted sketch without inventing it.
# Bring camera vertical framing upward slightly, compensate suspended seat independently.
cam=bpy.data.objects['MATCH_A_29m46s'];cam.location=(.15,-10.1,2.47);cam.rotation_euler=(Vector((.15,.65,1.90))-cam.location).to_track_quat('-Z','Y').to_euler()
# Correct wood UV density to prevent board-scale texture magnification.
for o in sc.objects:
 if o.type=='MESH' and ('Deck_board' in o.name or 'cedar' in o.name.lower()):
  uv=o.data.uv_layers.active
  for p in o.data.polygons:
   axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(p.normal[i]))]
   for li,vi in zip(p.loop_indices,p.vertices):v=o.data.vertices[vi].co;uv.data[li].uv=(v[axes[0]]*2,v[axes[1]]*2)
sc.camera=cam;sc.render.filepath=ROOT+'/renders/Iteration_02.png';bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/Terrace_Refined.blend',compress=True);bpy.ops.render.render(write_still=True)
