import bpy,os,math
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));bpy.ops.wm.open_mainfile(filepath=R+'/models/Garden_Refined.blend');s=bpy.context.scene
# Explicit world-scale UV projection fixes primitive cube atlas scaling.
for o in s.objects:
 if o.type!='MESH':continue
 if not o.data.uv_layers:o.data.uv_layers.new()
 if len(o.data.polygons)>200:continue
 for p in o.data.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(p.normal[i]))]
  for li,vi in zip(p.loop_indices,p.vertices):
   co=o.matrix_world@o.data.vertices[vi].co;o.data.uv_layers.active.data[li].uv=(co[axes[0]]*.62,co[axes[1]]*.62)
# Source emphasizes dark vertical bars; diamond leading stays fine and dark.
for o in list(s.objects):
 if o.name.startswith('Leaded_glass_diamond'):bpy.data.objects.remove(o,do_unlink=True)
for name,col in [('blue',(.19,.14,.24)),('purple',(.28,.14,.30)),('pink',(.45,.25,.31)),('rose',(.39,.16,.25)),('cream',(.61,.48,.22)),('white_flower',(.47,.43,.31))]:
 m=bpy.data.materials[name];m.diffuse_color=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1)
# Paving texture is a procedural approximation of source's dark, irregular ornamental slabs.
for o in s.objects:
 if o.name.startswith('Purple_path_paving'):
  for p in o.data.polygons:
   for li,vi in zip(p.loop_indices,p.vertices):
    co=o.matrix_world@o.data.vertices[vi].co;o.data.uv_layers.active.data[li].uv=(co.x/2.58+.5,co.y/.7)
# Extend only ground apron inside the witnessed foreground, never a complete garden.
for o in s.objects:
 if o.name=='INFERRED_thin_support_under_visible_patch':
  for v in o.data.vertices:
   if v.co.y<-.2:v.co.y-=.6
# Raise matched camera slightly while preserving distant entrance height.
o=bpy.data.objects['MATCH_A_00h25m11s'];o.location.z=3.15;o.rotation_euler=(Vector((.37,4,-.16))-o.location).to_track_quat('-Z','Y').to_euler()
s.camera=o;s.render.filepath=R+'/renders/v3_match.png';s.cycles.samples=40;s.cycles.use_denoising=False
bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Garden_Polished.blend',compress=True);bpy.ops.render.render(write_still=True)
