"""R09 shared environment candidate; load R08. No camera or piano changes.
Run: blender -b -t 8 --python scripts/build_environment_r09.py
Authored material maps are not source images. All sizes use inferred model units.
"""
import bpy,bmesh,math,json,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];T=R/'textures/r09';Q=R/'qa/r09';O=R/'models/r09'
for p in (Q,O):p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'models/r08/piano_seaside_material.blend'));sc=bpy.context.scene
MUTABLE={'D01_deck','S01_sand','E01_water','L01_lantern','L02_lantern'}
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def geo(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=array.array('f',[0])*len(me.vertices)*3;ix=array.array('i',[0])*len(me.loops);me.vertices.foreach_get('co',v);me.loops.foreach_get('vertex_index',ix)
 d={'v':hashlib.sha256(v.tobytes()).hexdigest(),'ix':hashlib.sha256(ix.tobytes()).hexdigest(),'faces':[(p.loop_start,p.loop_total,p.use_smooth) for p in me.polygons],'matrix':[list(v) for v in o.matrix_world]};ev.to_mesh_clear();return digest(d)
def cam(o):return {'matrix':[list(v) for v in o.matrix_world],'lens':o.data.lens,'shift':[o.data.shift_x,o.data.shift_y],'clip':[o.data.clip_start,o.data.clip_end],'sensor':[o.data.sensor_width,o.data.sensor_height],'type':o.data.type}
def matfinger(m):
 return digest({'diffuse':list(m.diffuse_color),'nodes':[{'name':n.name,'type':n.bl_idname,'inputs':{s.identifier:([*s.default_value] if hasattr(s.default_value,'__len__') and not isinstance(s.default_value,str) else s.default_value) for s in n.inputs if hasattr(s,'default_value')},'image':n.image.name if hasattr(n,'image') and n.image else None} for n in m.node_tree.nodes] if m.node_tree else [],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.node_tree else []})
# Name exclusions are explicit: old sand/water IDs were inspected rather than assumed.
mutable_names={o.name for o in sc.objects if o.type=='MESH' and (o.get('evidence_id') in MUTABLE or o.name in ['S01 local sand patch','E01 water environment'])}
frozen={o.name:{'geometry':geo(o),'materials':[(m.name,matfinger(m)) for m in o.data.materials if m]} for o in sc.objects if o.type=='MESH' and o.name not in mutable_names}
cameras={o.name:cam(o) for o in sc.objects if o.type=='CAMERA'}
deck_geo={o.name:geo(o) for o in sc.objects if o.get('evidence_id')=='D01_deck'}
def image(name,noncolor=False):
 im=bpy.data.images.load(str(T/name),check_existing=True)
 if noncolor:im.colorspace_settings.name='Non-Color'
 return im
def mat(name,color,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m

def maps(m,color=None,rough=None,normal=None,emission=None,strength=.4):
 n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF')
 for filename,socket,noncolor in [(color,'Base Color',False),(rough,'Roughness',True),(emission,'Emission Color',False)]:
  if filename:
   t=n.new('ShaderNodeTexImage');t.image=image(filename,noncolor);l.new(t.outputs['Color'],b.inputs[socket])
 if normal:
  t=n.new('ShaderNodeTexImage');t.image=image(normal,True);nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=strength;l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],b.inputs['Normal'])
 return m
wood=maps(mat('R09 weathered deck - common UV atlas',(.20,.17,.14),.8),'deck_weathered_color.png','deck_weathered_roughness.png','deck_weathered_normal.png',strength=.65)
sand=maps(mat('R09 finite dry to wet shore',(.20,.15,.10),.85),'shore_color.png','shore_roughness.png','shore_normal.png',strength=.8)
water=maps(mat('R09 common ocean dielectric',(.045,.065,.085),.14,.0),normal='water_ripple_normal.png',strength=.45);water.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.333
paper=maps(mat('R09 warm paper bag - emission approximates translucency',(.91,.5,.16),.85),'paper_color.png',normal='paper_normal.png',emission='paper_emission.png',strength=.15);paper.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=1.65
base=mat('R09 thin paper lantern base',(.035,.019,.012),.8)
wick=mat('R09 inferred lantern light source',(1,.48,.13),.9);wick.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.48,.13,1);wick.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=8

def tag(o,id):o['evidence_id']=id;o['camera_independent']=True;o['evidence_status']='source object class observed; shape, thickness and dimensions inferred';return o

def mesh(name,vs,fs,ma,id):
 me=bpy.data.meshes.new(name+' mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);sc.collection.objects.link(o);tag(o,id)
 if ma:me.materials.append(ma)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();return o

def uv_project(o,fn):
 uv=o.data.uv_layers.get('UVMap') or o.data.uv_layers.new(name='UVMap')
 for p in o.data.polygons:
  for li in p.loop_indices:uv.data[li].uv=fn(o.data.vertices[o.data.loops[li].vertex_index].co,p.normal)

def cube(name,loc,dims,ma,id):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);tag(o,id);return o
# Deck mesh and supports do not move. Longitudinal UV is X; 8 authored strips alternate.
for o in list(sc.objects):
 if o.get('evidence_id')!='D01_deck':continue
 o.data.materials.clear();o.data.materials.append(wood)
 if 'plank' in o.name:
  i=int(o.name.rsplit(' ',1)[-1]);band=i%8
  uv_project(o,lambda v,n,i=i,band=band:((v.x/7.4+.5) if i%2==0 else .5-v.x/7.4,(band+(.045+.91*(v.y/.244+.5)))/8))
 else:uv_project(o,lambda v,n:(v.x/7.4+.5,(v.y/.14+.5)/8))
# Replace the two existing lanterns; positions/identity count remain unchanged.
lamps=[]
for id,anchor,size in [('L01_lantern',(-.92,1.22,0),.25),('L02_lantern',(7.2,-5.5,-.08),.27)]:
 old=[o.name for o in sc.objects if o.type=='MESH' and o.get('evidence_id')==id]
 for name in old:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 x,y,z=anchor;w=size;d=size*.84;h=size*1.55;t=.0032;z0=z+.014
 # The perimeter's side midpoints make a shallow bag fold, not a metal frame.
 poly=[(-w/2,-d/2),(w/2,-d/2),(w/2-.008,0),(w/2,d/2),(-w/2,d/2),(-w/2+.008,0)];N=len(poly)
 inner=[(px-math.copysign(t,px),py-math.copysign(t,py) if py else 0) for px,py in poly]
 vs=[]
 for ring,zz in [(poly,z0),(poly,z0+h),(inner,z0+h),(inner,z0+t)]:
  for j,(px,py) in enumerate(ring):vs.append((x+px,y+py,zz+(.003*math.sin(j*2.3) if zz==z0+h else 0)))
 fs=[]
 for i in range(N):
  j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(N+i,N+j,2*N+j,2*N+i),(2*N+i,2*N+j,3*N+j,3*N+i)])
 fs.extend([tuple(range(N-1,-1,-1)),tuple(range(3*N,4*N))]);o=mesh(id+' open thin paper shell',vs,fs,paper,id)
 # Two five-point apertures through observed-style front panel; unseen rear is plain.
 for panel in [-1]:
  for k,(cx,cz,r) in enumerate([(-w*.16,z0+h*.74,w*.13),(w*.19,z0+h*.22,w*.082)]):
   star=[(x+cx+(r if i%2==0 else r*.43)*math.cos(math.pi/2+i*math.pi/5),cz+(r if i%2==0 else r*.43)*math.sin(math.pi/2+i*math.pi/5)) for i in range(10)]
   yy=y+panel*d/2;vv=[(xx,dep,zz) for dep in [yy-.015,yy+.015] for xx,zz in star];ff=[tuple(range(9,-1,-1)),tuple(range(10,20))]+[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]
   c=mesh('temporary star aperture',vv,ff,None,'construction');bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Real star aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)
 inner_paper=mat(id+' inferred lit interior paper',(1,.55,.18),.9)
 inner_paper.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.55,.18,1);inner_paper.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=3.8;o.data.materials.append(inner_paper)
 for f in o.data.polygons:
  if (f.center.x-x)*f.normal.x+(f.center.y-y)*f.normal.y < -.02 and abs(f.normal.z)<.5:f.material_index=1
 uv_project(o,lambda v,n:((v.x-x)/w+.5,(v.z-z0)/h) if abs(n.y)>.3 else ((v.y-y)/d+.5,(v.z-z0)/h))
 cube(id+' thin base',(x,y,z+.007),(w*1.06,d*1.06,.014),base,id)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=w*.095,location=(x,y,z0+h*.45));bulb=bpy.context.object;bulb.name=id+' inferred internal emitter';tag(bulb,id);bulb.data.materials.append(wick)
 lights=[a for a in sc.objects if a.type=='LIGHT' and a.data.type=='POINT' and abs(a.location.x-x)<.01 and abs(a.location.y-y)<.01]
 assert len(lights)==1,(id,len(lights))
 l=lights[0];l.location.z=z0+h*.46;l.data.energy=12*size/.25;l.data.color=(1,.44,.12);l.data.shadow_soft_size=w*.12;l['evidence_id']=id
 lamps.append({'id':id,'anchor':anchor,'size_inferred':size,'height_inferred':h,'thickness_inferred':t,'removed_generic_components':old,'new_components':[o.name,id+' thin base',bulb.name],'visible_class':'open paper bag with star apertures','inferred':'plain unseen rear panel; exact dimensions; lit interior paper approximation; internal emitter; cross-frame instance identity'})
# Replace hard rectangular shore by a limited closed topographic transition.
old=bpy.data.objects['S01 local sand patch'];oldid=old.get('evidence_id');bpy.data.objects.remove(old,do_unlink=True)
def shore_z(x,y):
 shore=8.55+.18*math.sin(y*.67)+.08*math.sin(y*1.9)
 left=max(0,min(1,(x-2.5)/1.18));left=left*left*(3-2*left)
 wet=max(0,min(1,(x-7.35)/(shore-7.35)));wet=wet*wet*(3-2*wet)
 end=max(0,min(1,(abs(y)-8.3)/3.7));end=end*end*(3-2*end)
 return -.08-.50*(1-left)-.48*wet-.45*end

def closed_grid(name,xs,ys,zfun,zbottom,ma,id):
 nx=len(xs);ny=len(ys);vs=[(x,y,zfun(x,y)) for y in ys for x in xs];fs=[]
 for j in range(ny-1):
  for i in range(nx-1):a=j*nx+i;fs.append((a,a+1,a+nx+1,a+nx))
 perimeter=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+[(ny-1)*nx+i for i in range(nx-2,-1,-1)]+[j*nx for j in range(ny-2,0,-1)]
 bottom=[]
 for i in perimeter:bottom.append(len(vs));vs.append((vs[i][0],vs[i][1],zbottom))
 center=len(vs);vs.append(((xs[0]+xs[-1])/2,(ys[0]+ys[-1])/2,zbottom))
 for k in range(len(perimeter)):
  j=(k+1)%len(perimeter);fs.append((perimeter[k],bottom[k],bottom[j],perimeter[j]));fs.append((bottom[j],bottom[k],center))
 o=mesh(name,vs,fs,ma,id)
 for p in o.data.polygons:
  if p.index<(nx-1)*(ny-1):p.use_smooth=True
 return o
shore=closed_grid('S01 local sand patch',[2.5+7.1*i/128 for i in range(129)],[-12+24*j/160 for j in range(161)],shore_z,-1.4,sand,oldid)
uv_project(shore,lambda v,n:((v.x-2.5)/7.1,(v.y+12)/24))
shore['evidence_status']='finite shoreline transition inferred; visible sand class observed; full footprint/continuation unknown'
# One continuous water surface, dense near scene, no view-dependent tessellation.
old=bpy.data.objects['E01 water environment'];oldid=old.get('evidence_id');bpy.data.objects.remove(old,do_unlink=True)
xs=[-500,-320,-160,-80,-40]+[-24+.25*i for i in range(193)]+[40,80,160,320,500]
def wave(x,y):
 f=max(0,min(1,(24-max(abs(x),abs(y)))/6));f=f*f*(3-2*f)
 return -.42+f*(.002*math.sin(y*3.9+x*.35)+.001*math.sin(y*8.3-x*.7))
sea=closed_grid('E01 water environment',xs,xs,wave,-1.8,water,oldid);uv_project(sea,lambda v,n:(v.x*.28,v.y*.28));sea['evidence_status']='shared near-surface waves inferred; finite render extent, no real sea boundary claimed'
# HDR worlds are environment state sidecars; never part of finite physical room geometry.
def world(state):
 w=bpy.data.worlds.new('R09 '+state+' global environment');w.use_nodes=True;n=w.node_tree.nodes;l=w.node_tree.links;n.clear();e=n.new('ShaderNodeTexEnvironment');e.image=image(state+'.hdr');e.interpolation='Linear';bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.55;l.new(e.outputs['Color'],bg.inputs['Color']);out=n.new('ShaderNodeOutputWorld');l.new(bg.outputs[0],out.inputs[0]);w['state']=state;w['status']='authored approximate lighting, not measured environment';return w
w40=world('S40_sunset');w105=world('S105_bluehour');w105.use_fake_user=True;sc.world=w40
for o in sc.objects:
 if o.type=='LIGHT' and o.data.type=='AREA':
  # Shared area lights are an approximation, not tuned per camera.
  if o.location.y<0:o.data.energy=500;o.data.color=(1,.66,.42)
  else:o.data.energy=650;o.data.color=(.42,.54,1)
sc['source_state']='S40_sunset globally active. S105_bluehour is an explicit alternate world; never camera-linked.'
sc['stage']='r09 local environment candidate; R08 piano and all cameras frozen'
sc.eevee.taa_render_samples=32
if hasattr(sc.eevee,'use_raytracing'):sc.eevee.use_raytracing=True
sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.camera=bpy.data.objects['main']
bpy.context.view_layer.update()
after={name:{'geometry':geo(bpy.data.objects[name]),'materials':[(m.name,matfinger(m)) for m in bpy.data.objects[name].data.materials if m]} for name in frozen}
assert frozen==after,'frozen object changed'
assert cameras=={o.name:cam(o) for o in sc.objects if o.type=='CAMERA'},'camera changed'
assert deck_geo=={o.name:geo(o) for o in sc.objects if o.get('evidence_id')=='D01_deck'},'deck geometry changed'
manifest={'stage':'r09','base':'models/r08/piano_seaside_material.blend','base_commit':'5a249baa21242e3d50c9be6bb9d24c4de8895285','frozen_object_count':len(frozen),'frozen_geometry_and_assigned_materials_identical':True,'frozen_hash_before':digest(frozen),'frozen_hash_after':digest(after),'cameras_identical':True,'all_cameras':cameras,'deck_geometry_identical':True,'lanterns':lamps,'world_states':{'default':'S40_sunset','alternate':'S105_bluehour','geometry_identical':True,'camera_binding':'none','source_evidence':'40min pink sunset versus 105min cooler blue state; exact physical values and transition unknown'},'shore_extent':{'x':[2.5,9.6],'y':[-12,12],'status':'inferred finite working patch; boundary submerged; no bar connection established'},'water':'single shared wave surface and ripple normal map; authored HDR cloud reflections','export_limitation':'GLB does not contain Blender world. Supply HDR sidecars and state separately. Reimport comparison explicitly retains saved world/lights.'}
(Q/'environment-invariants.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Pack maps for editable self-contained BLEND; sidecars stay available as ordinary files.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'piano_seaside_material.blend'))
bpy.ops.export_scene.gltf(filepath=str(O/'piano_seaside_material.glb'),export_format='GLB',export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
white=mat('R09 neutral geometry diagnostic',(.72,.72,.72),.68)
for o in sc.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(white)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'piano_seaside_white.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'piano_seaside_white.glb'),export_format='GLB',export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
print('R09_ENVIRONMENT_BUILT',len([o for o in sc.objects if o.type=='MESH']))
