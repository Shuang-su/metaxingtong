import bpy,bmesh,math,json,random,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'restored/models/Xingtong_Castle_Hall_Textured.blend'));S=bpy.context.scene
C=bpy.data.collections.new('10_Completed_Room_Shell');S.collection.children.link(C)
I=bpy.data.collections.new('11_Inferred_Rear_Entrance_and_Ceiling');S.collection.children.link(I)
A=bpy.data.collections.new('12_Physical_Support_Repairs');S.collection.children.link(A)
stone=bpy.data.materials['RoseStone | original UV PBR'];plaster=bpy.data.materials['Plaster | original UV PBR'];ivory=bpy.data.materials['IvoryMarble | original UV PBR'];dark=bpy.data.materials['DarkMarble | original UV PBR'];gold=bpy.data.materials['AntiqueGold | original UV PBR'];glass=bpy.data.materials['Night blue glazing'];bronze=bpy.data.materials['Dark bronze'];linen=bpy.data.materials['IvoryLinen | original UV PBR']

def mesh(name,vs,fs,mat,col=C,inferred=False):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o)
 if mat:me.materials.append(mat)
 o['evidence']='Inferred unseen completion for a coherent bounded room; not original source geometry.' if inferred else 'Source-observed visible form with inferred structural thickness.'
 uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  ax=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=ax]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.25,v[axes[1]]*.25)
 return o

def box(name,loc,d,ma=plaster,col=C,inferred=False,bevel=0):
 x,y,z=loc;a,b,c=[v/2 for v in d];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 o=mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,col,inferred)
 if bevel:
  m=o.modifiers.new('Physical eased edge','BEVEL');m.width=bevel;m.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 return o

def extrusion(name,poly,y0,y1,ma=plaster,col=C,inferred=False):
 n=len(poly);vs=[(x,y,z) for y in (y0,y1) for x,z in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,ma,col,inferred)

def boolean(o,cut):
 bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cut.data);bm.free()
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Actual through aperture','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)

def rod(name,a,b,r,ma=bronze,col=A):
 w=(Vector(b)-Vector(a)).normalized();u=w.cross(Vector((0,0,1)))
 if u.length<.01:u=w.cross(Vector((0,1,0)))
 u.normalize();v=w.cross(u);n=12
 vs=[tuple(Vector(p)+r*(math.cos(k*math.tau/n)*u+math.sin(k*math.tau/n)*v)) for p in (a,b) for k in range(n)]
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
 return mesh(name,vs,fs,ma,col)

# Remove incomplete structural backings, preserving existing observed ornament, props and camera poses.
remove=['Continuous marble floor substrate','Octagonal polished ivory floor tiles','Dark marble diamond inlay','Rose plaster side wall','End plaster wing','Grand window top spandrel','Central arched blue glass']
for o in list(S.objects):
 if any(o.name.startswith(n) for n in remove):bpy.data.objects.remove(o,do_unlink=True)
# Walls span the original reference-camera locations; dimensions remain nominal, not measured.
front=-12;back=22;H=8.8;wi=7;th=.36
floor=box('ARCH_Floor_slab_complete',(0,(front+back)/2,-.17),(14.72,34.72,.34),ivory)
# Rebuild visible floor inlays as shallow, closed solids clipped at finished wall planes.
def clip(poly,axis,val,greater):
 out=[]
 for i,p in enumerate(poly):
  q=poly[(i+1)%len(poly)];a=(p[axis]>=val) if greater else (p[axis]<=val);b=(q[axis]>=val) if greater else (q[axis]<=val)
  if a:out.append(p)
  if a!=b:
   t=(val-p[axis])/(q[axis]-p[axis]);out.append(tuple(p[j]+t*(q[j]-p[j]) for j in (0,1)))
 return out
vs=[];fs=[];vd=[];fd=[];pitch=.84;cut=.185;half=pitch/2-.002
for i in range(-9,10):
 for j in range(-15,28):
  for diamond,verts,faces in [(False,vs,fs),(True,vd,fd)]:
   points=[(-half+cut,-half),(half-cut,-half),(half,-half+cut),(half,half-cut),(half-cut,half),(-half+cut,half),(-half,half-cut),(-half,-half+cut)] if not diamond else [(-cut+.004,0),(0,-cut+.004),(cut-.004,0),(0,cut-.004)]
   x=i*pitch+(pitch/2 if diamond else 0);y=j*pitch+(pitch/2 if diamond else 0);poly=[(x+a,y+b) for a,b in points]
   for ax,val,g in [(0,-7,True),(0,7,False),(1,front,True),(1,back,False)]:
    if poly:poly=clip(poly,ax,val,g)
   if len(poly)<3:continue
   n=len(poly);off=len(verts);verts.extend([(a,b,z) for z in (-.016,.004 if diamond else .003) for a,b in poly]);faces.extend([tuple(off+k for k in range(n-1,-1,-1)),tuple(off+n+k for k in range(n))]);faces.extend([(off+k,off+(k+1)%n,off+(k+1)%n+n,off+k+n) for k in range(n)])
mesh('Octagonal ivory finish | clipped solid tiles',vs,fs,ivory);mesh('Dark marble diamond inlay | solid',vd,fd,dark)
# Side wall volumes, with real through-window openings and exposed returns.
for side in (-1,1):
 wall=box(f'ARCH_Side_wall_{side}_with_apertures',(side*(7+th/2),5,H/2),(th,34,H),plaster)
 for y in (-1,5,11,17):
  cut=box('TEMP_APERTURE',(side*7.18,y,4.1),(1.2,3.15,6.6),None);boolean(wall,cut)
  # Existing blue panels sit inside each aperture, retain source-visible face but now possess actual depth.
  box(f'Window_{side}_{y}_sill_return',(side*7.18,y,.76),(.43,3.25,.10),stone)
  box(f'Window_{side}_{y}_head_return',(side*7.18,y,7.43),(.43,3.25,.08),stone)
  for yy in (y-1.61,y+1.61):box(f'Window_{side}_{y}_jamb_return',(side*7.18,yy,4.1),(.43,.08,6.6),stone)
 # Continue moulding into unseen vestibule and to roof junction, explicitly inferred extents.
 for z,dep,height in [(.2,.14,.4),(8.10,.26,.24),(8.30,.35,.35)]:box('INF_side_moulding_continuation',(side*(7-dep/2),-8.5,z),(dep,7,height),stone,I,True)
 box('INF_side_ceiling_cornice',(side*6.83,5,8.60),(.38,34,.40),stone,I,True)
# Complete the far wall with an accurate arched aperture; straight wall segments remain outside the opening.
end=box('ARCH_Far_wall_arched_aperture',(0,22.18,H/2),(14.72,.36,H),plaster)
rad=3.075;spring=5.20
poly=[(-rad,-.1),(rad,-.1),(rad,spring)]+[(rad*math.cos(k*math.pi/64),spring+rad*math.sin(k*math.pi/64)) for k in range(1,65)]
cut=extrusion('TEMP_ARCH',poly,21.5,22.7,None);boolean(end,cut)
polyglass=[(-rad,0),(rad,0),(rad,spring)]+[(rad*math.cos(k*math.pi/64),spring+rad*math.sin(k*math.pi/64)) for k in range(1,65)]
extrusion('ARCH_Central_arched_glazing_40mm',polyglass,22.0,22.04,glass)
# Full-depth jamb and arch reveal trim, neutral external finish, no invented exterior environment.
for x in (-3.09,3.09):box('Grand_window_stone_jamb_return',(x,22.15,spring/2),(.08,.42,spring),stone)
vs=[];fs=[]
for y in (21.94,22.38):
 for rr in (rad,rad+.12):
  vs.extend([(rr*math.cos(k*math.pi/64),y,spring+rr*math.sin(k*math.pi/64)) for k in range(65)])
for k in range(64):
 fs.extend([(k,k+1,65+k+1,65+k),(130+k,195+k,195+k+1,130+k+1),(k,130+k,130+k+1,k+1),(65+k,65+k+1,195+k+1,195+k)])
fs.extend([(0,65,195,130),(64,194,259,129)]);mesh('Grand_window_full_depth_arch_reveal',vs,fs,stone)
box('Far_wall_ceiling_junction',(0,21.86,8.58),(14,.28,.44),stone)
# Inferred ceiling, simply coffered in the existing muted palette; no chandelier or unsupported source claims.
box('INF_Complete_ceiling_slab',(0,5,8.99),(14.72,34.72,.38),plaster,I,True)
for x in (-4.25,4.25):box('INF_Column_row_entablature',(x,8.5,8.48),(1.62,27.2,.68),stone,I,True)
for y in (-9,-3,3,9,15,21):
 box('INF_Ceiling_cross_beam',(0,y,8.68),(14,.20,.24),stone,I,True)
 for x in (-2.1,2.1):
  start=max(-11.9,y-5.8);stop=min(21.9,y-.1);box('INF_Ceiling_panel_bead',(x,(start+stop)/2,8.74),(.06,stop-start,.12),ivory,I,True)
# Inferred rear wall and closed double entrance. Real doorway returns; no claim about its destination.
rear=box('INF_Rear_wall_with_doorway',(0,-12.18,H/2),(14.72,.36,H),plaster,I,True)
boolean(rear,box('TEMP_DOOR',(0,-12.18,1.69),(2.8,1,3.42),None))
for x in (-1.45,1.45):box('INF_Entrance_jamb',(x,-12.13,1.73),(.14,.49,3.46),stone,I,True,bevel=.012)
box('INF_Entrance_lintel',(0,-12.13,3.48),(3.05,.49,.17),stone,I,True,bevel=.012)
for side in (-1,1):
 door=box(f'INF_Closed_door_leaf_{side}',(side*.70,-12.14,1.69),(1.40,.10,3.38),ivory,I,True,bevel=.01)
 door['connection']='Destination unknown; garden relation is unconfirmed.'
 for z,h in [(1.0,1.45),(2.55,1.0)]:box('INF_Door_recessed_panel',(side*.70,-12.07,z),(1.08,.06,h),stone,I,True,bevel=.025)
 rod('INF_Door_handle',(side*.15,-11.98,1.45),(side*.15,-11.98,1.72),.018,gold,I)
 for x in (side*3.8,side*6):
  box('INF_Rear_wall_panel_reveal',(x,-11.985,4.4),(1.35,.055,6.9),stone,I,True)
box('INF_Rear_ceiling_cornice',(0,-11.84,8.58),(14,.35,.44),stone,I,True)
box('INF_Entrance_threshold',(0,-12.17,.016),(2.9,.5,.035),stone,I,True)
for side in (-1,1):box('INF_Rear_skirting',(side*4.3,-11.94,.20),(5.55,.12,.4),stone,I,True)
box('INF_Entrance_head_stop',(0,-12.17,3.393),(2.82,.22,.05),stone,I,True)
# Put side glazing into the wall thickness; thickness is repaired without opaque walls behind it.
for o in S.objects:
 if o.type=='MESH' and o.name.startswith('Side recessed night panel'):
  xs=[v.co.x for v in o.data.vertices];c=(min(xs)+max(xs))/2;s=1 if c>0 else -1
  for v in o.data.vertices:v.co.x+=s*.04
# Actual supports on floor. Existing thin table legs stopped 35 mm above the floor.
for o in list(S.objects):
 if o.type=='MESH' and 'slender brass leg' in o.name:
  low=min(v.co.z for v in o.data.vertices)
  for v in o.data.vertices:
   if abs(v.co.z-low)<1e-5:v.co.z=.005
# Replace unfinished hanging ribbon tubes with tethers reaching a stable weighted table anchor.
for o in list(S.objects):
 if o.type=='MESH' and o.name.startswith('Balloon hanging ribbon'):bpy.data.objects.remove(o,do_unlink=True)
knots=[o for o in S.objects if o.type=='MESH' and o.name.startswith('Balloon knot')]
for idx,o in enumerate(knots):
 coords=[o.matrix_world@v.co for v in o.data.vertices];c=sum(coords,Vector())/len(coords);c.z=min(v.z for v in coords)
 # Anchor on the nearest banquet tabletop, not arbitrarily floating in space.
 tops=[t for t in S.objects if t.type=='MESH' and 'wooden top' in t.name]
 def center(t):return sum([t.matrix_world@v.co for v in t.data.vertices],Vector())/len(t.data.vertices)
 t=min(tops,key=lambda t:(center(t)-c).length);tc=center(t);a=(tc.x,tc.y,1.055)
 rod('Balloon tether completed '+str(idx),a,c,.0022,gold)
 box('Balloon anchor weight '+str(idx),(tc.x,tc.y,1.04),(.045,.045,.025),gold,A,False,bevel=.004)
# Repair all inherited open ornaments. Floor/glass were rebuilt; thin acanthus leaves acquire thickness,
# pipe ends acquire caps. No camera-dependent object transforms, visibility drivers or backdrop photos.
repairs=[]
for o in list(S.objects):
 if o.type!='MESH':continue
 bpy.context.view_layer.objects.active=o
 for m in list(o.modifiers):
  try:bpy.ops.object.modifier_apply(modifier=m.name)
  except:pass
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);boundary=[e for e in bm.edges if e.is_boundary]
 if boundary and o.name.startswith('Capital folded leaf'):
  bm.to_mesh(o.data);bm.free();m=o.modifiers.new('Physical acanthus leaf thickness','SOLIDIFY');m.thickness=.012;m.offset=0;bpy.ops.object.modifier_apply(modifier=m.name);bm=bmesh.new();bm.from_mesh(o.data);repairs.append(o.name)
 elif boundary:
  bmesh.ops.holes_fill(bm,edges=boundary,sides=0);repairs.append(o.name)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
 if not o.data.uv_layers:
  uv=o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   for li in p.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.25,v.y*.25)
 o.hide_render=False;o.hide_viewport=False
# Neutral soft architectural light in the inferred vestibule; light itself is not modeled structure.
def area(name,loc,target,energy,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area('INF_Vestibule ambient', (0,-8.5,8.35),(0,-8.5,0),320,6,(1,.78,.61))
# Inspection cameras are all genuine independent poses in a single unchanged completed room.
def camera(name,loc,target,lens=22):
 d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.05;d.clip_end=200;d.sensor_width=36;o=bpy.data.objects.new(name,d);bpy.data.collections['09_Cameras'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o
camera('MATCH_C_73m44_arch_crosscheck',(-.28,-6.9,1.46),(.2,21.9,2.7),32)
camera('QA_ENTRY_COMPLETE',(0,-10.7,2.0),(0,12,3.0),19)
camera('QA_REVERSE_COMPLETE',(1.4,19.7,2.0),(0,-12,2.8),19)
camera('QA_SIDE_COMPLETE',(-6.5,7.2,2.0),(6.8,10.5,2.6),18)
camera('QA_CEILING_COMPLETE',(0,6,1.8),(0,8,8.8),15)
camera('QA_EXTERIOR_COMPLETE',(31,-40,28),(0,5,3.6),37)
camera('QA_CUTAWAY_COMPLETE',(25,-34,26),(0,5,2.3),37)
for im in bpy.data.images:
 if im.source=='FILE':
  p=R/'restored/textures'/os.path.basename(im.filepath)
  if p.exists():
   if im.packed_file:im.unpack(method='REMOVE')
   im.filepath=str(p);im.reload();im.pack()
  elif not im.packed_file:raise RuntimeError('Missing unpacked texture: '+im.filepath)
  im.filepath='//../textures/'+os.path.basename(im.filepath)
S['Evidence']='Approximate reconstructed hall from real stream frames 00:45:15, 01:13:44, 01:15:07. A/C are broadly front-facing; B adds a small oblique change. Not three independently calibrated baselines.'
S['Inferred']='Rear closure at Y=-12, rear doorway and destination, ceiling, structural thickness, unseen wall extensions are explicitly inferred. No confirmed link to garden.'
S['Excluded']='Characters, player UI, garden geometry, literal source screenshot textures. Exterior beyond wall envelope unknown.'
S['GeometryCompletion']='Bounded 14 x 34 x 8.8 m nominal interior, continuous solid floor/wall/roof, physical window and entry apertures with returns. All camera-independent.'
S['Scale']='Nominal metres inferred; dimensions are not surveyed.'
S['Reconstruction']='Full-room structural continuation of previous source-visible Castle Hall asset.'
S.render.engine='CYCLES';S.cycles.samples=40;S.cycles.use_denoising=False;S.cycles.max_bounces=6;S.cycles.diffuse_bounces=4;S.render.resolution_x=1188;S.render.resolution_y=668;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=4;S.render.image_settings.file_format='PNG';S.camera=bpy.data.objects['QA_ENTRY_COMPLETE']
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.10,.16,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.15
S['repair_count']=len(repairs)
# Pack all assets; explicit text notes travel with the editable Blender file.
n=bpy.data.texts.new('READ_ME_Complete_Room_and_Uncertainty.txt');n.write('CASTLE HALL complete-room reconstruction, 2026-10-10.\nSource: https://www.bilibili.com/video/BV1aw411T7ws/\n'+S['Evidence']+'\n'+S['Inferred']+'\n'+S['GeometryCompletion']+'\nSource fit is approximate and remains uncalibrated. Geometry completion is not proof of original hidden layout.\nAll mesh objects remain visible from every camera. Diagnostic cutaway is generated separately by physically slicing a disposable copy.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Xingtong_Castle_Hall_FullRoom.blend'),compress=True)
json.dump({'repaired_open_meshes':repairs,'interior_bounds':[[-7,-12,0],[7,22,8.8]],'inferred':S['Inferred']},open(R/'qa/completion_changes.json','w'),indent=2)
print('FULLROOM_BUILD_DONE',len([o for o in S.objects if o.type=='MESH']),flush=True)
