import bpy,math,ast,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'models/Classroom_Refined.blend'));sc=bpy.context.scene
COL={c.name:c for c in bpy.data.collections};cur='02_Front_Teaching_Wall'
tree=ast.parse((R/'scripts/build_classroom.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
M={'chalk':bpy.data.materials['Faint verified chalk motifs']}
# Synchronize object transforms explicitly before and after geometric dimension edits.
bpy.context.view_layer.update()
for o in COL['02_Front_Teaching_Wall'].objects:
 if o.name=='Green teaching chalkboard':o.dimensions=(3.8,.072,1.52);o.location=(0,.048,1.68)
 elif o.name.startswith('Board brass edge vertical'):o.location.x=math.copysign(1.90,o.location.x);o.location.z=1.68;o.dimensions.z=1.52
 elif o.name.startswith('Board brass edge horizontal'):o.dimensions.x=3.8;o.location.z=1.68+math.copysign(.76,o.location.z-1.68)
 elif o.name=='Chalk and eraser ledge':o.dimensions.x=3.86;o.location.z=.91
 elif o.name.startswith('Beige side bulletin board'):o.location.x=math.copysign(2.60,o.location.x);o.location.z=1.68;o.dimensions=(1.35,.05,1.52)
 elif o.name.startswith('Bulletin slim dark edge'):
  side=math.copysign(1,o.location.x)
  if 'vertical' in o.name:o.location.x=side*(1.925 if abs(o.location.x)<2.7 else 3.275);o.location.z=1.68;o.dimensions.z=1.52
  else:o.location.x=side*2.60;o.location.z=1.68+math.copysign(.76,o.location.z-1.68);o.dimensions.x=1.35
 elif 'notice' in o.name:o.location.x+=.13
 elif o.name=='Front raised wooden podium':o.location.x=.10;o.dimensions.x=5.4
 elif o.name=='Podium front timber nosing':o.location.x=.10;o.dimensions.x=5.44
for o in COL['03_Bookcase_Books'].objects:o.location.x-=.22
# World-space affine adjustment preserves the table's conventional shape and thickness.
bpy.context.view_layer.update();trans=Matrix.Translation(Vector((-1.15,0,0)))@Matrix.Diagonal((1.25/1.88,1,1,1))@Matrix.Translation(Vector((.92,0,0)))
for o in list(COL['04_Teacher_Desk_Podium'].objects):o.matrix_world=trans@o.matrix_world
for o in COL['08_Small_Observed_Props'].objects:
 if o.name.startswith('Teacher cup') or o.name.startswith('Teacher stacked books') or 'desk ornament' in o.name.lower():o.matrix_world=trans@o.matrix_world
for o in COL['05_Student_Desks_Chairs'].objects:
 if o.name.startswith('Observed_front_right_side_set'):o.location.z-=.20
for o in COL['07_Lights_Clock_Speaker'].objects:
 if o.name.startswith('Clock'):o.location.x+=.22
# Replace the placeholder circle with low-detail traced motifs visible on the board's right.
for o in list(COL['02_Front_Teaching_Wall'].objects):
 if 'Approximate partially occluded chalk doodle perimeter' in o.name or 'Observed chalk star outline' in o.name:bpy.data.objects.remove(o,do_unlink=True)
cur='02_Front_Teaching_Wall'
def chalk(n,coords,cx=-1.12,cz=1.57,scale=.67):return tube(n,[(cx-x*scale,.093,cz+z*scale) for x,z in coords],.0044,M['chalk'])
chalk('Approximate visible chalk character outline',[(-.48,-.19),(-.57,-.06),(-.49,.10),(-.41,.19),(-.35,.40),(-.14,.57),(.12,.61),(.36,.49),(.49,.23),(.49,-.11),(.31,-.31),(.01,-.38),(-.25,-.34),(-.48,-.19)])
chalk('Approximate visible chalk hair fringe',[(-.40,.20),(-.24,.37),(-.10,.30),(-.15,.44),(.05,.35),(.12,.18),(.23,.27),(.38,.17),(.24,.42),(.07,.53),(-.10,.53)])
for cx,cz in [(-1.00,1.58),(-1.23,1.57)]:
 tube('Approximate chalk eye',[(cx+math.cos(a)*.045,.093,cz+math.sin(a)*.043) for a in [i*2*math.pi/16 for i in range(17)]],.004,M['chalk'])
chalk('Approximate chalk smiling mouth',[(-.08,-.13),(.01,-.18),(.12,-.13)])
for cx,cz,rr in [(-.58,1.88,.10),(-1.69,2.11,.09),(-.66,1.30,.08)]:
 pts=[]
 for i in range(11):
  a=math.pi/2+i*math.pi/5;r=rr if i%2==0 else rr*.42;pts.append((cx+math.cos(a)*r,.093,cz+math.sin(a)*r))
 tube('Observed decorative chalk star',pts,.0045,M['chalk'])
# Heart and single music note are identifiable; no unreadable writing is fabricated.
chalk('Observed chalk heart',[(-.18,0),(-.31,.17),(-.28,.30),(-.12,.33),(0,.22),(.13,.33),(.28,.30),(.30,.17),(0,-.12),(-.18,0)],cx=-1.09,cz=2.09,scale=.48)
chalk('Observed chalk music note',[(0,0),(0,.31),(.25,.36),(.25,.05)],cx=-.60,cz=2.11,scale=.40)
for o in sc.objects:
 if o.type=='LIGHT' and o.data.type=='SUN':o.visible_glossy=True;o.visible_transmission=True;o.data.energy=3.2;o.data.angle=.035
bpy.data.materials['Clean window glass'].node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.18
# Separately fit the window oblique view, never deforming desks to match it.
ca=bpy.data.objects['MATCH_B_Windows_00h35m23s'];ca.location=(-.10,4.30,1.20);ca.rotation_euler=(Vector((4,2.60,1.65))-ca.location).to_track_quat('-Z','Y').to_euler();ca.data.lens=28
ca=bpy.data.objects['MATCH_C_Wide_01h11m24s'];ca.rotation_euler=(Vector((.075,0,1.0))-ca.location).to_track_quat('-Z','Y').to_euler()
ca=bpy.data.objects['MATCH_A_Front_00h15m19s'];ca.rotation_mode='QUATERNION';ca.rotation_quaternion=ca.rotation_euler.to_quaternion()@Quaternion((0,0,1),math.radians(2.4));ca.rotation_mode='XYZ'
bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in sc.objects if o.type=='MESH');bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.context.view_layer.update()
sc.cycles.samples=24;sc.view_settings.exposure=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Classroom_Refined.blend'),compress=True)
for n,c in [('QA_Level','PANORAMA_Level_Front'),('QA_Wide','MATCH_C_Wide_01h11m24s'),('QA_Front','MATCH_A_Front_00h15m19s'),('QA_Window','MATCH_B_Windows_00h35m23s')]:
 sc.camera=bpy.data.objects[c];sc.render.filepath=str(R/'renders'/f'{n}.png');bpy.ops.render.render(write_still=True)
print('ADOPT_COMPLETE',flush=True)
