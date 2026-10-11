import bpy,os,math
from mathutils import Vector
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));bpy.ops.wm.open_mainfile(filepath=R+'/models/Garden_Working.blend');s=bpy.context.scene;s.cycles.use_denoising=False
# V1 visual comparison showed excessive axial depth: door and arch too small and front bed ends cropped.
for o in s.objects:
 if o.type=='MESH':
  # Compress depth in world space, preserving editable object transforms.
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;p.y=-4.7+(p.y+4.7)*.5;v.co=inv@p
# Correct floral arc's characteristic sagging center seen behind performer.
for o in bpy.data.collections['05_Far_Floral_Arch'].objects:
 if o.type=='MESH':
  for v in o.data.vertices:
   if v.co.z>2.75:v.co.z-=.38*math.exp(-(v.co.x/.50)**2)
for name,pos,target,lens in [('MATCH_A_00h25m11s',(.35,-10.9,2.65),(0,4,-.03),29),('MATCH_B_00h21m59s',(0,-10.6,2.65),(0,4,.12),29),('WIDE_Level_Entrance',(0,-14,4.1),(0,-1,2.35),27),('WIDE_Oblique_Visible_Patch',(10,-14,8),(0,-1,2),35)]:
 o=bpy.data.objects[name];o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
# Reduce overbright petals and foreground illumination toward dark livestream mood.
for o in s.objects:
 if o.type=='LIGHT':o.data.energy*=.56
s.world.node_tree.nodes['Background'].inputs[1].default_value=.30
s.camera=bpy.data.objects['MATCH_A_00h25m11s'];s.render.filepath=R+'/renders/v2_match.png';bpy.ops.wm.save_as_mainfile(filepath=R+'/models/Garden_Refined.blend',compress=True);bpy.ops.render.render(write_still=True)
