import bpy,json,hashlib,os,math,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/workspace/scratch/fa58bfcf0425/garden_hd_revision_20261010');old=R.parent/'castle_garden_fullscene/delivery/models/Garden_Complete_Textured.blend'
bpy.ops.wm.open_mainfile(filepath=str(old));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=1180;s.render.resolution_y=664;s.render.resolution_percentage=100
joint=json.load(open(R/'qa/joint_candidate_v3_conservative.json'));fits=joint['fits'];g=joint['shared_parameters'];changes=[]
for o in list(s.objects):
 if o.type!='MESH':continue
 kind=None
 if 'window' in o.name.lower() or 'leaded_glass' in o.name.lower():kind='window'
 elif 'door' in o.name.lower():kind='door'
 elif o.name.startswith('05_Far') or o.name=='Far_floral_arch_support' or (o.name.startswith('推定_花架埋入式柱脚') and abs(o.location.y+.625)<.01):kind='arch'
 elif o.name=='Visible_violet_masonry_facade_patch':kind='wall'
 if kind is None:continue
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  q=o.matrix_world@v.co
  if kind=='window' or (kind=='wall' and 2.71999<=abs(q.x)<=4.08001 and q.z>=1.14999):
   c=3.4 if q.x>0 else -3.4;q.x=c+(q.x-c)*g['window_width_factor']
  elif kind=='door' or (kind=='wall' and abs(q.x)<=1.18001 and q.z>=.24999):q.x*=g['door_width_factor']
  elif kind=='arch':
   ox=q.x;oz=q.z;q.x*=g['arch_width_factor'];q.y+=g['arch_y_translation'];q.z=.25+(q.z-.25)*g['arch_height_factor'] if q.z>.25 else q.z
   # Shared double-crest profile, supported by all three views, approximate hidden stem.
   weight=max(0,min(1,(oz-2.0)/1.0));q.z+=g['arch_shoulder_amplitude']*(math.exp(-((ox-1.1)/.55)**2)+math.exp(-((ox+1.1)/.55)**2)-2*math.exp(-(1.1/.55)**2))*weight
  v.co=inv@q
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();changes.append(dict(object=o.name,kind=kind))
json.dump(dict(parameters=g,double_crest_amplitude=g['arch_shoulder_amplitude'],changes=changes,units='working model units; not measured meters',note='One shared geometry; closed door/glass retained; no new room or roof.'),open(R/'qa/geometry_changes_v3_conservative.json','w'),ensure_ascii=False,indent=2)

for d in fits:
 bpy.ops.object.camera_add(location=d['parameters'][:3]);o=bpy.context.object;o.name=d['tag'];cv=d['camera_basis_cv'];o.rotation_euler=Matrix([cv[0],[-v for v in cv[1]],[-v for v in cv[2]]]).transposed().to_euler();o.data.lens=d['lens_mm'];o.data.sensor_width=36;o.data.sensor_fit='HORIZONTAL';o.data.shift_y=d['shift_y'];o.data.clip_end=200
bpy.ops.object.camera_add(location=(0,-11,2.6));o=bpy.context.object;o.name='MAIN_Level_Normal';o.rotation_euler=(Vector((0,-1,2.6))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=25;o.data.sensor_width=36;o.data.sensor_fit='HORIZONTAL';s.camera=o
frozen=R/'models/Garden_HD_Conservative_v3_Frozen.blend';bpy.ops.wm.save_as_mainfile(filepath=str(frozen),compress=True)
sha=hashlib.sha256(frozen.read_bytes()).hexdigest()
