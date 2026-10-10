import bpy,bmesh,math,json,hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'deliverables'
bpy.ops.wm.open_mainfile(filepath=str(R/'original/01_train_material.blend'))
S=bpy.context.scene
C={c.name[:2]:c for c in bpy.data.collections}
C['12']=bpy.data.collections.new('12_Full_carriage_completion');S.collection.children.link(C['12'])
wood=bpy.data.materials['Walnut veneer | authored UV PBR'];metal=bpy.data.materials['Blackened bronze racks and edging'];brass=bpy.data.materials['Aged satin brass details'];glass=bpy.data.materials['Dark night window glazing'];black=metal.copy();black.name='Dark rubber gasket';black.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.012,.012,.01,1);black.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=0;black.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65;floor=bpy.data.materials['Dark walnut floorboards | authored UV PBR']
def uv(o):
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
 u=o.data.uv_layers.active
 for f in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;u.data[li].uv=(v[axes[0]],v[axes[1]])
def link(o,col='12'):
 for c in list(o.users_collection):c.objects.unlink(o)
 C[col].objects.link(o);o['Completion_scope']='Consistent full-carriage construction; inferred unseen structure';return o
def cube(name,loc,dim,mat,col='12',bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link(o,col);o.data.materials.append(mat);uv(o)
 if bevel:m=o.modifiers.new('Small physical edge bevel','BEVEL');m.width=bevel;m.segments=2
 return o
def prism(name,poly,y0,y1,mat,col='12'):
 n=len(poly);v=[(x,y,z) for y in [y0,y1] for x,z in poly];f=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);C[col].objects.link(o);me.materials.append(mat);uv(o);return o
def cyl(name,x,y,z0,z1,r,mat,col='12'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=z1-z0,location=(x,y,(z0+z1)/2));o=bpy.context.object;o.name=name;link(o,col);o.data.materials.append(mat);return o
def apply(o):
 bpy.context.view_layer.objects.active=o
 for m in list(o.modifiers):
  try:bpy.ops.object.modifier_apply(modifier=m.name)
  except RuntimeError:pass
def boolean(o,cutter):
 m=o.modifiers.new('True modeled through-aperture','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;apply(o)
def rounded_rect(w,h,r,n=8):
 pts=[]
 for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for k in range(n+1):
   a=math.radians(start+k*90/n);pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
 return pts
# Complete outer body. It is a finite shell, with every modeled side-window opening cut through it.
for side in [-1,1]:
 sidewall=cube(('Left' if side<0 else 'Right')+' full sidewall with six true apertures',(side*1.565,0,1.145),(.14,11.22,2.55),wood)
 sidewall['Geometry_role']='envelope'
 for y in [-4.5,-2.7,-.9,.9,2.7,4.5]:
  cut=cube('temporary window cutter',(side*1.565,y,1.53),(.5,1.232,1.135),wood)
  boolean(sidewall,cut);bpy.data.objects.remove(cut,do_unlink=True)
  # Four reveal pieces create a continuous return between interior surround and exterior skin.
  for dy in [-.616,.616]:cube('Window side return '+str(side),(side*1.545,y+dy,1.53),(.18,.018,1.153),wood)
  for z in [.9625,2.0975]:cube('Window sill or head return '+str(side),(side*1.545,y,z),(.18,1.25,.018),wood)
 # Continuous low skirting is joined to floor and wall, not a view-specific patch.
 cube('Continuous side floor skirting '+str(side),(side*1.484,0,.075),(.038,11.14,.15),wood,bevel=.004)
# Structural roof volume behind retained observed interior roof finishes.
roof_poly=[(-1.635,2.345),(-.575,2.590),(.575,2.590),(1.635,2.345),(1.635,2.465),(.58,2.71),(-.58,2.71),(-1.635,2.465)]
roof=prism('Complete profiled roof solid',roof_poly,-5.615,5.615,wood);roof['Geometry_role']='envelope'
cube('Continuous underfloor structural solid',(0,0,-.095),(3.27,11.23,.11),floor)['Geometry_role']='envelope'
# Replace overlapping box end panels with a full profile that meets both sloping shoulders.
for o in list(bpy.data.objects):
 if o.name.startswith(('End walnut side panel','End wall header')):bpy.data.objects.remove(o,do_unlink=True)
profile=[(-1.635,-.09),(1.635,-.09),(1.635,2.405),(.58,2.655),(-.58,2.655),(-1.635,2.405)]
for side in [-1,1]:
 wall=prism(('Observed forward' if side>0 else 'Inferred reverse')+' profiled end wall',profile,side*5.55-.06,side*5.55+.06,wood);wall['Geometry_role']='envelope';wall['Evidence']='forward end supported; reverse end inferred consistently' if side>0 else 'inferred reverse end, not source-confirmed'
 cut=cube('temporary true doorway cutter',(0,side*5.55,1.1525),(.914,.6,2.315),wood);boolean(wall,cut);bpy.data.objects.remove(cut,do_unlink=True)
 for x in [-.477,.477]:cube('Solid doorway side return',(x,side*5.55,1.158),(.054,.22,2.316),wood)
 cube('Solid doorway head return',(0,side*5.55,2.314),(1.00,.22,.045),wood)
 cube('Door threshold',(0,side*5.55,.012),(1.07,.25,.024),brass,bevel=.003)
 # Rabbet/gasket closes the modeled door seam behind the movable leaf.
 for x in [-.448,.448]:cube('Door jamb backstop gasket',(x,side*5.573,1.15),(.028,.021,2.30),black)
 cube('Door head backstop gasket',(0,side*5.573,2.294),(.906,.021,.04),black)
 for z in [.45,1.89]:cyl('Door hinge barrel',-.445,side*5.467,z,z+.14,.018,brass)
 # Existing opaque frame and wood leaf are genuinely drilled, preserving original silhouettes.
 leaves=[o for o in bpy.data.objects if o.name.startswith('End door leaf') and o.location.y*side>0]
 frames=[o for o in bpy.data.objects if o.name.startswith('End door rounded dark window frame') and o.location.y*side>0]
 opening=[(x,z+1.68) for x,z in rounded_rect(.45,.745,.038)]
 cut=prism('temporary rounded door-light cutter',opening,side*5.55-.35,side*5.55+.35,wood)
 for o in leaves+frames:boolean(o,cut);o['Geometry_role']='envelope'
 bpy.data.objects.remove(cut,do_unlink=True)
 # Long return prevents detached glass decal appearance when inspected from the outer end.
 outside=[(x,z+1.68) for x,z in rounded_rect(.51,.805,.057)]
 inner=prism('Door glass full-depth dark reveal',outside,side*5.55-.11,side*5.55+.065,metal)
 cut=prism('temporary reveal inner cutter',opening,side*5.55-.3,side*5.55+.3,wood);boolean(inner,cut);bpy.data.objects.remove(cut,do_unlink=True)
 # Exterior ring is structural completion, not a claim about the real vehicle exterior.
 inner['Evidence']='Inferred end glazing rebate'
# Furniture: retain placement and silhouettes; add real load paths.
for o in list(bpy.data.objects):
 if o.name.startswith('Table brass pedestal'):
  x,y,_=o.location;cyl('Table pedestal lower continuation',x,y,.02,.132,.045,metal);cyl('Table circular floor mounting plate',x,y,-.001,.027,.125,metal)
  for a in range(4):ang=a*math.pi/2;cyl('Table foot anchor bolt',x+.086*math.cos(ang),y+.086*math.sin(ang),.025,.033,.008,brass)
 if o.name.startswith('Seat lower timber plinth'):
  cube('Seat continuous floor contact foot',(o.location.x,o.location.y,.008),(.94,.50,.018),black,bevel=.002)
 if o.name.startswith('Luggage case'):
  o.location.z=2.270;o.scale.z*=.160/.190;o['Evidence']='Inferred luggage size constrained to supported rack clearance'
 if o.name.startswith('Luggage leather strap'):o.location.z=2.357
for side in [-1,1]:
 for y in [-4.5,-2.7,-.9,.9,2.7,4.5]:
  cube('Table wall attachment plate',(side*1.478,y,.699),(.052,.20,.13),metal,bevel=.003)
  cube('Table wall edge mounting cleat',(side*1.474,y,.764),(.060,.62,.046),wood,bevel=.003)
# All decorative surfaces acquire physical thickness. Vases get a closed base and an open mouth.
for o in list(bpy.data.objects):
 if o.type!='MESH' or any(c.name.startswith('11_') for c in o.users_collection):continue
 if o.name.startswith('Small terracotta table vase'):
  bm=bmesh.new();bm.from_mesh(o.data);base=[v for v in bm.verts if abs(v.co.z-.795)<1e-5];bm.faces.new(list(reversed(base)));bm.to_mesh(o.data);bm.free()
  m=o.modifiers.new('Ceramic wall and base thickness','SOLIDIFY');m.thickness=.003;m.offset=-1
 elif o.name.startswith(('Leather subtle tufted face','Sloped wood ceiling shoulder','Verified destination sign face')):
  m=o.modifiers.new('Physical surface thickness','SOLIDIFY');m.thickness=.003 if o.name.startswith('Leather') else .012 if o.name.startswith('Sloped') else .001;m.offset=0
# Apply modifiers for portable, independently auditable meshes; weld duplicate plan endpoints.
changes={'normals_recalculated':0,'meshes_cleaned':0}
for o in list(bpy.data.objects):
 if o.type!='MESH' or any(c.name.startswith('11_') for c in o.users_collection):continue
 apply(o);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=bm.edges,dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=bm.faces)
 bm.to_mesh(o.data);bm.free();o.data.update();changes['meshes_cleaned']+=1
 if not o.data.uv_layers:uv(o)
 o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
 if o.name.startswith('Window ') and 'glazing' in o.name:o['Geometry_role']='glazing';o['Aperture']='True opening through sidewall; finite transparent pane'
 if o.name.startswith('End door rounded glass pane'):o['Geometry_role']='glazing'
# No unverified adjacent carriage or city is part of this interior deliverable.
for o in list(C['11'].objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(C['11'])
# Keep exact A/B/D source cameras, distinct from inspection cameras.
def camera(name,loc,target,lens=20):
 d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.025;d.clip_end=100;d.sensor_width=36;o=bpy.data.objects.new(name,d);C['10'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();o['Role']='inspection view, not source evidence';return o
camera('INSPECT_01_forward_aisle',(0,-5.15,1.57),(0,5.4,1.57),18)
camera('INSPECT_02_reverse_aisle',(0,5.15,1.57),(0,-5.4,1.57),18)
camera('INSPECT_03_right_booth',(-.24,-.90,1.64),(1.50,-.90,1.30),18)
camera('INSPECT_04_left_booth',(.24,.90,1.64),(-1.50,.90,1.30),18)
camera('INSPECT_05_ceiling',(0,-3.0,1.13),(0,2.5,2.53),18)
camera('INSPECT_06_floor_supports',(0,-2.7,.40),(.96,.1,.27),18)
camera('INSPECT_07_forward_door',(0,3.82,1.39),(0,5.50,1.40),18)
camera('INSPECT_08_reverse_door',(.05,-3.82,1.39),(0,-5.50,1.40),18)
camera('INSPECT_09_exterior_front',(5.5,9.0,5.2),(0,1.1,1.1),32)
camera('INSPECT_10_exterior_reverse',(-5.5,-9.0,4.5),(0,-1.1,1.1),32)
camera('INSPECT_11_cutaway',(5.8,-8.8,5.8),(0,.1,.9),30)
# Honest dimensional convention, replacing historical metre labels.
S.unit_settings.system='NONE';S.unit_settings.scale_length=1
S['Scale_status']='All dimensions are inferred model units, not measured metres.'
S['Nominal_dimensions']='Model units: inside width ~3.0; length 11.1; central height ~2.6; table 0.795; back ~1.28. Not measured metric dimensions.'
S['Exterior']='No outside city, adjacent carriage, bogie or exact train make is asserted. Finite outer shell only.'
S['Geometry_scope']='Complete finite carriage shell, 12 side apertures, 2 true glazed door lights, supported furniture; shared geometry for all cameras.'
S['Completion_revision']='2026-10-10 full-interior completion v1'
S['Unseen_reverse_end']='Inferred matching end closure; no verified 180-degree source view.'
S['Cutaway_policy']='Only separate diagnostic cutaway scene may section geometry. All source and interior views use complete unchanged mesh.'
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=False;S.cycles.max_bounces=8;S.cycles.transmission_bounces=6;S.render.threads_mode='FIXED';S.render.threads=2
S.render.resolution_x=1188;S.render.resolution_y=668;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.camera=bpy.data.objects['INSPECT_01_forward_aisle']
# Separate lighting is retained; geometry is never switched for a source view.
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.045,.06,.075,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.08
for im in bpy.data.images:
 if im.has_data and not im.packed_file:im.pack()
# Source-fit camera matrices are immutable relative to the restored source model.
cam_data={o.name:{'location':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens} for o in S.objects if o.type=='CAMERA' and o.name.startswith(('MATCH_','APPROX_'))}
(R/'analysis/source_camera_preservation.json').write_text(json.dumps(cam_data,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'01_train_material.blend'),compress=True)
print('MATERIAL_COMPLETE',changes,flush=True)
