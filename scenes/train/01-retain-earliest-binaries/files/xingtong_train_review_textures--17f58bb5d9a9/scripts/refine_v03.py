import bpy,math,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'train_v02.blend'));s=bpy.context.scene
leather=bpy.data.materials['Dark forest green leather | authored UV PBR'];wood=bpy.data.materials['Walnut veneer | authored UV PBR'];metal=bpy.data.materials['Blackened bronze racks and edging'];brass=bpy.data.materials['Aged satin brass details']
for n in leather.node_tree.nodes:
 if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.12

def obj(name,vs,fs,mat,col):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.data.collections[col].objects.link(o);me.materials.append(mat);uv=me.uv_layers.new(name='UVMap')
 for loop in me.loops:
  v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x*2,v.z*2)
 return o
for ob in list(bpy.data.objects):
 if ob.name.startswith('Seat top leather piping'):bpy.data.objects.remove(ob,do_unlink=True)
for side in [-1,1]:
 for i,y in enumerate([-4.5,-2.7,-.9,.9,2.7,4.5]):
  for d in [-1,1]:
   by=y+d*.78;xc=side*.97;vs=[];fs=[];nx=36;nz=33
   for j in range(nz+1):
    z=.58+.765*j/nz
    for k in range(nx+1):
     x=xc-.468+.936*k/nx
     ds=min(((x-(xc+bx))/.075)**2+((z-bz)/.065)**2 for bx in [-.29,0,.29] for bz in [.72,.96,1.20])
     edge=min(1,(k/nx)*12,(1-k/nx)*12,(j/nz)*12,(1-j/nz)*12);puff=.018*(1-math.exp(-ds))*edge
     yy=by-d*(.099+puff)+d*.052*(z-.915);vs.append((x,yy,z))
   for j in range(nz):
    for k in range(nx):a=j*(nx+1)+k;fs.append((a,a+1,a+nx+2,a+nx+1))
   o=obj('Leather subtle tufted face',vs,fs,leather,'03_Booth_seating')
   for p in o.data.polygons:p.use_smooth=True
   for bx in [-.29,0,.29]:
    for bz in [.72,.96,1.20]:
     bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=1,location=(xc+bx,by-d*.105+d*.052*(bz-.915),bz));o=bpy.context.object;o.name='Leather covered tuft button';o.scale=(.008,.004,.008);o.data.materials.append(leather)
     for c in list(o.users_collection):c.objects.unlink(o)
     bpy.data.collections['03_Booth_seating'].objects.link(o)
# Observed end-wall lower cabinet doors. The exact hinges/width are approximate.
for sy in [-1,1]:
 for xx in [-1.03,1.03]:
  for xoff in [-.32,.32]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(xx+xoff,sy*5.46,.59));o=bpy.context.object;o.name='End lower cupboard vertical border';o.dimensions=(.023,.025,.94);o.data.materials.append(wood)
   for c in list(o.users_collection):c.objects.unlink(o)
   bpy.data.collections['07_End_wall_details'].objects.link(o)
  for zz in [.12,1.06]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(xx,sy*5.46,zz));o=bpy.context.object;o.name='End lower cupboard horizontal border';o.dimensions=(.66,.025,.023);o.data.materials.append(wood)
   for c in list(o.users_collection):c.objects.unlink(o)
   bpy.data.collections['07_End_wall_details'].objects.link(o)
  bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.017,location=(xx+.245,sy*5.44,.90));o=bpy.context.object;o.name='End cupboard knob';o.data.materials.append(brass)
  for c in list(o.users_collection):c.objects.unlink(o)
  bpy.data.collections['07_End_wall_details'].objects.link(o)

def camera(name,loc,target,lens):
 if name in bpy.data.objects:o=bpy.data.objects[name]
 else:d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);bpy.data.collections['10_Cameras'].objects.link(o)
 o.data.lens=lens;o.data.sensor_width=36;o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o
camera('MATCH_D_13m59_wide',(.55,-5,1.63),(-.15,1.49,2.60),24)
camera('QA_WIDE_FORWARD_FLOOR',(0,-3.3,1.70),(0,5.2,1.70),18)
# Test C from the table-side opening instead of looking through the nearest back.
camera('MATCH_C_60m16_aisle',(0,2.05,1.66),(0,5.55,1.69),17)
# Door window proportions are visible in the distant wide reference.
for o in bpy.data.objects:
 if o.name.startswith('End door rounded dark window frame'):o.scale.x=.55/.41
 if o.name.startswith('End door rounded glass pane'):o.scale.x=.47/.338
 if o.name.startswith('End door glass divider'):o.scale.x=.485/.35
# Separate approximate night-city context. These are exterior meshes, never projected room pixels.
city=bpy.data.collections.new('11_Exterior_city_approximation');s.collection.children.link(city)
night=bpy.data.materials.new('Exterior charcoal-blue building');night.use_nodes=True;bs=night.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.006,.009,.016,1);bs.inputs['Roughness'].default_value=.9
win=bpy.data.materials.new('Exterior muted office windows');win.use_nodes=True;bs=win.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.09,.105,.12,1);bs.inputs['Emission Color'].default_value=(.15,.17,.18,1);bs.inputs['Emission Strength'].default_value=.45
import random
random.seed(1027)
for side in [-1,1]:
 vs=[];fs=[]
 for j in range(10):
  cy=-18+j*4.1;width=random.uniform(2.1,3.6);top=random.uniform(.7,4.2);bot=-4.0;x=side*13
  o=obj('Night city inferred tower',[(x,cy-width/2,bot),(x,cy+width/2,bot),(x,cy+width/2,top),(x,cy-width/2,top)],[(0,1,2,3)],night,'11_Exterior_city_approximation')
  z=bot+.25
  while z<top-.18:
   yy=cy-width/2+.2
   while yy<cy+width/2-.12:
    if random.random()<.47:
     a=len(vs);vx=x-side*.03;vs.extend([(vx,yy,z),(vx,yy+.13,z),(vx,yy+.13,z+.11),(vx,yy,z+.11)]);fs.append((a,a+1,a+2,a+3))
    yy+=.25
   z+=.31
 obj('Night city inferred illuminated windows',vs,fs,win,'11_Exterior_city_approximation')
# Reduce glass metalness and use transmission so the separate city can actually be seen.
glass=bpy.data.materials['Dark night window glazing'];bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.22,.29,.27,1);bs.inputs['Metallic'].default_value=0;bs.inputs['Transmission Weight'].default_value=.88;bs.inputs['IOR'].default_value=1.45;bs.inputs['Roughness'].default_value=.09

s.cycles.samples=40;s.render.resolution_percentage=65;s.camera=bpy.data.objects['QA_WIDE_FORWARD_FLOOR'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'train_v03.blend'))
for cname in ['QA_WIDE_FORWARD_FLOOR','MATCH_D_13m59_wide','MATCH_C_60m16_aisle','MATCH_B_45m12_left_booth']:
 s.camera=bpy.data.objects[cname];s.render.filepath=str(R/'renders'/f'v03_{cname}.png');bpy.ops.render.render(write_still=True)
print('TRAIN_V03_READY')
