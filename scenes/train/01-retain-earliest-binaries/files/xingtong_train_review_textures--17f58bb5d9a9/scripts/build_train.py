import bpy, math, json, random, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.collections):
 if d.name!='Collection':bpy.data.collections.remove(d)
base=bpy.data.collections.get('Collection');base.name='00_Scene'
COL={}
for name in ['01_Carriage_shell','02_Windows_and_curtains','03_Booth_seating','04_Wall_tables','05_Luggage_racks','06_Ceiling_fixtures','07_End_wall_details','08_Flowers','09_Lights','10_Cameras']:
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);COL[name[:2]]=c

def link(o,col):
 for c in list(o.users_collection):c.objects.unlink(o)
 COL[col].objects.link(o);return o

def simple(name,color,rough=.5,metal=0,emit=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if emit:b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=emit
 return m

def pbr(stem,name,roughscale=1):
 m=simple(name,(.3,.3,.3));n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord')
 for ch,cs in [('basecolor','sRGB'),('roughness','Non-Color'),('normal','Non-Color')]:
  t=n.new('ShaderNodeTexImage');t.name='UV '+ch;t.image=bpy.data.images.load(str(R/'textures'/f'{stem}_{ch}.png'));t.image.colorspace_settings.name=cs;t.image.pack();l.new(tc.outputs['UV'],t.inputs['Vector'])
  if ch=='basecolor':l.new(t.outputs['Color'],b.inputs['Base Color'])
  elif ch=='roughness':l.new(t.outputs['Color'],b.inputs['Roughness'])
  else:
   nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.38;l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],b.inputs['Normal'])
 return m
wood=pbr('walnut','Walnut veneer | authored UV PBR');tablemat=pbr('rosewood','Polished reddish table wood | authored UV PBR');leather=pbr('forest_leather','Dark forest green leather | authored UV PBR');curtainmat=pbr('burgundy_velvet','Burgundy draped fabric | authored UV PBR');ceilingmat=pbr('ceiling_cream','Warm ivory ceiling | authored UV PBR');floor=pbr('floor_wood','Dark walnut floorboards | authored UV PBR')
metal=simple('Blackened bronze racks and edging',(.045,.032,.023),.3,.75);brass=simple('Aged satin brass details',(.32,.19,.071),.28,.7);black=simple('Dark rubber gasket',(.012,.012,.01),.6);glass=simple('Dark night window glazing',(.010,.018,.017),.16,.55);cream=simple('Aged ivory fittings',(.49,.40,.29),.55);lamp=simple('Warm white lamp diffuser',(.92,.76,.48),.4,0,3);sign=simple('Green illuminated destination sign',(.014,.21,.10),.45,0,.35);signtext=simple('Dim green sign glyphs',(.19,.59,.35),.45,0,.3);vase=simple('Terracotta flower vase',(.45,.15,.083),.29);stemmat=simple('Flower stems',(.06,.12,.038),.7);petalmat=simple('Ochre and orange flower petals',(.65,.28,.058),.7)

def uv_metric(o,scale=1):
 me=o.data
 if not me.uv_layers:uv=me.uv_layers.new(name='UVMap')
 else:uv=me.uv_layers.active
 for p in me.polygons:
  normal=p.normal;a=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=a]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*scale,v[axes[1]]*scale)

def cube(name,loc,dim,mat,col,bev=0,uvscale=1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link(o,col)
 if mat:o.data.materials.append(mat)
 uv_metric(o,uvscale)
 if bev:
  m=o.modifiers.new('Rounded physical edges','BEVEL');m.width=bev;m.segments=3;m.affect='EDGES';m=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o

def cyl(name,a,b,r,mat,col,vertices=16):
 mid=(Vector(a)+Vector(b))*.5;d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=mid);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);link(o,col)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o

def sphere(name,loc,scale,mat,col,segments=16,rings=8):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);link(o,col)
 for p in o.data.polygons:p.use_smooth=True
 return o

def custom(name,verts,faces,mat,col):
 me=bpy.data.meshes.new(name+' mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);COL[col].objects.link(o);me.materials.append(mat);uv_metric(o);return o

# Nominal dimensions constrained to a consistent human-scale carriage, not a measured train.
W=3.0;H=2.60;L=10.5;end=L/2;bay_centers=[-3.65,-1.25,1.15,3.55]
cube('Continuous floor shell',(0,0,-.07),(3.12,L+.2,.14),floor,'01',.025,4)
for side in [-1,1]:
 x=side*1.535
 cube('Lower walnut wainscot',(x,0,.46),(.09,L,.92),wood,'01',.02)
 cube('Window sill wooden rail',(side*1.465,0,.94),(.13,L,.085),wood,'01',.018)
 cube('Upper walnut header',(x,0,2.22),(.11,L,.32),wood,'01',.012)
 cube('Lower dado cap brass',(side*1.477,0,.90),(.018,L,.012),brass,'01',.004)
 # Side ceiling shoulders with actual sloping geometry.
 verts=[(side*.58,-end,2.60),(side*1.50,-end,2.36),(side*1.50,end,2.36),(side*.58,end,2.60)]
 custom('Sloped wood ceiling shoulder',verts,[(0,1,2,3)],wood,'01')
 cube('Ceiling shoulder longitudinal moulding',(side*.585,0,2.575),(.046,L,.056),wood,'01',.01)
 for i,y in enumerate(bay_centers):
  # Window opening is a gap in the wall, never a photograph of the interior.
  winw=1.66;winh=1.12;zc=1.53
  cube(f'Window {side} {i+1} real dark glazing',(side*1.502,y,zc),(.018,winw,winh),glass,'02',.025)
  for yy in [y-winw/2-.035,y+winw/2+.035]:cube('Window vertical moulding',(side*1.471,yy,zc),(.078,.09,winh+.12),wood,'02',.018)
  for zz in [zc-winh/2-.022,zc+winh/2+.025]:cube('Window horizontal moulding',(side*1.47,y,zz),(.08,winw+.16,.06),wood,'02',.012)
  cube('Window mid sash',(side*1.466,y,1.59),(.025,winw,.019),metal,'02',.004)
  # Inter-window wall piers and brass coat hooks.
  py=y+1.20
  if py<end:
   cube('Walnut wall pier',(x,py,1.52),(.095,.68,1.19),wood,'01',.012)
   for dy in [-.15,.15]:
    cyl('Coat hook stem',(side*1.47,py+dy,1.90),(side*1.405,py+dy,1.90),.012,brass,'02');cyl('Coat hook upturn',(side*1.405,py+dy,1.90),(side*1.405,py+dy,1.935),.011,brass,'02')
  # Draped curtain sheets with sculpted folds and gathered waist.
  for edge in [-1,1]:
   verts=[];faces=[];nu=18;nv=36
   for j in range(nv+1):
    z=.83+(2.105-.83)*j/nv;t=(z-.83)/(2.105-.83);width=.25-.125*math.exp(-((z-1.22)/.19)**2)
    yc=y+edge*(.82-width/2)
    for k in range(nu+1):
     u=k/nu;yy=yc+width*(u-.5);xx=side*(1.405-.033*math.sin(u*math.pi*10)-.018*math.cos(t*math.pi*2));verts.append((xx,yy,z))
   for j in range(nv):
    for k in range(nu):a=j*(nu+1)+k;faces.append((a,a+1,a+nu+2,a+nu+1))
   o=custom('Red gathered curtain',verts,faces,curtainmat,'02');sol=o.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.004
   for p in o.data.polygons:p.use_smooth=True
   cube('Curtain gathered brass tie',(side*1.398,y+edge*.77,1.23),(.012,.125,.027),brass,'02',.012)
  cyl('Curtain pole',(side*1.405,y-.9,2.11),(side*1.405,y+.9,2.11),.018,brass,'02')
 # End infill beside last window.
 for yy in [-end+.17,end-.15]:cube('Corner wall infill',(x,yy,1.52),(.09,.35,1.20),wood,'01',.015)
 # Open slatted luggage rack.
 rx=side*1.12
 for xx in [side*.88,side*1.43]:cyl('Rack continuous edge rail',(xx,-end+.15,2.19),(xx,end-.15,2.19),.018,metal,'05')
 for yy in [(-end+.2)+.16*k for k in range(64)]:cyl('Rack transverse slat',(side*.90,yy,2.18),(side*1.44,yy,2.18),.009,metal,'05',10)
 for yy in [-4.75,-2.4,0,2.4,4.75]:
  cyl('Rack triangular diagonal support',(side*.9,yy,2.19),(side*1.47,yy,2.40),.016,metal,'05');cyl('Rack wall bracket',(side*1.47,yy,2.15),(side*1.47,yy,2.40),.016,metal,'05')
 # Subtle alternating luggage silhouettes, supported on rack.
 for j,yy in enumerate([-3.4,.1,3.4]):
  o=cube('Luggage case | inferred clutter',(side*1.23,yy,2.32),(.40,.68,.19),wood,'05',.055);cube('Luggage leather strap',(side*1.23,yy,2.423),(.33,.07,.012),metal,'05',.003)

cube('Central warm ivory ceiling',(0,0,2.62),(1.15,L,.09),ceilingmat,'01',.03)
# End wall with a genuine framed door and small inset glass window.
for ey in [-end,end]:
 for xx in [-1.045,1.045]:cube('End walnut side panel',(xx,ey,1.25),(.99,.11,2.50),wood,'01',.012)
 cube('End wall header',(0,ey,2.40),(3.0,.12,.32),wood,'01',.02)
 cube('End door leaf',(0,ey-.025 if ey>0 else ey+.025,1.15),(.90,.085,2.30),wood,'07',.032)
 for xx in [-.50,.50]:cube('End door vertical black jamb',(xx,ey-.079 if ey>0 else ey+.079,1.16),(.044,.026,2.32),metal,'07',.006)
 cube('End door top jamb',(0,ey-.08 if ey>0 else ey+.08,2.32),(1.04,.03,.04),metal,'07',.006)
 yy=ey-.078 if ey>0 else ey+.078
 cube('End door rounded dark window frame',(0,yy,1.68),(.41,.048,.84),metal,'07',.09)
 cube('End door rounded glass pane',(0,yy-.026 if ey>0 else yy+.026,1.68),(.338,.014,.765),glass,'07',.067)
 cube('End door glass divider',(0,yy-.04 if ey>0 else yy+.04,1.87),(.35,.022,.023),metal,'07',.004)
 cyl('Door brass handle',(.34,yy-.04,1.06),(.34,yy-.04,1.24),.022,brass,'07')
 cube('Door destination sign housing',(0,yy,2.475),(.89,.075,.14),metal,'07',.018)
 cube('Door destination sign green glass',(0,yy-.04 if ey>0 else yy+.04,2.475),(.83,.012,.086),sign,'07',.008)
 # Reference lettering is illegible: use neutral light bars, do not invent text.
 for k in range(12):cube('Illegible sign marker',(-.34+k*.039,yy-.047 if ey>0 else yy+.047,2.475),(.026,.008,.020),signtext,'07',.001)
 cube('End left notice frame',(-.78,yy,1.65),(.155,.025,.285),brass,'07',.008)
 cube('End left notice cream paper',(-.78,yy-.019 if ey>0 else yy+.019,1.65),(.12,.009,.247),cream,'07',.003)
 cube('End left notice red band',(-.78,yy-.025 if ey>0 else yy+.025,1.71),(.093,.008,.06),curtainmat,'07',.002)
 cube('End right switch panel',(.88,yy,1.16),(.19,.022,.27),brass,'07',.01)

# Rounded wall-mounted table polygon. Curved aisle end is real mesh.
def make_table(side,y,i):
 # Inward semicircle meets the rectangular wall-attached half.
 cx=side*.70;radius=.36;outer=side*1.45
 arc=[]
 # Orient plan polygon around its perimeter.
 if side==1:
  pts=[(outer,y-.36),(cx,y-.36)]+[(cx-radius*math.cos(a),y+radius*math.sin(a)) for a in [(-math.pi/2)+math.pi*k/24 for k in range(25)]]+[(outer,y+.36)]
 else:
  pts=[(outer,y+.36),(cx,y+.36)]+[(cx+radius*math.cos(a),y+radius*math.sin(a)) for a in [(math.pi/2)-math.pi*k/24 for k in range(25)]]+[(outer,y-.36)]
 verts=[(x,yy,z) for z in [.745,.795] for x,yy in pts];n=len(pts);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 o=custom(f'Booth {side} {i} rounded wood table',verts,faces,tablemat,'04');b=o.modifiers.new('Table edge rounding','BEVEL');b.width=.014;b.segments=3;o.modifiers.new('Table normals','WEIGHTED_NORMAL')
 cyl('Table brass pedestal',(side*.92,y,.12),(side*.92,y,.745),.045,metal,'04');cyl('Table wall underside brace',(side*.92,y,.47),(side*1.45,y,.73),.023,metal,'04')
 # Pink ceramic vase with a narrow neck, actual revolved surface.
 fx=side*.70;fy=y+.04;rings=[(0,.034),(.018,.048),(.068,.052),(.11,.036),(.145,.019),(.177,.022)];vs=[];fs=[]
 for z,rr in rings:
  for k in range(20):a=k*2*math.pi/20;vs.append((fx+rr*math.cos(a),fy+rr*math.sin(a),.795+z))
 for j in range(len(rings)-1):
  for k in range(20):a=j*20+k;b=j*20+(k+1)%20;fs.append((a,b,b+20,a+20))
 o=custom('Small terracotta table vase',vs,fs,vase,'08')
 for p in o.data.polygons:p.use_smooth=True
 random.seed(i+side*13)
 for j in range(7):
  a=j*2.4;rr=.05+random.random()*.025;tip=(fx+rr*math.cos(a),fy+rr*math.sin(a),1.035+random.random()*.07)
  cyl('Flower green stem',(fx,fy,.955),tip,.003,stemmat,'08',6)
  sphere('Flower dark center',tip,(.017,.017,.014),brass,'08',10,6)
  for k in range(7):
   a=k*math.pi*2/7;p=(tip[0]+.023*math.cos(a),tip[1]+.023*math.sin(a),tip[2]);o=sphere('Flower ochre petal',p,(.021,.012,.006),petalmat,'08',8,4);o.rotation_euler.z=a

for side in [-1,1]:
 for i,y in enumerate(bay_centers):
  xc=side*.97
  for direction in [-1,1]:
   by=y+direction*.86
   cube(f'Booth {side} {i+1} base',(xc,by-direction*.15,.26),(1.01,.56,.44),leather,'03',.09,2)
   cube(f'Booth {side} {i+1} seat cushion',(xc,by-direction*.19,.48),(1.01,.56,.17),leather,'03',.07,2)
   o=cube(f'Booth {side} {i+1} high back',(xc,by,.915),(1.055,.185,1.02),leather,'03',.08,2);o.rotation_euler.x=direction*math.radians(-3)
   # Discrete piping follows the cushion boundary and adds readable structure.
   cyl('Seat top leather piping',(xc-.47,by-direction*.104,1.384),(xc+.47,by-direction*.104,1.384),.009,leather,'03')
   for xx in [xc-.49,xc+.49]:cyl('Seat edge leather piping',(xx,by-direction*.109,.57),(xx,by-direction*.109,1.35),.007,leather,'03')
   # Dark wood plinth under each seat.
   cube('Seat lower timber plinth',(xc,by-direction*.11,.065),(.97,.53,.11),wood,'03',.02)
  make_table(side,y,i)

# Repeating central inset lamps, access panels and louvred ventilation grilles.
def area(name,loc,energy,size,size_y=None,rot=(0,0,0),color=(1,.73,.44)):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='RECTANGLE';d.size=size;d.size_y=size_y or size;o=bpy.data.objects.new(name,d);COL['09'].objects.link(o);o.location=loc;o.rotation_euler=rot;return o
for i,y in enumerate(bay_centers):
 cyl('Central round ceiling fitting',(0,y-.53,2.565),(0,y-.53,2.602),.10,cream,'06',32)
 cube('Central rectangular ceiling access',(0,y+.10,2.561),(.35,.53,.035),cream,'06',.03)
 for xx in [-.35,.35]:
  cube('Vent grille frame',(xx,y+.10,2.55),(.22,.39,.035),cream,'06',.008)
  cube('Vent grille dark recess',(xx,y+.10,2.529),(.184,.335,.012),metal,'06',.001)
  for yy in [y-.05+k*.046 for k in range(7)]:cube('Vent louvre',(xx,yy,2.52),(.177,.014,.02),cream,'06',.002)
 for side in [-1,1]:
  cube('Central ceiling side fluorescent',(side*.58,y-.35,2.55),(.035,.62,.025),lamp,'06',.009)
  cube('Window head warm strip housing',(side*1.395,y,2.115),(.056,.35,.035),metal,'06',.008)
  cube('Window head warm strip diffuser',(side*1.368,y,2.107),(.016,.29,.019),lamp,'06',.006)
  area('Window header soft lamp',(side*1.32,y,2.04),8,.30,.14,color=(1,.82,.59))
 area('Ceiling diffuse pool',(0,y,2.49),45,.83,1.65,color=(1,.73,.45))
 # Bounce into ceiling so fixtures are legible without a fake photograph.
 area('Indirect ceiling upward',(0,y,2.13),12,.76,1.3,rot=(math.pi,0,0),color=(1,.75,.51))
area('Camera-side room bounce',(0,-4.72,1.78),30,2,1.1,rot=(math.radians(74),0,0),color=(1,.81,.62))

# All cameras share the exact same immutable geometry.
def cam(name,loc,target,lens):
 d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.035;d.clip_end=100;o=bpy.data.objects.new(name,d);COL['10'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o
cam('MATCH_A_15m19_right_booth',(.89,-4.19,1.30),(.40,2.3,1.68),24)
cam('MATCH_B_45m12_left_booth',(-.86,-4.19,1.46),(-1.92,2.3,1.54),24)
cam('MATCH_C_60m16_aisle',(0,.05,1.63),(0,end,1.77),22)
cam('QA_WIDE_LEVEL_AISLE',(0,-4.82,1.60),(0,4.6,1.60),18)
cam('QA_REVERSE_LEVEL_AISLE',(0,4.76,1.60),(0,-4.6,1.60),18)
cam('QA_SIDE_BOOTH',(-.20,-1.25,1.62),(1.5,-1.25,1.45),18)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.cycles.max_bounces=6;s.cycles.diffuse_bounces=4;s.cycles.glossy_bounces=3;s.render.resolution_x=1188;s.render.resolution_y=668;s.render.resolution_percentage=65;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.075,.09,.12,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.05
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.3
s.unit_settings.system='METRIC';s['Geometry_scope']='One single consistent repeated booth carriage. Four bays per side is inferred, not fully measured.';s['Scale_status']='Nominal metres from human-scale priors, no original dimensions.';s['Reference_video']='https://www.bilibili.com/video/BV1fMP4ziEUd/';s['PBR_maps']='18 original raster PBR maps; basecolor roughness normal; packed and UV-mapped.';s['Exterior']='Dark glazing only; unseen exterior not reconstructed.'
s.camera=bpy.data.objects['QA_WIDE_LEVEL_AISLE'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'train_v01.blend'))
for cname in ['QA_WIDE_LEVEL_AISLE','MATCH_A_15m19_right_booth','MATCH_B_45m12_left_booth','MATCH_C_60m16_aisle']:
 s.camera=bpy.data.objects[cname];s.render.filepath=str(R/'renders'/f'v01_{cname}.png');bpy.ops.render.render(write_still=True)
(R/'analysis/scene_parameters_v01.json').write_text(json.dumps({'width':W,'length':L,'height':H,'bay_centers':bay_centers,'booth_back_top':1.425,'table_top':.795,'floor':0,'note':'Estimated dimensions. Number of bays inferred.'},indent=2))
print('TRAIN_V01_READY')
