import bpy,bmesh,pathlib,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'models/R03_material.blend'))
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=96
removed=[]
for o in list(bpy.data.objects):
 if o.type=='MESH' and o.name.startswith('WING_') and o.name.endswith('_visible_pale_panel'):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
assert len(removed)==4
# Appearance regions belong to the existing true 3-D membrane, not floating sheets.
im=bpy.data.images.load(str(P/'dependencies/R04-generated-color-regions.png'),check_existing=False);im.name='R04_generated_region_atlas_NOT_source_photo';im.pack()
m=bpy.data.materials.new('R04_membrane_generated_color_regions_NOT_recovered_texture');m.use_nodes=True
p=m.node_tree.nodes['Principled BSDF'];p.inputs['Metallic'].default_value=.4;p.inputs['Roughness'].default_value=.27
t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('WING_') and o.name.endswith('_finite_outer_shell'):
  o.data.materials.clear();o.data.materials.append(m);uv=o.data.uv_layers.new(name='Source_contour_coordinate_color_regions')
  half=len(o.data.vertices)//2
  for loop in o.data.loops:
   v=o.data.vertices[loop.vertex_index%half].co;u=596+1500*v.x/(36+v.y);vv=335.5-1500*(v.z-7)/(36+v.y);uv.data[loop.index].uv=(u/1192,1-vv/671)
  o['appearance']='Generated solid-color inner region atlas from authored visible-outline coordinates; no source pixels; no raised separate inner panel'
# Place the existing visible vein tubes on the nearest visible membrane.
# No extra back supports, hidden frame, invented fasteners or new tube paths.
membranes=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WING_')]
bvhs=[]
for o in membranes:
 o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];tris=[tuple(t.vertices) for t in o.data.loop_triangles];bvhs.append((o.name,BVHTree.FromPolygons(vs,tris,all_triangles=True)))
cam=Vector((0,-36,7));moves=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('VEIN_'):continue
 assert len(o.data.vertices)%10==0
 report={'object':o.name,'rings':len(o.data.vertices)//10,'ray_hits':0,'nearest_fallbacks':0,'unchanged_outside_membrane':0,'max_center_movement':0,'targets':{}}
 for a in range(0,len(o.data.vertices),10):
  verts=[o.data.vertices[i] for i in range(a,a+10)];center=sum((v.co for v in verts),Vector())/10;radius=sum((v.co-center).length for v in verts)/10;direction=(center-cam).normalized();hits=[]
  for name,bvh in bvhs:
   pt,n,ix,dist=bvh.ray_cast(cam,direction)
   if pt is not None:hits.append((dist,pt,name))
  if hits:
   dist,pt,name=min(hits,key=lambda x:x[0]);report['ray_hits']+=1
  else:
   near=[]
   for name,bvh in bvhs:
    pt,n,ix,dist=bvh.find_nearest(center)
    if pt is not None:near.append((dist,pt,name))
   if not near or min(near,key=lambda x:x[0])[0]>.16:
    report['unchanged_outside_membrane']+=1;continue
   dist,pt,name=min(near,key=lambda x:x[0]);report['nearest_fallbacks']+=1
  new=pt-direction*radius*.45;delta=new-center
  # A distant silhouette intersection cannot justify a dramatic depth jump.
  if delta.length>.35:
   report['unchanged_outside_membrane']+=1;continue
  for v in verts:v.co+=delta
  report['max_center_movement']=max(report['max_center_movement'],delta.length);report['targets'][name]=report['targets'].get(name,0)+1
 o.data.update();o['R04_contact']='tube section shifted toward nearest visible membrane, radius45% in front; unhit ends retained and logged; no hidden supports'
 moves.append(report)
# Keep original 05 horizontal camera. Add one explicit alternative diagnostic,
# because source05 floor perspective is not explained by the old horizontal pose.
old=bpy.data.objects['SOURCE05_conditional_close'];d=old.data.copy();o=bpy.data.objects.new('SOURCE05_alternate_tilt_diagnostic',d);bpy.context.collection.objects.link(o)
o.location=(0,-13.6,3.3);o.rotation_euler=(Vector((0,0,1.17))-o.location).to_track_quat('-Z','Y').to_euler();o['status']='ALTERNATE_CAMERA_ONLY_NOT_SOURCE_VERIFIED; shared geometry; original 05 pose retained'
s.camera=bpy.data.objects['SOURCE02_conditional_front'];s['revision']='R04 color-region membrane, contact-seated existing veins; no new hidden support; source FAILED'
qa=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);qa.append({'object':o.name,'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free()
assert all(r['nonmanifold']==0 and r['volume']>0 for r in qa),'Do not render failed shell'
(P/'qa/R04-object-diff-and-contact.json').write_text(json.dumps({'removed':removed,'mesh_count':len(qa),'camera_count':len([o for o in bpy.data.objects if o.type=='CAMERA']),'tube_adjustments':moves,'preflight':qa},indent=2))
def save(tag):
 bpy.ops.wm.save_as_mainfile(filepath=str(P/f'models/R04_{tag}.blend'))
 bpy.ops.export_scene.gltf(filepath=str(P/f'models/R04_{tag}.glb'),export_format='GLB',export_cameras=True,export_lights=True,export_extras=True,export_apply=True)
save('material')
clay=bpy.data.materials['M99_neutral_white_clay']
for o in bpy.data.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(clay)
save('white')
print('R04_FINITE_FROZEN',len(qa),'meshes',len(moves),'adjusted tube objects')
