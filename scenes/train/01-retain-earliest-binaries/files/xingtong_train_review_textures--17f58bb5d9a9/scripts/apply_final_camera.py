import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'deliverables';fit=json.loads((R/'analysis/final_D_camera_fit.json').read_text());audit={};proj={}
for stem,outglb,render in [('01_train_material','03_train_material','final_D_material'),('02_train_white','04_train_white','final_D_white')]:
 bpy.ops.wm.open_mainfile(filepath=str(O/(stem+'.blend')));s=bpy.context.scene;o=bpy.data.objects['MATCH_D_13m59_wide'];yaw=math.radians(fit['yaw_degrees']);pitch=math.radians(fit['pitch_degrees']);fw=Vector((math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),math.sin(pitch)));o.location=(fit['x'],-5,fit['z']);o.rotation_euler=fw.to_track_quat('-Z','Y').to_euler()
 # Keep the first unobserved ceiling assembly physically inside the completed shell.
 for a in bpy.data.objects:
  if a.name.startswith(('Central round ceiling','Central rectangular ceiling','Vent grille','Vent louvre','Central ceiling side fluorescent','Ceiling diffuse pool','Indirect ceiling upward')) and a.location.y<-4.8:a.location.y+=.9
 bpy.context.view_layer.update();h=hashlib.sha256();meshes=[a for a in bpy.data.objects if a.type=='MESH' and not any(c.name.startswith('11_') for c in a.users_collection)]
 for a in sorted(meshes,key=lambda a:a.name):
  h.update(a.name.encode());h.update(str(tuple(tuple(round(float(v),8) for v in row) for row in a.matrix_world)).encode())
  for v in a.data.vertices:h.update(str(tuple(round(float(t),8) for t in v.co)).encode())
  for p in a.data.polygons:h.update(str(tuple(p.vertices)).encode())
 audit[stem]=h.hexdigest()
 pts={'sign_center':(0,5.42,2.475),'door_top_left':(-.5,5.47,2.32),'door_top_right':(.5,5.47,2.32),'near_right_back_top_left':(.4425,-3.72,1.28),'near_right_back_top_right':(1.4975,-3.72,1.28)}
 proj={k:[world_to_camera_view(s,o,Vector(p)).x*1188,(1-world_to_camera_view(s,o,Vector(p)).y)*668] for k,p in pts.items()}
 s.camera=bpy.data.objects['QA_WIDE_FORWARD_FLOOR'];s['D_camera_fit']='Fixed 24mm lens; only camera position and orientation fit to five manually read structural landmarks; not whole-image equivalence.';bpy.ops.wm.save_as_mainfile(filepath=str(O/(stem+'.blend')),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for a in bpy.data.objects:
  if a in meshes or a.type=='CAMERA':a.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(O/(outglb+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_cameras=True,export_extras=True,export_materials='EXPORT')
 s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=675;s.render.resolution_percentage=100;s.camera=o;s.render.filepath=str(R/'renders'/(render+'.png'));bpy.ops.render.render(write_still=True)
meta=json.loads((O/'verification.json').read_text());meta['geometry_sha256']=audit['01_train_material'];meta['white_geometry_sha256']=audit['02_train_white'];meta['same_interior_geometry']=len(set(audit.values()))==1;meta['world_bounds'][0][1]=-5.65
ref=meta['D_alignment']['reference_approximate_landmarks'];errs={k:math.hypot(proj[k][0]-ref[k][0],proj[k][1]-ref[k][1]) for k in ref};meta['D_alignment']['model_projected_landmarks']=proj;meta['D_alignment']['residual_pixels']=errs;meta['D_alignment']['mean_residual_pixels']=sum(errs.values())/len(errs);meta['D_alignment']['camera_fit']=fit;meta.pop('glb_validation',None);(O/'verification.json').write_text(json.dumps(meta,indent=2));print('FINAL_CAMERA_SAVED',flush=True)
