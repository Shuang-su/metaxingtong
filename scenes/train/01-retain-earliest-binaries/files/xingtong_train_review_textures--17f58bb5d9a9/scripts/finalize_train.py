import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'deliverables';O.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'train_v03.blend'));s=bpy.context.scene
# Lower every back equally; retain human-scale seat bases and table heights.
f=(1.28-.55)/(1.425-.55)
for o in bpy.data.objects:
 if ' high back' in o.name or o.name.startswith(('Seat edge leather piping','Leather covered tuft button')):
  o.location.z=.55+(o.location.z-.55)*f;o.scale.z*=f
 elif o.name.startswith('Leather subtle tufted face'):
  for v in o.data.vertices:v.co.z=.55+(v.co.z-.55)*f
# Fixture pitch is independent of the denser window/seat pitch.
old=[-4.5,-2.7,-.9,.9,2.7,4.5];new={-4.5:-5.4,-2.7:-2.7,.9:0,4.5:2.7}
for o in list(bpy.data.objects):
 if o.name.startswith(('Central round ceiling','Central rectangular ceiling','Vent grille','Vent louvre','Central ceiling side fluorescent','Ceiling diffuse pool','Indirect ceiling upward')):
  cy=min(old,key=lambda a:abs(o.location.y-a))
  if cy not in new:bpy.data.objects.remove(o,do_unlink=True)
  else:o.location.y+=new[cy]-cy
# Door glass upper two short vertical mullions and the second horizontal bar.
metal=bpy.data.materials['Blackened bronze racks and edging']
for sy in [-1,1]:
 y=sy*(5.55-.123)
 for x in [-.145,.145]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,1.975));o=bpy.context.object;o.name='Door glass upper short vertical mullion';o.dimensions=(.013,.018,.175);o.data.materials.append(metal)
  for c in list(o.users_collection):c.objects.unlink(o)
  bpy.data.collections['07_End_wall_details'].objects.link(o)
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,y,1.815));o=bpy.context.object;o.name='Door glass second horizontal mullion';o.dimensions=(.48,.018,.02);o.data.materials.append(metal)
 for c in list(o.users_collection):c.objects.unlink(o)
 bpy.data.collections['07_End_wall_details'].objects.link(o)
# Reproduce only the now-verified sign sentence; no invented tiny notice text.
for o in list(bpy.data.objects):
 if o.name.startswith('Illegible sign marker'):bpy.data.objects.remove(o,do_unlink=True)
m=bpy.data.materials.new('Verified SHENYUE destination text | image UV');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'textures/destination_sign_basecolor.png'));t.image.pack();l.new(t.outputs['Color'],b.inputs['Base Color']);l.new(t.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=.5;b.inputs['Roughness'].default_value=.4
for sy in [-1,1]:
 y=sy*(5.55-.13);verts=[(-.41,y,2.432),(.41,y,2.432),(.41,y,2.518),(-.41,y,2.518)];me=bpy.data.meshes.new('Sign UV panel');me.from_pydata(verts,[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('Verified destination sign face',me);bpy.data.collections['07_End_wall_details'].objects.link(o);me.materials.append(m);uv=me.uv_layers.new(name='UVMap')
 for j,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[j].uv=p if sy>0 else (1-p[0],p[1])

def camera(name,loc,target,lens):
 o=bpy.data.objects[name];o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;return o
camera('MATCH_A_15m19_right_booth',(.89,-4.82,1.18),(.89,1.67,1.56),24)
camera('MATCH_B_45m12_left_booth',(-.86,-5,1.495),(-1.92,1.49,1.575),24)
camera('MATCH_D_13m59_wide',(.55,-5,1.485),(-.15,1.49,2.455),24)
bpy.data.objects['MATCH_C_60m16_aisle'].name='APPROX_C_60m16_aisle_unresolved'
# Every mesh has a real UV layer; material/white objects retain exact geometry.
for o in bpy.data.objects:
 if o.type=='MESH' and not o.data.uv_layers:
  uv=o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   a=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=a]
   for li in p.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
def interior(o):return o.type=='MESH' and not any(c.name.startswith('11_') for c in o.users_collection)
def audit():
 h=hashlib.sha256();ob=[o for o in bpy.data.objects if interior(o)];lo=[float('inf')]*3;hi=[-float('inf')]*3
 for o in sorted(ob,key=lambda a:a.name):
  h.update(o.name.encode());h.update(str(tuple(tuple(float(v) for v in row) for row in o.matrix_world)).encode())
  for v in o.data.vertices:
   h.update(str(tuple(float(a) for a in v.co)).encode());p=o.matrix_world@v.co
   for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
  for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return {'geometry_sha256':h.hexdigest(),'interior_mesh_objects':len(ob),'base_vertices':sum(len(o.data.vertices) for o in ob),'base_polygons':sum(len(o.data.polygons) for o in ob),'UV_mesh_objects':sum(bool(o.data.uv_layers) for o in ob),'world_bounds':[lo,hi]}
s.render.resolution_x=1200;s.render.resolution_y=675;s.render.resolution_percentage=100;s.cycles.samples=96;s.cycles.use_denoising=False;s.cycles.max_bounces=8;s.cycles.transmission_bounces=6
s['Nominal_dimensions']='3.0m width x 11.1m length x 2.6m ceiling. Seat back 1.28m. All inferred.';s['Module_count_evidence']='At least 5 windows/modules identifiable; 6 used as explicit inference.';s['Reference_alignment']='Approximate pinhole camera matches A/B/D; no warps, no camera-specific furniture movement.';s['Sign_source']='11:51 THE NEXT STOP IS SHENYUE STATION; static verified wording.'
text=bpy.data.texts.new('README_中文');text.write((R/'README_中文.txt').read_text());s.camera=bpy.data.objects['QA_WIDE_FORWARD_FLOOR']
meta=audit();meta['PBR_image_maps']=18;meta['sign_image_maps']=1;meta['packed_image_count']=sum(bool(im.packed_file) for im in bpy.data.images);meta['source_video']='https://www.bilibili.com/video/BV1fMP4ziEUd/';meta['render_size']=[1200,675]
# Project a small set of visible structural landmarks in D; source values are manually read low-resolution anchors.
cam=bpy.data.objects['MATCH_D_13m59_wide'];bpy.context.view_layer.update()
pts={'sign_center':(0,5.42,2.475),'door_jamb_top_left':(-.5,5.47,2.32),'door_jamb_top_right':(.5,5.47,2.32),'near_right_back_top_left':(.4425,-3.72,1.28),'near_right_back_top_right':(1.4975,-3.72,1.28)}
meta['D_projected_landmarks_px']={k:[round(world_to_camera_view(s,cam,Vector(p)).x*1200,2),round((1-world_to_camera_view(s,cam,Vector(p)).y)*675,2)] for k,p in pts.items()}
# Actual source cropped video uses 1188x668 from y=26; source anchors remain approximate.
meta['D_reference_landmarks_px_1188x668']={'sign_center':[646,384],'door_jamb_top_left':[608,396],'door_jamb_top_right':[685,396],'near_right_back_top_left':[407,548],'near_right_back_top_right':[1100,548]}
meta['alignment_metric_warning']='Sparse manually read low-resolution anchors; not a full-image score; characters are absent in reconstruction.'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'01_train_material.blend'),compress=True)
def glb(path):
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.data.objects:
  if interior(o) or o.type=='CAMERA':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
glb(O/'03_train_material.glb')
for name,f in [('QA_WIDE_FORWARD_FLOOR','normal_material'),('QA_WIDE_LEVEL_AISLE','wide_material'),('MATCH_A_15m19_right_booth','A_material'),('MATCH_B_45m12_left_booth','B_material'),('MATCH_D_13m59_wide','D_material')]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/'renders'/f'{f}.png');bpy.ops.render.render(write_still=True)
# White keeps all interior geometry and glass, with neutralized illumination.
white=bpy.data.materials.new('White neutral matte model');white.use_nodes=True;b=white.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.63,.63,.63,1);b.inputs['Roughness'].default_value=.85
for o in bpy.data.objects:
 if interior(o) and not any('glazing' in m.name.lower() for m in o.data.materials if m):o.data.materials.clear();o.data.materials.append(white)
for o in bpy.data.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1)
bpy.data.collections['11_Exterior_city_approximation'].hide_render=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.12;s.view_settings.exposure=-.15;s['VERSION']='White model: exact same interior geometry, neutral illumination'
meta['white_geometry_sha256']=audit()['geometry_sha256'];meta['same_interior_geometry']=meta['geometry_sha256']==meta['white_geometry_sha256'];s.camera=bpy.data.objects['QA_WIDE_FORWARD_FLOOR']
# Remove orphan materials/images only after material blend and GLB are safely saved.
for m in list(bpy.data.materials):
 if m.users==0:bpy.data.materials.remove(m)
for im in list(bpy.data.images):
 if im.users==0:bpy.data.images.remove(im)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'02_train_white.blend'),compress=True);glb(O/'04_train_white.glb')
for name,f in [('QA_WIDE_FORWARD_FLOOR','normal_white'),('MATCH_D_13m59_wide','D_white')]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/'renders'/f'{f}.png');bpy.ops.render.render(write_still=True)
(R/'analysis/verification_initial.json').write_text(json.dumps(meta,indent=2));(O/'verification.json').write_text(json.dumps(meta,indent=2));print('TRAIN_FINAL_READY',json.dumps(meta))
