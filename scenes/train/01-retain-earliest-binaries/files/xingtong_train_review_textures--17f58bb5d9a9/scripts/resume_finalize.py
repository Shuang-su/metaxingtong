import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'deliverables';bpy.ops.wm.open_mainfile(filepath=str(O/'01_train_material.blend'));s=bpy.context.scene
readme=(R/'README_中文.txt').read_text().replace('18张1024×1024','18张512×512');(R/'README_中文.txt').write_text(readme);(O/'README_中文.txt').write_text(readme)
def inside(o):return o.type=='MESH' and not any(c.name.startswith('11_') for c in o.users_collection)
def audit():
 bpy.context.view_layer.update();h=hashlib.sha256();ob=[o for o in bpy.data.objects if inside(o)];lo=[1e9]*3;hi=[-1e9]*3
 for o in sorted(ob,key=lambda a:a.name):
  h.update(o.name.encode());h.update(str(tuple(tuple(round(float(v),8) for v in row) for row in o.matrix_world)).encode())
  for v in o.data.vertices:
   h.update(str(tuple(round(float(a),8) for a in v.co)).encode());p=o.matrix_world@v.co
   for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
  for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return {'geometry_sha256':h.hexdigest(),'interior_mesh_objects':len(ob),'base_vertices':sum(len(o.data.vertices) for o in ob),'base_polygons':sum(len(o.data.polygons) for o in ob),'UV_mesh_objects':sum(bool(o.data.uv_layers) for o in ob),'world_bounds':[lo,hi]}
meta=audit();meta['PBR_image_maps']=18;meta['PBR_image_size']=[512,512];meta['sign_image_maps']=1;meta['packed_image_count']=sum(bool(i.packed_file) for i in bpy.data.images);meta['reference_video']='https://www.bilibili.com/video/BV1fMP4ziEUd/';meta['sixth_module']='Inferred; at least five identifiable in source.'
cam=bpy.data.objects['MATCH_D_13m59_wide'];pts={'sign_center':(0,5.42,2.475),'door_top_left':(-.5,5.47,2.32),'door_top_right':(.5,5.47,2.32),'near_right_back_top_left':(.4425,-3.72,1.28),'near_right_back_top_right':(1.4975,-3.72,1.28)};ref={'sign_center':[646,384],'door_top_left':[608,396],'door_top_right':[685,396],'near_right_back_top_left':[407,548],'near_right_back_top_right':[1100,548]}
proj={k:[world_to_camera_view(s,cam,Vector(p)).x*1188,(1-world_to_camera_view(s,cam,Vector(p)).y)*668] for k,p in pts.items()};errs={k:round(math.hypot(proj[k][0]-ref[k][0],proj[k][1]-ref[k][1]),2) for k in ref};meta['D_alignment']={'image_size':[1188,668],'reference_approximate_landmarks':ref,'model_projected_landmarks':proj,'residual_pixels':errs,'mean_residual_pixels':sum(errs.values())/len(errs),'warning':'Sparse manually read landmarks. Not a full-image score. No post-render warp.'}
# Save the white variant before any longer renders.
white=bpy.data.materials.new('White neutral matte model');white.use_nodes=True;b=white.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.63,.63,.63,1);b.inputs['Roughness'].default_value=.85
for o in bpy.data.objects:
 if inside(o) and not any('glazing' in m.name.lower() for m in o.data.materials if m):o.data.materials.clear();o.data.materials.append(white)
for o in bpy.data.objects:
 if o.type=='LIGHT':o.data.color=(1,1,1)
bpy.data.collections['11_Exterior_city_approximation'].hide_render=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.12;s.view_settings.exposure=-.15;s.camera=bpy.data.objects['QA_WIDE_FORWARD_FLOOR'];s['VERSION']='White model: exact same interior geometry, neutral illumination'
for t in bpy.data.texts:
 if t.name.startswith('README'):t.clear();t.write(readme)
meta['white_geometry_sha256']=audit()['geometry_sha256'];meta['same_interior_geometry']=meta['geometry_sha256']==meta['white_geometry_sha256']
for m in list(bpy.data.materials):
 if m.users==0:bpy.data.materials.remove(m)
for im in list(bpy.data.images):
 if im.users==0:bpy.data.images.remove(im)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'02_train_white.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if inside(o) or o.type=='CAMERA':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'04_train_white.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
(O/'verification.json').write_text(json.dumps(meta,indent=2));print('WHITE_FILES_SAVED',flush=True)
s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=675;s.render.resolution_percentage=100
for cn,fn in [('QA_WIDE_FORWARD_FLOOR','normal_white'),('MATCH_D_13m59_wide','D_white')]:
 s.camera=bpy.data.objects[cn];s.render.filepath=str(R/'renders'/f'{fn}.png');bpy.ops.render.render(write_still=True);print('RENDER_SAVED',fn,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'01_train_material.blend'));s=bpy.context.scene;s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=675;s.render.resolution_percentage=100
for cn,fn in [('QA_WIDE_FORWARD_FLOOR','packed_normal_material'),('MATCH_A_15m19_right_booth','packed_A_material'),('MATCH_D_13m59_wide','packed_D_material')]:
 s.camera=bpy.data.objects[cn];s.render.filepath=str(R/'renders'/f'{fn}.png');bpy.ops.render.render(write_still=True);print('RENDER_SAVED',fn,flush=True)
print('RESUME_FINAL_DONE',flush=True)
