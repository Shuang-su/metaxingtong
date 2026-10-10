import bpy,os,json,math,bmesh
from mathutils import Vector
ROOT='/workspace/scratch/fa58bfcf0425/ktv_fullroom/delivery'
bpy.ops.wm.open_mainfile(filepath=ROOT+'/models/KTV_Complete_Open_Stage.blend');sc=bpy.context.scene
core=[o for o in sc.objects if o.type=='MESH' and not any(c.name=='09_Optional_Moving_Balloon_Dog' for c in o.users_collection)]
bpy.ops.object.select_all(action='DESELECT')
for o in core:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=ROOT+'/models/KTV_Complete_Open_Stage.glb',export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False)
report={'units':'relative Blender units, no measured scale','mesh_count':len(core),'degenerate_faces':[],'nonmanifold_structural':[],'negative_volume_closed_meshes':[],'light_emitters':[]}
for o in core:
 bm=bmesh.new();bm.from_mesh(o.data);degen=sum(f.calc_area()<1e-12 for f in bm.faces)
 if degen:report['degenerate_faces'].append([o.name,degen])
 if o.name.startswith(('INFERRED','Checker_','Visible_blue_rear_band')):
  boundary=sum(not e.is_manifold for e in bm.edges)
  if boundary:report['nonmanifold_structural'].append([o.name,boundary])
 if all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)<-1e-8:report['negative_volume_closed_meshes'].append(o.name)
 bm.free()
for o in sc.objects:
 if o.type=='LIGHT' and o.data.type=='AREA':
  points=[o.matrix_world@Vector((math.cos(i*math.pi/32)*o.data.size/2,math.sin(i*math.pi/32)*o.data.size/2,0)) for i in range(64)]
  report['light_emitters'].append({'name':o.name,'shape':o.data.shape,'diameter':o.data.size,'emitter_z_min':min(p.z for p in points),'emitter_z_max':max(p.z for p in points),'walls_or_roof_present':False,'wall_roof_intersection':False})
# Densely test full polygon deck rays and perimeter/underside seams on continuous solid deck.
deck=bpy.data.objects['INFERRED_continuous_closed_deck'];hits=0;miss=[]
poly=[(-6,-4.5),(6,-4.5),(6,.95),(.82,3.65),(-6,.9)]
def inside(x,y):return all((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0])>=-1e-6 for a,b in zip(poly,poly[1:]+poly[:1]))
for ix in range(121):
 for iy in range(83):
  x=-5.999+ix*11.998/120;y=-4.499+iy*8.148/82
  if inside(x,y):
   h=deck.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),distance=2)[0];hits+=h
   if not h:miss.append([x,y])
seam_hits=0;seam_misses=[]
for a,b in zip(poly,poly[1:]+poly[:1]):
 e=Vector((b[0]-a[0],b[1]-a[1],0));out=Vector((e.y,-e.x,0)).normalized()
 for i in range(101):
  p=Vector((a[0],a[1],-.23))+e*(i+.5)/101
  if deck.ray_cast(p+out*.1,-out,distance=.3)[0]:seam_hits+=1
  else:seam_misses.append(list(p))
report['deck_rays']={'interior_hits':hits,'interior_misses':miss,'edge_hits':seam_hits,'edge_misses':seam_misses,'door_window_apertures':'none evidenced or added','city_facing_opening':'unoccluded; no invented window glass'}
json.dump(report,open(ROOT+'/qa/geometry_audit.json','w'),indent=2)
views=sorted(o.name for o in sc.objects if o.type=='CAMERA' and o.name[:2].isdigit())+['MATCH_A_01h15m29s','MATCH_B_00h35m17s','MATCH_D_01h58m39s_empty']
for n in views:
 sc.camera=bpy.data.objects[n];sc.render.resolution_x=891 if n.startswith('MATCH') else 792;sc.render.resolution_y=501 if n.startswith('MATCH') else 446;sc.render.filepath=ROOT+'/renders/'+n+'.png'
 if n[:2].isdigit() and os.path.exists(sc.render.filepath) and os.path.getmtime(sc.render.filepath)>os.path.getmtime(ROOT+'/models/KTV_Complete_Open_Stage.blend'):continue
 bpy.ops.render.render(write_still=True)
w=bpy.data.materials.new('Neutral_white_clay');w.use_nodes=True;w.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.65,.65,1)
for o in core:
 o.data.materials.clear();o.data.materials.append(w)
 for f in o.data.polygons:f.material_index=0
for o in sc.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1)
for n in ['MATCH_A_01h15m29s','MATCH_B_00h35m17s','MATCH_D_01h58m39s_empty','09_shell','10_underside']:
 sc.camera=bpy.data.objects[n];sc.render.resolution_x=891 if n.startswith('MATCH') else 792;sc.render.resolution_y=501 if n.startswith('MATCH') else 446;sc.render.filepath=ROOT+'/renders/'+n+'_white.png';bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['01_front'];bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/models/KTV_Complete_Open_Stage_White.blend',compress=True)
