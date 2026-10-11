import bpy,math,json,random,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/Classroom_Blockout_Textured.blend'))
COL={c.name:c for c in bpy.data.collections};cur='02_Front_Teaching_Wall'
# Reuse geometry helpers only; do not rerun scene assembly.
tree=ast.parse((R/'scripts/build_classroom.py').read_text());funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef)];exec(compile(ast.Module(body=funcs,type_ignores=[]),'helpers','exec'))
M={n:bpy.data.materials[n] for n in ['Plaster','Ceiling','DeskOak','FloorOak','Chalkboard','Cork']}
for k,n in [('black','Charcoal painted metal'),('metal','Warm grey tubular steel'),('paper','Unprinted pale paper'),('glass','Clean window glass'),('white','Chalk white'),('rubber','Dark rubber feet'),('darkwood','Dark edge stained wood'),('mint','Pale jade notebook'),('blue','Desk cup blue ceramic')]:M[k]=bpy.data.materials[n]
# Verified right-side doorway. Replace wall with wall segments around the opening.
cur='01_Observed_Enclosure';bpy.data.objects.remove(bpy.data.objects['Right pale blue side wall'],do_unlink=True)
y0=.60;y1=1.64;top=2.22
box('Right wall front door-side pier',(4.10,y0/2,1.675),(.20,y0,3.35),M['Plaster'])
box('Right wall beyond observed door',(4.10,(8.2+y1)/2,1.675),(.20,8.2-y1,3.35),M['Plaster'])
box('Right wall doorway lintel',(4.10,(y0+y1)/2,(3.35+top)/2),(.20,y1-y0,3.35-top),M['Plaster'])
cur='02_Front_Teaching_Wall'
box('Observed dark door leaf',(4.045,1.12,1.09),(.055,.94,2.18),M['darkwood'],.005)
for yy in [y0-.025,y1+.025]:box('Dark door jamb',(3.996,yy,1.13),(.14,.10,2.26),M['black'])
box('Dark door header',(3.996,1.12,2.22),(.14,1.14,.10),M['black'])
# Pale elongated glazing inset observed in door; exact external corridor unverified.
gl=mat('Door pale frosted glazing',(.73,.78,.61),.34);p=gl.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.57,.64,.40,1);p.inputs['Emission Strength'].default_value=.22
box('Door long narrow frosted glazing',(4.010,1.12,1.43),(.017,.34,.89),gl,.004)
rod('Door metal pull',(3.955,.78,1.0),(3.955,.78,1.18),.013,M['metal'])
green=mat('Green illuminated exit sign',(.035,.35,.14),.5);p=green.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.01,.25,.03,1);p.inputs['Emission Strength'].default_value=.9
box('Observed green exit sign',(3.97,1.12,2.50),(.042,.50,.16),green,.008)
# Directional marks only, no invented unreadable letterforms.
box('Exit pictogram doorway',(3.943,1.255,2.505),(.012,.055,.112),M['paper'],.001)
for ya,yb,za,zb in [(1.18,.98,2.5,2.5),(.98,1.04,2.5,2.54),(.98,1.04,2.5,2.46)]:rod('Exit observed white direction mark',(3.940,ya,za),(3.940,yb,zb),.008,M['paper'])
cur='08_Small_Observed_Props'
cyl('Observed dark corner wastebasket',(3.67,.55,.185),.17,.37,M['black'],vertices=32);cyl('Wastebasket dark opening',(3.67,.55,.377),.14,.012,M['rubber'],vertices=32)
red=mat('Observed fire extinguisher red enamel',(.46,.036,.022),.42)
cyl('Observed red fire extinguisher cylinder',(3.31,.38,.235),.081,.43,red,vertices=24);box('Fire extinguisher pale label',(3.31,.462,.27),(.095,.005,.18),M['paper'],.001);cyl('Extinguisher neck',(3.31,.38,.48),.028,.07,M['black']);rod('Fire extinguisher handle',(3.24,.38,.511),(3.37,.38,.511),.012,M['black'])
for o in list(bpy.data.objects):
 if o.name.startswith('Small front-right wall loudspeaker'):o.name='Observed front-right CCTV dark housing'
 if o.name.startswith('Loudspeaker centre'):o.name='Observed CCTV pale circular lens surround'
# Side single desk visible adjacent to teacher table in front-right corner.
cur='05_Student_Desks_Chairs'
for o in list(COL[cur].objects):
 if o.name.startswith('R1C4'):
  q=o.copy();q.data=o.data.copy();COL[cur].objects.link(q);q.name=o.name.replace('R1C4','Observed_front_right_side_set');q.location+=Vector((.47,-1.36,.20))
# Replace shallow rectangular chair backs with normal-scale arched plywood backs.
backs=[o for o in COL[cur].objects if 'chair curved-back oak panel' in o.name]
for o in backs:
 name=o.name;cx,cy,cz=o.location;cz+=.035;bpy.data.objects.remove(o,do_unlink=True)
 # Width 0.39m, lower z=0.62, upper z=0.89. Deliberate modest curvature.
 outline=[(-.195,-.117),(.195,-.117),(.195,.074)]+[(.195*math.cos(a),.074+.068*math.sin(a)) for a in [i*math.pi/16 for i in range(1,17)]]
 vs=[]
 for side in [-1,1]:
  for x,z in outline:vs.append((cx+x,cy+side*.013-.10*x*x,cz+z))
 n=len(outline);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);COL[cur].objects.link(ob);me.materials.append(M['DeskOak']);uvbox(ob)
 # Back screw heads, circular and geometrically distinct.
 for dx in [-.16,.16]:
  for dz in [-.075,.050]:cyl(name+' screw',(cx+dx,cy+.018-.10*dx*dx,cz+dz),.005,.007,M['metal'],rot=(math.pi/2,0,0),vertices=12)
# Front fascia with actual perforations built once and linked across desk positions.
fascia=mat('Observed aged ochre metal desk fascia',(.43,.25,.115),.35,.52)
# Source desks are seen with a metal perforated edge on side opposite the chair.
positions=[(o.location.x,o.location.y,o.location.z) for o in COL[cur].objects if 'rounded oak desktop' in o.name]
for idx,(x,y,z) in enumerate(positions):
 strip=box('Desk perforated ochre front rail %02d'%idx,(x,y-.210,z-.073),(.58,.021,.091),fascia,.002)
 for dx in [-.22,-.14,.14,.22]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.018,depth=.045,location=(x+dx,y-.210,z-.073),rotation=(math.pi/2,0,0));cut=bpy.context.object
  mod=strip.modifiers.new('Real round punched hole','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=strip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 uvbox(strip)
 box('Desk front empty label mount',(x,y-.224,z-.073),(.105,.006,.049),M['metal'],.002)
# Window masonry piers have substantial observed width. Four repeat bays were provisional;
# keep 3 plausible wide bays while explicitly disclosing total count is unresolved.
cur='06_Window_Wall'
for o in list(COL[cur].objects):bpy.data.objects.remove(o,do_unlink=True)
box('Observed left window sill wall',(-4.08,4.1,.45),(.18,8.2,.9),M['Plaster'])
box('Observed left window upper spandrel',(-4.08,4.1,3.2),(.18,8.2,.30),M['Plaster'])
for i in range(3):
 y=1.38+i*2.70;ow=2.29
 for yy in [y-ow/2,y+ow/2]:box('Window bay %d side dark mullion'%i,(-3.984,yy,1.995),(.10,.052,2.19),M['black'])
 for z in [.90,1.44,2.53,3.09]:box('Window bay %d crossbar'%i,(-3.984,y,z),(.10,ow,.047),M['black'])
 for yy in [y-ow/6,y+ow/6]:box('Window bay %d narrow vertical'%i,(-3.984,yy,1.995),(.095,.048,2.19),M['black'])
 for j in range(3):
  for k,(zz,h) in enumerate([(1.17,.51),(1.985,1.045),(2.81,.515)]):box('Window glass %d_%d_%d'%(i,j,k),(-4.012,y-ow/3+j*ow/3,zz),(.009,ow/3-.050,h),M['glass'],0)
 box('Window sill stone ledge %d'%i,(-3.94,y,.895),(.30,ow+.04,.045),M['Ceiling'])
 if i<2:box('Window plaster pier %d'%i,(-4.02,y+1.35,1.99),(.23,.41,2.19),M['Plaster'])
for yy,w in [(.102,.20),(8.132,.136)]:box('Window side end masonry',(-4.02,yy,1.99),(.23,w,2.19),M['Plaster'])
# Exterior remains intentionally approximate, fix facade attachment positions.
for i in range(15):
 b=bpy.data.objects.get('INFERRED exterior city block %02d'%i)
 if b:
  for o in bpy.data.objects:
   if o.name=='INFERRED facade glazing %d'%i or o.name.startswith('INFERRED facade glazing %d.'%i):o.location.x=b.location.x+b.dimensions.x/2+.009

# Front blackboard proportions validated against the complete classroom wide view.
cur='02_Front_Teaching_Wall'
for o in list(COL[cur].objects):
 if o.name=='Green teaching chalkboard':o.dimensions.x=3.8;o.dimensions.z=1.65
 elif o.name.startswith('Board brass edge vertical'):o.location.x=math.copysign(1.90,o.location.x);o.dimensions.z=1.65
 elif o.name.startswith('Board brass edge horizontal'):o.dimensions.x=3.8;o.location.z=1.62+math.copysign(.825,o.location.z-1.62)
 elif o.name=='Chalk and eraser ledge':o.dimensions.x=3.86;o.location.z=.780
 elif o.name.startswith('Beige side bulletin board'):o.location.x=math.copysign(2.725,o.location.x);o.dimensions.z=1.65
 elif o.name.startswith('Bulletin slim dark edge'):
  o.location.x-=math.copysign(.335,o.location.x)
  if 'vertical' in o.name:o.dimensions.z=1.65
  else:o.location.z=1.62+math.copysign(.825,o.location.z-1.62)
 elif 'notice' in o.name:o.location.x-=.335
 elif o.name=='Front raised wooden podium':o.location.x=.4;o.dimensions.x=6.2
 elif o.name=='Podium front timber nosing':o.location.x=.4;o.dimensions.x=6.24
# Genuine teacher table construction, four legs and a modesty apron.
cur='04_Teacher_Desk_Podium'
for o in list(COL[cur].objects):
 if 'end panel' in o.name or 'panel seam' in o.name:bpy.data.objects.remove(o,do_unlink=True)
 elif 'modesty panel' in o.name:o.location.z=.75;o.dimensions.z=.43
for xx in [.09,1.75]:
 for yy in [.50,1.06]:box('Teacher table solid square leg',(xx,yy,.565),(.064,.064,.73),M['DeskOak'],.004)
box('Teacher table underside side apron L',(.09,.78,.89),(.044,.57,.20),M['DeskOak'])
box('Teacher table underside side apron R',(1.75,.78,.89),(.044,.57,.20),M['DeskOak'])
# Narrow five-shelf bookcase with twin lower cupboard doors, now clearly visible.
cur='03_Bookcase_Books'
for o in list(COL[cur].objects):bpy.data.objects.remove(o,do_unlink=True)
bx=-2.98;by=.31;bw=.83
box('Five-shelf bookcase timber back',(bx,.20,1.05),(bw,.035,2.1),M['DeskOak'])
for x in [bx-bw/2,bx+bw/2]:box('Bookcase tall side',(x,by,1.05),(.036,.30,2.1),M['DeskOak'])
for z in [.02,.37,.715,1.06,1.405,1.75,2.095]:box('Bookcase shelf',(bx,by,z),(bw+.036,.33,.030),M['DeskOak'])
for x in [bx-.204,bx+.204]:
 box('Bookcase lower cupboard door',(x,.486,.19),(.393,.028,.34),M['DeskOak'],.004)
 rod('Bookcase small curved door handle',(x+(.14 if x<bx else -.14),.51,.18),(x+(.14 if x<bx else -.14),.523,.155),.008,M['darkwood'])
bookm=[m for m in bpy.data.materials if m.name.startswith('Book cloth')]
random.seed(43)
for si,z in enumerate([.397,.742,1.087,1.432,1.777]):
 x=bx-.36
 for j in range(12):
  w=random.uniform(.034,.057);h=random.uniform(.235,.30)
  if x+w>bx+.36:break
  box('Book shelf%d spine%02d'%(si,j),(x+w/2,.408,z+h/2),(w,.17,h),bookm[(j+si)%len(bookm)],.0015,rot=(0,random.choice([0,0,.05,-.05]),0));x+=w+.010
# Front-left twin upright plant in red pot, observed in wide 1:05:12 frame.
cur='08_Small_Observed_Props';plant=mat('Observed plant leaves',(.17,.31,.055),.77);pot=mat('Observed oxblood plant pot',(.25,.035,.022),.47)
cyl('Observed red plant pot',(-3.60,.49,.18),.16,.32,pot,vertices=32)
for dx,h in [(-.065,1.04),(.07,1.20)]:
 base=Vector((-3.60+dx,.49,.30));rod('Plant upright stem',base,base+Vector((dx*.4,0,h)),.009,M['darkwood'])
 for k in range(11):
  a=k*2.39;zz=.14+k*(h-.2)/11;end=base+Vector((math.sin(a)*.12,math.cos(a)*.10,zz+.15));start=base+Vector((0,0,zz));rod('Plant small leaf stem',start,end,.004,plant)
  bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=1,location=end);ob=finish(bpy.context.object,'Observed plant narrow leaf',plant,0,True);ob.scale=(.030,.014,.10);ob.rotation_euler=(.40*math.cos(a),.60*math.sin(a),a)
# Right wall also has high strip windows in the complete wide view.
cur='01_Observed_Enclosure';bpy.data.objects.remove(bpy.data.objects['Right wall beyond observed door'],do_unlink=True)
box('Right wall door-to-window pier',(4.10,1.895,1.675),(.20,.51,3.35),M['Plaster'])
box('Right window sill wall',(4.10,5.175,.525),(.20,6.05,1.05),M['Plaster'])
box('Right window upper wall',(4.10,5.175,2.975),(.20,6.05,.75),M['Plaster'])
cur='06_Window_Wall'
for yy in [2.18,3.185,4.19,5.195,6.20,7.205,8.18]:box('Observed right-window vertical frame',(3.984,yy,1.825),(.10,.055,1.55),M['black'])
for zz in [1.05,1.63,2.60]:box('Observed right-window continuous bar',(3.984,5.18,zz),(.10,6.05,.048),M['black'])
rightgl=mat('Right window pale diffuse glazing',(.83,.85,.72),.28);b=rightgl.node_tree.nodes.get('Principled BSDF');b.inputs['Emission Color'].default_value=(.71,.76,.60,1);b.inputs['Emission Strength'].default_value=.38
for i in range(6):
 for zz,hh in [(1.34,.53),(2.115,.92)]:box('Right side pale glass pane',(4.011,2.68+i*1.005,zz),(.009,.94,hh),rightgl,0)
box('Right window long ledge',(3.94,5.18,1.045),(.25,6.10,.035),M['Ceiling'])
# Four clearly visible ceiling fixtures (two rows); no unsupported third row.
for o in list(bpy.data.objects):
 if ('fixture suspension' in o.name or 'fluorescent' in o.name) and o.location.y>5.5:bpy.data.objects.remove(o,do_unlink=True)
# Fix an exposed rectangular light reflection in the glazing, keep genuine glass.
for o in bpy.data.objects:
 if o.type=='LIGHT':o.visible_glossy=False;o.visible_transmission=False
p=bpy.data.materials['Unlit monitor glass'].node_tree.nodes.get('Principled BSDF');p.inputs['Specular IOR Level'].default_value=.07
# Camera is solved separately from physical furniture; frame A is low and upward looking.
ca=bpy.data.objects['MATCH_A_Front_00h15m19s'];ca.location=(-.05,6.15,1.45);ca.rotation_euler=(Vector((-.02,0,2.48))-ca.location).to_track_quat('-Z','Y').to_euler();ca.data.lens=28
cur='99_Cameras_Lighting'
cam('MATCH_C_Wide_01h11m24s',(0,8.0,1.0),(0,0,1.0),19.35)
cam('MATCH_D_Front_Left_01h05m12s',(-1.35,4.67,1.07),(-1.12,0,1.18),24)
# Coordinate correction: viewed from +Y, image-left is world +X. Mirror the physical scene,
# then re-orient cameras with right-handed upright rotations, avoiding negative camera scales.
from mathutils import Matrix
reflect=Matrix.Diagonal((-1,1,1,1))
for o in list(bpy.data.objects):
 if o.type=='MESH':o.matrix_world=reflect@o.matrix_world
 elif o.type in ['CAMERA','LIGHT']:
  direction=o.matrix_world.to_3x3()@Vector((0,0,-1));direction.x*=-1;o.location.x*=-1;o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in bpy.data.objects if o.type=='MESH');bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

sc=bpy.context.scene;sc.cycles.samples=18
sc['inferences']='Metric dimensions; 8x8.2m footprint; 4x4 student set plus observed front-right set; three wide window bays; unseen back wall, six light repetition and generic exterior are inferred. No readable blackboard/notice text reconstructed.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Classroom_Refined.blend'),compress=True)
for n,ca in [('Refined_Front','MATCH_A_Front_00h15m19s'),('Refined_Window','MATCH_B_Windows_00h35m23s'),('Refined_Panorama','PANORAMA_Level_Front'),('Refined_Desks','DETAIL_Desks_Podium'),('Refined_WideMatch','MATCH_C_Wide_01h11m24s'),('Refined_LeftMatch','MATCH_D_Front_Left_01h05m12s')]:
 sc.camera=bpy.data.objects[ca];sc.render.filepath=str(R/'renders'/f'{n}.png');bpy.ops.render.render(write_still=True)
print('REFINEMENT_COMPLETE',flush=True)
